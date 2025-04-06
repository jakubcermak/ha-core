"""Conversation support for Azure AI."""

from __future__ import annotations

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.function_choice_behavior import (
    FunctionChoiceBehavior,
)
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.azure_chat_prompt_execution_settings import (
    AzureChatPromptExecutionSettings,
)

from homeassistant.components import conversation
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers import device_registry as dr

from .const import (
    CONF_API_KEY,
    CONF_BASE_URL,
    CONF_MODEL_DEPLOYMENT,
    CONF_REASONING_EFFORT,
    CONF_SYSTEM_PROMPT,
    CONF_TEMPERATURE,
    CONF_TOP_P,
    DOMAIN,
)


class AzureAIConversationEntity(
    conversation.ConversationEntity, conversation.AbstractConversationAgent
):
    """Azure AI conversation agent."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize the agent."""

        # Enable planning
        self.execution_settings = AzureChatPromptExecutionSettings()
        self.execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

        self.entry = entry
        self.kernel = Kernel()
        self.chat_completion = AzureChatCompletion(
            api_key=entry.data[CONF_API_KEY],
            endpoint=entry.data[CONF_BASE_URL],
            deployment_name=entry.data[CONF_MODEL_DEPLOYMENT],
            temperature=entry.data.get(CONF_TEMPERATURE),
            top_p=entry.data.get(CONF_TOP_P),
            reasoning_effort=entry.data.get(CONF_REASONING_EFFORT),
        )
        self.kernel.register_plugin("azure_ai", self)
        self.system_prompt = entry.data.get(CONF_SYSTEM_PROMPT, "")

        self._attr_unique_id = entry.entry_id
        self._attr_device_info = dr.DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Azure",
            model="Azure OpenAI",
            entry_type=dr.DeviceEntryType.SERVICE,
        )

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
        history = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_input.text},
        ]

        try:
            response = await self.chat_completion.get_chat_message_content(history)
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
