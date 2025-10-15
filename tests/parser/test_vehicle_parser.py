from wt_resource_tool.parser.vehicle_data_parser import parse_vehicle_data


def test_parse_vehicle_data(repo_path: str):
    vehicles = parse_vehicle_data(repo_path)
    assert vehicles is not None
    assert len(vehicles.vehicles) >= 3098
    assert vehicles.max_economic_rank == 40
