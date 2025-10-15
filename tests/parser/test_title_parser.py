from wt_resource_tool.parser.player_title_parser import parse_player_title


def test_parse_player_title(repo_path: str):
    titles = parse_player_title(repo_path)
    assert titles is not None
    assert len(titles.titles) >= 602
