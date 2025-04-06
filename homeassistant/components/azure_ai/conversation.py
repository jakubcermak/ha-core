"""Conversation support for Azure AI."""

from __future__ import annotations

from homeassistant.components import conversation
from homeassistant.components.azure_ai import AzureAIConfigEntry
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.chat_completion_client_base import (
    ChatCompletionClientBase,
)
from semantic_kernel.contents.chat_history import ChatHistory
from .const import (
    CONF_ENABLE_CONTROL,
    DOMAIN,
    CONF_API_KEY,
    CONF_SYSTEM_PROMPT,
    CONF_MODEL_DEPLOYMENT,
    CONF_BASE_URL,
    CONF_TEMPERATURE,
    CONF_TOP_P,
    CONF_REASONING_EFFORT,
    LOGGER,
)
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)
from semantic_kernel.connectors.ai.function_choice_behavior import (
    FunctionChoiceBehavior,
)


class AzureAIConversationEntity(
    conversation.ConversationEntity, conversation.AbstractConversationAgent
):
    """Azure AI conversation agent."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, entry: AzureAIConfigEntry) -> None:
        """Initialize the agent."""
        self.config_entry = entry
        self._attr_unique_id = entry.entry_id
        self._attr_device_info = dr.DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Microsoft Azure",
            model="Azure OpenAI",
            entry_type=dr.DeviceEntryType.SERVICE,
        )
        if self.config_entry.data.get(CONF_ENABLE_CONTROL):
            self._attr_supported_features = (
                conversation.ConversationEntityFeature.CONTROL
            )

        # Enable planning
        self.execution_settings = AzureChatPromptExecutionSettings()
        self.execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    async def async_added_to_hass(self) -> None:
        """When entity is added to Home Assistant."""
        await super().async_added_to_hass()
        conversation.async_set_agent(self.hass, self.entry, self)

    async def async_will_remove_from_hass(self) -> None:
        """When entity will be removed from Home Assistant."""
        conversation.async_unset_agent(self.hass, self.entry)
        await super().async_will_remove_from_hass()

    async def _async_handle_message(
        self,
        user_input: conversation.ConversationInput,
        chat_log: conversation.ChatLog,
    ) -> conversation.ConversationResult:
        """Call the Azure AI API."""
        client = self.config_entry.runtime_data
        options = self.entry.options

        history = ChatHistory()
        history.add_system_message(options[CONF_SYSTEM_PROMPT])
        LOGGER.debug("system prompt: %s", options[CONF_SYSTEM_PROMPT])
        for message in chat_log.content:
            if message.role == "user":
                LOGGER.debug("user message: %s", message.text)
                history.add_user_message(message.text)
            elif message.role == "assistant":
                LOGGER.debug("assistant message: %s", message.text)
                history.add_assistant_message(message.text)
            else:
                LOGGER.debug("unknown message: %s %s", message.role, message.text)

        try:
            chat_completion: AzureChatCompletion = client.get_service(
                None, AzureChatCompletion
            )
            response = await chat_completion.get_chat_message_content(
                history, self.execution_settings, kernel=client
            )
            LOGGER.debug("Azure AI response: %s", response)
        except Exception as err:
            raise conversation.ConverseError(
                f"Error communicating with Azure AI: {err}"
            )

        intent_response = conversation.IntentResponse(language=user_input.language)
        intent_response.async_set_speech(response)
        return conversation.ConversationResult(
            response=intent_response,
            conversation_id=chat_log.conversation_id,
            continue_conversation=False,
        )
