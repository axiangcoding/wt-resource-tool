from wt_resource_tool.parser.tools import camel_to_snake, clean_text


def test_clean_text():
    assert clean_text("Hello World") == "Hello World"
    assert clean_text("Hello\u200bWorld") == "HelloWorld"
    assert clean_text("Hello\nWorld") == "HelloWorld"
    assert clean_text("  Hello World  ") == "  Hello World  "
    assert clean_text("Hello\tWorld") == "HelloWorld"
    assert clean_text("Hello\\tWorld") == "HelloWorld"


def test_camel_to_snake():
    assert camel_to_snake("needBuyToOpenNextInTier2") == "need_buy_to_open_next_in_tier2"
    assert camel_to_snake("speed") == "speed"
    assert camel_to_snake("maxAmmo") == "max_ammo"
    assert camel_to_snake("reloadTimeMGun") == "reload_time_m_gun"
