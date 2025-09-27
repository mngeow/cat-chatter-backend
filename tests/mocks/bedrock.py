from unittest.mock import AsyncMock, patch

import pytest

from app.utils.bedrock import BedrockUtils, GuardrailEvaluationResult


@pytest.fixture
def mock_bedrock_client():
    with patch("aioboto3.Session") as mock_session:
        mock_client = AsyncMock()
        mock_session.return_value.client.return_value.__aenter__.return_value = (
            mock_client
        )
        yield mock_client


@pytest.mark.asyncio
async def test_guardrail_evaluation(mock_bedrock_client):
    # Arrange
    mock_bedrock_client.apply_guardrail.return_value = {
        "action": "GUARDRAIL_INTERVENED",
        "assessments": "Some reason",
        "outputs": [{"text": "Template message"}],
    }

    bedrock_utils = BedrockUtils("us-west-2", "guardrail-id", "1.0")

    # Act
    result = await bedrock_utils.guardrail_evaluation("Test question")

    # Assert
    assert isinstance(result, GuardrailEvaluationResult)
    assert result.is_blocked_by_guardrail
    assert result.template_message == "Template message"

    mock_bedrock_client.apply_guardrail.assert_called_once_with(
        guardrailIdentifier="guardrail-id",
        guardrailVersion="1.0",
        source="OUTPUT",
        content=[{"text": {"text": "Test question"}}],
    )
