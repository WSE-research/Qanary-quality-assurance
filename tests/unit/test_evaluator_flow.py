"""Tests for the evaluation flow and the Excel export, with all network and
triplestore access faked."""
import os


def _fake_connection(boolean_result=True):
    class FakeConn:
        def setQuery(self, q):
            self.q = q

        def setReturnFormat(self, fmt):
            self.fmt = fmt

        def query(self):
            class R:
                def convert(self_inner):
                    return {"boolean": boolean_result}
            return R()

    return FakeConn()


def test_request_qanary_endpoint(evaluator, monkeypatch):
    class FakeResp:
        status_code = 200
        request = object()

        def json(self):
            return {"outGraph": "urn:g", "endpoint": "http://ts/sparql"}

    monkeypatch.setattr(evaluator.requests, "post", lambda url, data: FakeResp())
    monkeypatch.setattr(evaluator.curlify, "to_curl", lambda req: "curl ...")
    out = evaluator.request_qanary_endpoint_for_question(
        evaluator.logging.getLogger("t"),
        {"system_url": "http://q/ask", "componentlist": ["C1"]},
        "What is the real name of Batman?",
    )
    assert out["outGraph"] == "urn:g"


def test_evaluate_tests_end_to_end_with_mocks(evaluator, monkeypatch, tmp_path):
    # two ASK templates in a temp configuration directory
    for name in ["a.sparql", "b.sparql"]:
        (tmp_path / name).write_text("ASK FROM <GRAPHID> WHERE { ?s ?p ?o }")

    monkeypatch.setattr(
        evaluator, "request_qanary_endpoint_for_question",
        lambda logger, conf, question: {"outGraph": "urn:g", "endpoint": "http://ts/sparql"},
    )
    monkeypatch.setattr(evaluator, "connect_to_triplestore", lambda conf, ep: _fake_connection(True))

    tests = [{"question": "Q1", "replacements": {}}]
    results = evaluator.evaluate_tests(
        evaluator.logging.getLogger("t"),
        {"system_url": "http://q", "componentlist": []},
        str(tmp_path),
        ["a.sparql", "b.sparql"],
        evaluator.dummy,
        tests,
    )
    assert len(results) == 1
    assert results[0]["question"] == "Q1"
    assert results[0]["graph"] == "urn:g"
    # each ASK template result plus the custom evaluation are recorded
    keys = [list(r.keys())[0] for r in results[0]["results"]]
    assert "a.sparql" in keys and "b.sparql" in keys and "custom_evaluation" in keys


SAMPLE_RESULTS = [
    {"question": "Q1", "graph": "g1", "results": [{"a.sparql": 1}, {"b.sparql": 0}, {"custom_evaluation": 1}]},
    {"question": "Q2", "graph": "g2", "results": [{"a.sparql": 0}, {"b.sparql": 1}, {"custom_evaluation": 0}]},
]


def test_export_to_excel_creates_file(evaluator, tmp_path):
    prefix = str(tmp_path / "report")
    evaluator.export_to_excel(
        evaluator.logging.getLogger("t"), SAMPLE_RESULTS, prefix, "Sheet1"
    )
    assert os.path.exists(prefix + ".xlsx")
    assert os.path.getsize(prefix + ".xlsx") > 0
