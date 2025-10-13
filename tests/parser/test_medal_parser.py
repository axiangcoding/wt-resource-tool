from wt_resource_tool.parser.player_medal_parser import parse_player_medal


def test_parse_player_medal(repo_path: str):
    medals = parse_player_medal(repo_path)
    assert medals is not None
    assert len(medals.medals) >= 261
