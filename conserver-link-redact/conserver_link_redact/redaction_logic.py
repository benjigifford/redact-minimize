"""
Redaction logic for conserver-link-redact.

This module handles the processing of vCon objects to redact sensitive information
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
        messages=[{"role": "system", "content": "You are a redaction assistant."},
                  {"role": "user", "content": prompt}]
    )
    # compatible with ChatCompletion response shape
    return response.choices[0].message["content"]


def _fallback_redact(value):
    """Fallback redaction if OpenAI API fails."""
    if isinstance(value, str):
        return "[REDACTED]"
    return None


def run_redaction(vcon, options):
    """
    Runs the redaction process on the provided vCon object.
    Uses OpenAI for intelligent redaction with a fallback to simple replacement.
    """
    start_time = time.time()
    failures = 0
    model = options.get("redaction_model", "gpt-4o-mini")

    redaction_config = options.get("redaction_config") or {}
    # Iterate configured component types (analysis, attachments, parties, dialog)
    for component_type, configs in redaction_config.items():
        for entry in vcon.get(component_type, []):
            for cfg in configs:
                for field in cfg.get("fields_to_redact", []):
                    try:
                        original_value = entry.get(field)
                        if original_value is None:
                            continue
                        prompt = f"Redact sensitive information from the following text and return only the redacted text:\n\n{original_value}"
                        redacted_value = _call_openai(prompt, model)
                        # If model returns an empty string, fall back
                        if not redacted_value:
                            raise ValueError("Empty redaction result")
                        entry[field] = redacted_value
                    except Exception as e:
                        logger.error(f"Redaction failed for {component_type}.{field}: {e}")
                        entry[field] = _fallback_redact(entry.get(field))
                        failures += 1

    processing_time = time.time() - start_time
    logger.info(f"conserver.link.redact.processing_time: {processing_time}")
    logger.info(f"conserver.link.redact.failures: {failures}")

    return vcon
