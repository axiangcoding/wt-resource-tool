from wt_resource_tool.parser.tools import clean_text


def test_clean_text():
    assert clean_text("Hello World") == "Hello World"
    assert clean_text("Hello\u200bWorld") == "HelloWorld"
    assert clean_text("Hello\nWorld") == "HelloWorld"
    assert clean_text("  Hello World  ") == "  Hello World  "
    assert clean_text("Hello\tWorld") == "HelloWorld"
    assert clean_text("Hello\\tWorld") == "HelloWorld"
