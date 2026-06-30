"""Unit tests for the pure helper logic in evaluate-qanary-system.py."""
import json

import pytest


def test_prepare_sparql_query_replaces_placeholders(evaluator, tmp_path):
    template = tmp_path / "t.sparql"
    template.write_text("ASK FROM <GRAPHID> WHERE { ?s ?p DBPEDIAENTITY }")
    out = evaluator.prepare_sparql_query(
        evaluator.logging.getLogger("t"),
        str(template),
        {"DBPEDIAENTITY": "http://dbpedia.org/resource/Batman"},
        "urn:graph:1",
    )
    assert "<urn:graph:1>" in out
    assert "http://dbpedia.org/resource/Batman" in out
    assert "DBPEDIAENTITY" not in out


def test_prepare_sparql_query_requires_graphid_placeholder(evaluator, tmp_path):
    template = tmp_path / "t.sparql"
    template.write_text("ASK WHERE { ?s ?p ?o }")  # no <GRAPHID>
    with pytest.raises(RuntimeError, match="GRAPHID"):
        evaluator.prepare_sparql_query(evaluator.logging.getLogger("t"), str(template), {}, "g")


def test_prepare_sparql_query_requires_ask(evaluator, tmp_path):
    template = tmp_path / "t.sparql"
    template.write_text("SELECT * FROM <GRAPHID> WHERE { ?s ?p ?o }")  # not an ASK
    with pytest.raises(RuntimeError, match="ASK"):
        evaluator.prepare_sparql_query(evaluator.logging.getLogger("t"), str(template), {}, "g")


def test_measure_duration_is_non_negative(evaluator):
    import datetime
    start = datetime.datetime.now()
    assert evaluator.measure_duration_in_milliseconds(start) >= 0


SAMPLE_RESULTS = [
    {"question": "Q1", "graph": "g1", "results": [{"a.sparql": 1}, {"b.sparql": 0}, {"custom_evaluation": 1}]},
    {"question": "Q2", "graph": "g2", "results": [{"a.sparql": 0}, {"b.sparql": 1}, {"custom_evaluation": 0}]},
]


def test_get_headers_from_test_results(evaluator):
    headers = evaluator.get_headers_from_test_results(SAMPLE_RESULTS)
    assert headers == ["a.sparql", "b.sparql", "custom_evaluation"]


def test_create_data_frame_has_average_column(evaluator):
    df = evaluator.create_data_frame(SAMPLE_RESULTS)
    # one column per question plus the computed average
    assert "Q1" in df.columns and "Q2" in df.columns
    assert "average" in df.columns
    # average of a.sparql (1, 0) is 0.5
    assert df["average"][0] == pytest.approx(0.5)


def test_export_to_json_writes_file(evaluator, tmp_path):
    prefix = str(tmp_path / "out")
    evaluator.export_to_json(evaluator.logging.getLogger("t"), SAMPLE_RESULTS, prefix)
    with open(prefix + ".json") as f:
        assert json.load(f) == SAMPLE_RESULTS


def test_dummy_validate_returns_true(evaluator):
    assert evaluator.dummy.validate(None, None, None, None, None) is True


def test_custom_module_callable_check_passes_for_dummy(evaluator):
    # the bundled dummy.validate has the required 5 parameters
    evaluator.determine_if_custom_module_is_callable(
        evaluator.logging.getLogger("t"), evaluator.dummy
    )


def test_custom_module_callable_check_rejects_missing_validate(evaluator):
    class NoValidate:
        __name__ = "no_validate"

    with pytest.raises(RuntimeError):
        evaluator.determine_if_custom_module_is_callable(
            evaluator.logging.getLogger("t"), NoValidate
        )


def test_custom_module_callable_check_rejects_wrong_arity(evaluator):
    class WrongArity:
        __name__ = "wrong_arity"

        @staticmethod
        def validate(a, b):  # only 2 params, needs 5
            return True

    with pytest.raises(RuntimeError, match="5 parameters"):
        evaluator.determine_if_custom_module_is_callable(
            evaluator.logging.getLogger("t"), WrongArity
        )


def test_connect_to_triplestore_returns_wrapper(evaluator):
    conn = evaluator.connect_to_triplestore({}, "http://localhost:8890/sparql")
    assert conn is not None
