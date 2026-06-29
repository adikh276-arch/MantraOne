import json
from typing import Type, TypeVar, Any, Callable, Awaitable
from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


async def generate_with_retry(generate_fn: Callable[[], Awaitable[str]], model: Type[T], max_retries: int = 3) -> T:
    """
    Executes an AI generation function, attempts to parse it into the Pydantic model.
    Retries on ValidationError or JSONDecodeError.
    """
    last_exception = None

    for attempt in range(max_retries):
        try:
            raw_response = await generate_fn()

            # Clean potential markdown wrapping
            if raw_response.startswith("```json"):
                raw_response = raw_response.strip("```json").strip("```").strip()
            elif raw_response.startswith("```"):
                raw_response = raw_response.strip("```").strip()

            parsed_json = json.loads(raw_response)
            return model.model_validate(parsed_json)

        except (json.JSONDecodeError, ValidationError) as e:
            last_exception = e
            # In a real implementation we might pass the error back to the LLM to fix it.
            # For now we just retry blindly.

    # Fallback: if we exhausted retries, we shouldn't crash the pipeline.
    # We return an empty/default instance of the model.
    # (Assuming the model allows defaults, or we can raise a specific AIValidationError)

    # We will raise it here, and the caller (Capability) must handle fallback logic.
    raise ValueError(
        f"Failed to validate structured output after {max_retries} retries. Last error: {str(last_exception)}"
    )
