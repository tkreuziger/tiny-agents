from llmini.tools.docstring import parse_google_docstring


def test_empty_docstring():
    assert parse_google_docstring("") == {"description": "", "params": {}}


def test_none_docstring():
    assert parse_google_docstring(None) == {"description": "", "params": {}}


def test_description_only():
    result = parse_google_docstring("Add two numbers.")
    assert result["description"] == "Add two numbers."
    assert result["params"] == {}


def test_description_with_params():
    doc = "Add two numbers.\n\nArgs:\n    a: First number.\n    b: Second number.\n"
    result = parse_google_docstring(doc)
    assert result["description"] == "Add two numbers."
    assert result["params"] == {"a": "First number.", "b": "Second number."}


def test_multiline_param_description():
    doc = (
        "Do something.\n"
        "\n"
        "Args:\n"
        "    x: A very long description\n"
        "    that spans multiple lines.\n"
    )
    result = parse_google_docstring(doc)
    assert "very long description" in result["params"]["x"]
    assert "multiple lines" in result["params"]["x"]


def test_params_without_args_section():
    doc = """Just a description."""
    result = parse_google_docstring(doc)
    assert result["description"] == "Just a description."
    assert result["params"] == {}
