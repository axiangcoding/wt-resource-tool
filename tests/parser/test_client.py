import pytest

from wt_resource_tool._client import WTResourceToolMemory


@pytest.mark.asyncio
async def test_parse_and_load_data(repo_path: str):
    tool = WTResourceToolMemory()
    await tool.parse_and_load_data(data_types=["player_title", "player_medal", "vehicle"], local_repo_path=repo_path)
    title = await tool.get_player_title("title_cannon_fodder")
    assert title is not None
    assert title.name_i18n.chinese == "炮灰"
