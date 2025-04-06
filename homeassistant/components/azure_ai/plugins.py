"""Plugins for Azure AI integration."""

from __future__ import annotations

from homeassistant.core import HomeAssistant


class HomeAssistantIntegrationPlugin:
    """Plugin for Azure AI integration."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the plugin."""
        self.hass = hass

    async def get_switch_entities(self) -> list[dict[str, str]]:
        """Retrieve switch entities with their IDs and names."""
        entity_registry = self.hass.helpers.entity_registry.async_get(self.hass)
        return [
            {"id": entity_id, "name": entry.name or entity_id}
            for entity_id, entry in entity_registry.entities.items()
            if entry.domain == "switch"
        ]

    async def get_sensor_entities(self) -> list[dict[str, str]]:
        """Retrieve sensor entities with their IDs and names."""
        entity_registry = self.hass.helpers.entity_registry.async_get(self.hass)
        return [
            {"id": entity_id, "name": entry.name or entity_id}
            for entity_id, entry in entity_registry.entities.items()
            if entry.domain == "sensor"
        ]

    async def get_entity_state(self, entity_id: str) -> str:
        """Retrieve the state of an entity given its ID."""
        state = self.hass.states.get(entity_id)
        return state.state if state else "Entity not found"
