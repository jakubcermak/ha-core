"""Config flow for Azure AI integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.helpers import llm, selector

from .const import (
    CONF_API_KEY,
    CONF_BASE_URL,
    CONF_ENABLE_CONTROL,
    CONF_MODEL_DEPLOYMENT,
    CONF_REASONING_EFFORT,
    CONF_SYSTEM_PROMPT,
    CONF_TEMPERATURE,
    CONF_TOP_P,
    DEFAULT_REASONING_EFFORT,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    DOMAIN,
)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_API_KEY): str,
        vol.Required(CONF_MODEL_DEPLOYMENT): str,
        vol.Required(CONF_BASE_URL): str,
    }
)

OPTIONS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ENABLE_CONTROL): bool,
        vol.Optional(CONF_SYSTEM_PROMPT, default=llm.DEFAULT_INSTRUCTIONS_PROMPT): str,
        vol.Optional(
            CONF_TEMPERATURE, default=DEFAULT_TEMPERATURE
        ): selector.NumberSelector(
            selector.NumberSelectorConfig(min=0.0, max=1.0, step=0.1)
        ),
        vol.Optional(CONF_TOP_P, default=DEFAULT_TOP_P): selector.NumberSelector(
            selector.NumberSelectorConfig(min=0.0, max=1.0, step=0.1)
        ),
        vol.Optional(
            CONF_REASONING_EFFORT, default=DEFAULT_REASONING_EFFORT
        ): selector.SelectSelector(
            selector.SelectSelectorConfig(
                options=["low", "medium", "high"],
                mode=selector.SelectSelectorMode.DROPDOWN,
            )
        ),
    }
)

DEFAULT_OPTIONS = {
    CONF_SYSTEM_PROMPT: llm.DEFAULT_INSTRUCTIONS_PROMPT,
    CONF_TEMPERATURE: DEFAULT_TEMPERATURE,
    CONF_TOP_P: DEFAULT_TOP_P,
    CONF_REASONING_EFFORT: DEFAULT_REASONING_EFFORT,
    CONF_ENABLE_CONTROL: False,
}


class AzureAIConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Azure AI."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=CONFIG_SCHEMA)

        # Configuration is ok, save it
        return self.async_create_entry(
            title="AzureAI",
            data=user_input,
            options=DEFAULT_OPTIONS,
        )

    @staticmethod
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlow:
        """Create the options flow."""
        return AzureAIOptionsFlow(config_entry)


class AzureAIOptionsFlow(OptionsFlow):
    """Handle Azure AI options."""

    async def async_step_init(self, user_input: dict | None = None) -> ConfigFlowResult:
        """Handle the options step."""
        if user_input is None:
            return self.async_show_form(step_id="init", data_schema=OPTIONS_SCHEMA)

        return self.async_create_entry(title="", data=user_input)
