from blazemeter_explorer_mcp.catalog import operation_by_id, operations


def test_public_spec_has_expected_operation_count() -> None:
    assert len(operations()) == 54


def test_known_mutating_operation_is_discoverable() -> None:
    method, path, operation = operation_by_id("userRemoveUiMessage")
    assert method == "DELETE"
    assert path == "/user/ui-messages/{messageId}"
    assert operation["operationId"] == "userRemoveUiMessage"
