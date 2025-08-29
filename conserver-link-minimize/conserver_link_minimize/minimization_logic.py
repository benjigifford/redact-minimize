"""
Minimization logic for conserver-link-minimize.

This module handles the processing of vCon objects to remove non-essential information
using OpenAI's GPT models with retry logic and fallback mechanisms.
"""

import time
import logging
import openai
from typing import Any, Dict, List
import pydash
from pathlib import Path
from typing import Dict, Any
import yaml
from tenacity import retry, stop_after_attempt, wait_exponential

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


def minimize_document(document: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Minimize document based on configuration with keep/drop actions.
    """
    if not config or 'analysis' not in config:
        return document
        
    for rule in config['analysis']:
        fields = rule.get('fields', [])
        action = rule.get('action')
        
        if action == 'keep':
            # Keep only specified fields
            result = {}
            for field in fields:
                value = get_nested_value(document, field)
                if value is not None:
                    set_nested_value(result, field, value)
            return result
            
        elif action == 'drop':
            # Drop specified fields
            result = document.copy()
            for field in fields:
                remove_field(result, field)
            return result
    
    return document

def get_nested_value(obj: Dict[str, Any], field: str) -> Any:
    """Get value from object using field expression."""
    if "[]" not in field:
        return pydash.get(obj, field)
    
    parts = field.split("[]")
    array_path = parts[0]
    array = pydash.get(obj, array_path, [])
    
    if not isinstance(array, list):
        return None
        
    if len(parts) == 1:
        return array
        
    # Handle nested array fields
    remainder = parts[1].lstrip('.')
    result = []
    for item in array:
        if isinstance(item, dict):
            value = get_nested_value(item, remainder)
            if value is not None:
                result.append({remainder: value})
    return result

def set_nested_value(obj: Dict[str, Any], field: str, value: Any) -> None:
    """Set value in object using field expression."""
    if "[]" not in field:
        pydash.set_(obj, field, value)
        return
        
    parts = field.split("[]")
    array_path = parts[0]
    
    if len(parts) == 1:
        pydash.set_(obj, array_path, value)
        return
        
    # For nested array fields, preserve the structure
    if isinstance(value, list):
        pydash.set_(obj, array_path, value)

def remove_field(obj: Dict[str, Any], field: str) -> None:
    """Remove field from object."""
    parts = field.split('.')
    current = obj
    
    for part in parts[:-1]:
        if part not in current:
            return
        current = current[part]
        
    if parts[-1] in current:
        del current[parts[-1]]

class MinimizationEngine:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.minimize_fields = self.config.get('minimize_fields', [])

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def minimize_content(self, content: str) -> str:
        """Minimize content based on configured fields."""
        if not content:
            return ""
        
        minimized = content
        for field in self.minimize_fields:
            if field.lower() in minimized.lower():
                start_idx = minimized.lower().find(field.lower())
                end_idx = minimized.find('\n', start_idx)
                if end_idx == -1:
                    end_idx = len(minimized)
                
                minimized = (
                    minimized[:start_idx] + 
                    field + " [MINIMIZED]" +
                    minimized[end_idx:]
                )
        
        return minimized

    def run(self, vcon_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a vCon document."""
        if not vcon_data:
            return {}

        minimized_vcon = vcon_data.copy()
        if 'dialog' in minimized_vcon:
            for entry in minimized_vcon['dialog']:
                if 'content' in entry:
                    entry['content'] = self.minimize_content(entry['content'])
                if 'transcript' in entry:
                    entry['transcript'] = self.minimize_content(entry['transcript'])

        return minimized_vcon
