import pytest
from unittest.mock import MagicMock, create_autospec

from src.application.handlers.action_command_handlers import (
    SubmitActionCommandHandler, ValidateProofCommandHandler
)
from src.application.handlers.activity_command_handlers import (
    CreateActivityCommandHandler, DeactivateActivityCommandHandler
)

# Action command handler tests
def test_submit_action_command_handler_calls_service():
    mock_service = MagicMock()
    handler = SubmitActionCommandHandler(mock_service)
    command = MagicMock()
    context = MagicMock()
    mock_service.submit_action.return_value = "action-id"

    result = handler.handle(command, context)

    command.validate.assert_called_once()
    mock_service.submit_action.assert_called_once_with(command, context)
    assert result == "action-id"

def test_validate_proof_command_handler_calls_service():
    mock_service = MagicMock()
    handler = ValidateProofCommandHandler(mock_service)
    command = MagicMock()
    context = MagicMock()

    handler.handle(command, context)

    command.validate.assert_called_once()
    mock_service.simulate_proof_validation.assert_called_once_with(command, context)

# Activity command handler tests
def test_create_activity_command_handler_calls_service():
    mock_service = MagicMock()
    handler = CreateActivityCommandHandler(mock_service)
    command = MagicMock()
    context = MagicMock()
    mock_service.create_activity.return_value = "activity-id"

    result = handler.handle(command, context)

    command.validate.assert_called_once()
    mock_service.create_activity.assert_called_once_with(command, context)
    assert result == "activity-id"

def test_deactivate_activity_command_handler_calls_service():
    mock_service = MagicMock()
    handler = DeactivateActivityCommandHandler(mock_service)
    command = MagicMock()
    context = MagicMock()

    handler.handle(command, context)

    command.validate.assert_called_once()
    mock_service.deactivate_activity.assert_called_once_with(command, context)
