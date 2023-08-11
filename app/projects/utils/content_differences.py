from typing import Dict, Tuple, List

def parse_differences_stack(differences_stack: Dict) -> Dict:
    parsed_data = {}
    for client_version, differences in differences_stack.items():
        new_differences = []
        for difference in differences:
            new_differences.append((difference["0"], difference["1"]))
        parsed_data[client_version] = new_differences
    return parsed_data


def serialize_differences_stack(differences_stack: Dict) -> Dict:
    serialized_data = {}
    for server_version, differences in differences_stack.items():
        new_differences = []
        for difference in differences:
            new_differences.append({"0": difference[0], "1": difference[1]})
        serialized_data[server_version] = new_differences
    return serialized_data


def differences_contain_changes(differences: List[Tuple[int, str]]) -> bool:
    return any(difference[0] in [-1, 1] for difference in differences)
