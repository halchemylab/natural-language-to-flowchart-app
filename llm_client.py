import os
import json
import logging
from openai import OpenAI, RateLimitError, APIError
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

# --- Main Client Function ---
def generate_graph_from_text(
    api_key: str,
    text: str,
    model: str = DEFAULT_MODEL,
    temperature: float = DEFAULT_TEMPERATURE,
    max_retries: int = MAX_RETRIES,
) -> Graph:
    """
    Generates a graph from natural language text using an LLM, with validation and retries.

    Args:
        api_key: The OpenAI API key.
        text: The user's natural language input.
        model: The model to use.
        temperature: The generation temperature.
        max_retries: The maximum number of times to retry on validation failure.

    Returns:
        A validated Graph object.

    Raises:
        GraphGenerationError: If generation and validation fail after all retries.
    """
    client = OpenAI(api_key=api_key)
    prompt = MAIN_PROMPT_TEMPLATE.format(user_text=text)
    
    for attempt in range(max_retries + 1):
        logging.info(f"Generation attempt {attempt + 1}...")
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
            
            raw_response_text = response.choices[0].message.content
            token_usage = response.usage
            
            logging.info(f"LLM call successful. Time: {end_time - start_time:.2f}s, Tokens: {token_usage.total_tokens}")
            
            # 1. Parse the JSON
            try:
                json_data = json.loads(raw_response_text)
            except json.JSONDecodeError as e:
                logging.warning(f"Attempt {attempt + 1}: Failed to parse JSON. Error: {e}")
                prompt = REPAIR_PROMPT_TEMPLATE.format(
                    user_text=text,
                    invalid_json=raw_response_text,
                    error_message="The response was not valid JSON. Please provide only a single, well-formed JSON object."
                )
                continue

            # 2. Validate with Pydantic
            try:
                graph = Graph.model_validate(json_data)
                logging.info("Graph validation successful.")
                return graph
            except ValidationError as e:
                logging.warning(f"Attempt {attempt + 1}: Graph validation failed. Errors: {e.errors()}")
                prompt = REPAIR_PROMPT_TEMPLATE.format(
                    user_text=text,
                    invalid_json=json.dumps(json_data, indent=2),
                    error_message=str(e)
                )
                continue

        except (RateLimitError, APIError) as e:
            logging.error(f"API Error on attempt {attempt + 1}: {e}")
            if attempt < max_retries:
                time.sleep(2 ** attempt) # Exponential backoff
            else:
                raise GraphGenerationError(f"API error after multiple retries: {e}") from e
        except Exception as e:
            logging.error(f"An unexpected error occurred on attempt {attempt + 1}: {e}")
            raise GraphGenerationError(f"An unexpected error occurred: {e}") from e

    raise GraphGenerationError("Failed to generate a valid graph after multiple attempts.")
