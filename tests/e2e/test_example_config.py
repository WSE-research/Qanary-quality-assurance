"""End-to-end smoke over the bundled `superhero-real-names` example: the test
definition parses, references real SPARQL templates, and every template can be
materialised by prepare_sparql_query (ASK + <GRAPHID> placeholder present)."""
import json
import os

import pytest

pytestmark = pytest.mark.e2e

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EXAMPLE_DIR = os.path.join(REPO_ROOT, "superhero-real-names")


def test_example_definition_and_templates(evaluator):
    with open(os.path.join(EXAMPLE_DIR, "qanary-test-definition.json")) as f:
        definition = json.load(f)

    templates = definition["validation-sparql-templates"]
    assert templates, "the example should define validation templates"

    logger = evaluator.logging.getLogger("e2e")
    sample_test = definition["tests"][0]
    for template in templates:
        # each referenced template file exists and is a valid ASK query
        rendered = evaluator.prepare_sparql_query(
            logger,
            os.path.join(EXAMPLE_DIR, template),
            sample_test.get("replacements", {}),
            "urn:graph:e2e",
        )
        assert "ASK" in rendered.upper()
        assert "<urn:graph:e2e>" in rendered
