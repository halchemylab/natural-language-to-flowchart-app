import json
import logging
from collections.abc import Callable

from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)
from pydantic import ValidationError
import time

from graph_schema import Graph
from prompts import MAIN_PROMPT_TEMPLATE, REPAIR_PROMPT_TEMPLATE
from config import DEFAULT_MODEL, DEFAULT_TEMPERATURE, MAX_RETRIES

# --- Configuration ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Custom Exception ---
class GraphGenerationError(Exception):
    """Custom exception for errors during graph generation."""
    pass

def _extract_response_text(response) -> str:
    """Return the first response message, or raise a user-facing generation error."""
    choices = getattr(response, "choices", None) or []
    if not choices:
        raise GraphGenerationError("The model returned no response choices.")

    message = getattr(choices[0], "message", None)
    content = getattr(message, "content", None)
    if not content or not content.strip():
        raise GraphGenerationError("The model returned an empty response.")
    return content

def _total_tokens(response) -> int | None:
    usage = getattr(response, "usage", None)
    return getattr(usage, "total_tokens", None)

# --- Main Client Function ---
def generate_graph_from_text(
    api_key: str,
    text: str,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_retries: int = MAX_RETRIES,
    status_callback: Callable[[str], None] | None = None,
) -> Graph:
    """
    Generates a graph from natural language text using an LLM, with validation and retries.

    Args:
        api_key: The OpenAI API key.
        text: The user's natural language input.
        model: The model to use.
        temperature: The generation temperature.
        max_retries: The maximum number of times to retry on validation failure.
        status_callback: A function to call with status updates.

    Returns:
        A validated Graph object.

    Raises:
        GraphGenerationError: If generation and validation fail after all retries.
    """
    client = OpenAI(api_key=api_key)
    prompt = MAIN_PROMPT_TEMPLATE.format(user_text=text)
    
    def update_status(message: str) -> None:
        if status_callback:
            status_callback(message)

    for attempt in range(max_retries + 1):
        logging.info(f"Generation attempt {attempt + 1}...")
        update_status(f"🧠 Attempt {attempt + 1}: Contacting LLM...")
        
        try:
            start_time = time.time()
            
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                top_p=1.0,
                max_tokens=2048,
                response_format={"type": "json_object"},
            )
            
            end_time = time.time()
            
            raw_response_text = _extract_response_text(response)
            total_tokens = _total_tokens(response)
            
            logging.info(
                "LLM call successful. Time: %.2fs, Tokens: %s",
                end_time - start_time,
                total_tokens if total_tokens is not None else "unknown",
            )
            update_status("✅ LLM response received. Parsing and validating...")

            # 1. Parse the JSON
            try:
                json_data = json.loads(raw_response_text)
            except json.JSONDecodeError as e:
                logging.warning(f"Attempt {attempt + 1}: Failed to parse JSON. Error: {e}")
                update_status(f"⚠️ Attempt {attempt + 1}: Invalid JSON received. Retrying...")
                prompt = REPAIR_PROMPT_TEMPLATE.format(
                    user_text=text,
                    invalid_json=raw_response_text,
                    error_message="The response was not valid JSON. Please provide only a single, well-formed JSON object."
                )
                continue

            # 2. Validate with Pydantic
            try:
                update_status("🔍 Validating graph schema...")
                graph = Graph.model_validate(json_data)
                logging.info("Graph validation successful.")
                update_status("✅ Graph validation successful!")
                return graph
            except ValidationError as e:
                logging.warning(f"Attempt {attempt + 1}: Graph validation failed. Errors: {e.errors()}")
                update_status(f"⚠️ Attempt {attempt + 1}: Schema validation failed. Retrying...")
                prompt = REPAIR_PROMPT_TEMPLATE.format(
                    user_text=text,
                    invalid_json=json.dumps(json_data, indent=2),
                    error_message=str(e)
                )
                continue

        except AuthenticationError as e:
            logging.error("Authentication failed: %s", e)
            raise GraphGenerationError("Invalid OpenAI API key. Please check your key and try again.") from e
        except (RateLimitError, APITimeoutError, APIConnectionError, APIError) as e:
            logging.error(f"API Error on attempt {attempt + 1}: {e}")
            update_status("🔥 API error. Retrying in a moment...")
            if attempt < max_retries:
                time.sleep(2 ** attempt) # Exponential backoff
            else:
                raise GraphGenerationError(f"API error after multiple retries: {e}") from e
        except Exception as e:
            logging.error(f"An unexpected error occurred on attempt {attempt + 1}: {e}")
            raise GraphGenerationError(f"An unexpected error occurred: {e}") from e

    raise GraphGenerationError("Failed to generate a valid graph after multiple attempts.")
