"""
Minimization logic for conserver-link-minimize.

This module handles the processing of vCon objects to remove non-essential information
using OpenAI's GPT models with retry logic and fallback mechanisms.
"""

import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
import openai

logger = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(6), wait=wait_exponential(multiplier=1, min=1, max=60))
def _call_openai(prompt, model):
    """Call OpenAI API with retry on failure."""
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "system", "content": "You are a data minimization assistant."},
                  {"role": "user", "content": prompt}]
    )
    return response.choices[0].message["content"]


def _fallback_minimize(value):
    """Fallback minimization if OpenAI API fails."""
    # Drop the value entirely for minimization fallback
    return None


def run_minimization(vcon, options):
    """
    Runs the minimization process on the provided vCon object.
    Uses OpenAI for intelligent minimization with a fallback to simple removal.
    """
    start_time = time.time()
    failures = 0
    model = options.get("minimization_model", "gpt-4o-mini")

    minimization_config = options.get("minimization_config") or {}
    for component_type, configs in minimization_config.items():
        for entry in vcon.get(component_type, []):
            for cfg in configs:
                for field in cfg.get("fields_to_minimize", []):
                    try:
                        original_value = entry.get(field)
                        if original_value is None:
                            continue
                        prompt = f"Remove non-essential information from the following text and return a minimized version (or an empty string if nothing essential):\n\n{original_value}"
                        minimized_value = _call_openai(prompt, model)
                        if minimized_value is None:
                            raise ValueError("Empty minimization result")
                        entry[field] = minimized_value if minimized_value != "" else None
                    except Exception as e:
                        logger.error(f"Minimization failed for {component_type}.{field}: {e}")
                        entry[field] = _fallback_minimize(entry.get(field))
                        failures += 1

    processing_time = time.time() - start_time
    logger.info(f"conserver.link.minimize.processing_time: {processing_time}")
    logger.info(f"conserver.link.minimize.failures: {failures}")

    return vcon
