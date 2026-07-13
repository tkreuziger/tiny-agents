from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ModelConfig:
    """Configuration options for the language model.

    Attributes:
        model: The identifier or name of the model to use.
        temperature: Sampling temperature controlling randomness (higher is more random).
    """

    model: str
    temperature: float = 0.7


@dataclass(frozen=True, slots=True)
class TransportConfig:
    """Configuration options for the transport layer.

    Attributes:
        api_key: The API key used for authenticating requests, or None if not required.
        base_url: The base URL for the API endpoint, or None to use the default.
    """

    api_key: str | None = None
    base_url: str | None = None
