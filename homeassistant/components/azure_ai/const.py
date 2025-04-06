"""Constants for the Azure AI integration."""

import logging

DOMAIN = "azure_ai"
CONF_API_KEY = "api_key"
CONF_SYSTEM_PROMPT = "system_prompt"
CONF_MODEL_DEPLOYMENT = "model_deployment"
CONF_BASE_URL = "base_url"
CONF_TEMPERATURE = "temperature"
CONF_TOP_P = "top_p"
CONF_REASONING_EFFORT = "reasoning_effort"
CONF_ENABLE_CONTROL = "enable_control"

DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9
DEFAULT_REASONING_EFFORT = "medium"

LOGGER: logging.Logger = logging.getLogger(__package__)
