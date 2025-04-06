"""The Azure AI integration."""

from __future__ import annotations

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_API_KEY, CONF_BASE_URL, CONF_MODEL_DEPLOYMENT
from .plugins import HomeAssistantIntegrationPlugin

PLATFORMS = [Platform.CONVERSATION]

type AzureAIConfigEntry = ConfigEntry[Kernel]


def init_semantic_kernel(
    hass: HomeAssistant,
    entry: AzureAIConfigEntry,
) -> Kernel:
    """Initialize the semantic kernel."""
    kernel = Kernel()
    chat_completion = AzureChatCompletion(
        deployment_name=entry.data[CONF_MODEL_DEPLOYMENT],
        api_key=entry.data[CONF_API_KEY],
        base_url=entry.data[CONF_BASE_URL],
    )
    kernel.add_plugin(
        HomeAssistantIntegrationPlugin(hass),
        plugin_name="HomeAssistant",
    )
    kernel.add_service(chat_completion)

    return kernel


async def async_setup_entry(hass: HomeAssistant, entry: AzureAIConfigEntry) -> bool:
    """Set up Azure AI from a config entry."""
    entry.runtime_data = init_semantic_kernel(hass, entry)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Azure AI config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
