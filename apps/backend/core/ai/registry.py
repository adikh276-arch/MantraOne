from typing import Dict, Any, Type
import yaml
from pathlib import Path

from core.providers.ai_provider import AIProvider
from core.providers.sarvam_provider import SarvamProvider


class AIRegistry:
    """
    Centralized registry mapping capabilities to providers based on configuration.
    Services request capabilities here instead of instantiating providers directly.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIRegistry, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self._providers: Dict[str, AIProvider] = {}
        self._config: Dict[str, Any] = {}
        self._load_config()
        self._register_default_providers()

    def _load_config(self):
        config_path = Path(__file__).parent.parent.parent / "config" / "capabilities.yaml"
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f) or {}

    def _register_default_providers(self):
        # Instantiate available providers. Sarvam is the default.
        self._providers["sarvam"] = SarvamProvider()

    def get(self, capability: str) -> AIProvider:
        """
        Returns the appropriate provider for the requested capability based on config.
        """
        cap_config = self._config.get(capability, {})
        provider_name = cap_config.get("provider", "sarvam")

        provider = self._providers.get(provider_name)
        if not provider:
            raise ValueError(f"Unknown provider '{provider_name}' configured for capability '{capability}'.")

        return provider


# Global instance for easy importing
registry = AIRegistry()
