"""
Redaction logic for conserver-link-redact.

This module handles the processing of vCon objects to redact sensitive information
using OpenAI's GPT models with retry logic and fallback mechanisms.
"""

import time
import logging
from typing import Dict, Any, Optional
import yaml
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class RedactionEngine:
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.redact_patterns = self.config.get('redact_patterns', [])

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def redact_content(self, content: str) -> str:
        """Redact content based on configured patterns."""
        if not content:
            return ""
        
        redacted = content
        for pattern in self.redact_patterns:
            if pattern.lower() in redacted.lower():
                start_idx = redacted.lower().find(pattern.lower())
                end_idx = redacted.find('\n', start_idx)
                if end_idx == -1:
                    end_idx = len(redacted)
                
                redacted = (
                    redacted[:start_idx] + 
                    '[REDACTED]' +
                    redacted[end_idx:]
                )
        
        return redacted

    def run(self, vcon_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a vCon document."""
        if not vcon_data:
            return {}

        start_time = time.time()
        failures = 0
        redacted_vcon = vcon_data.copy()

        if 'dialog' in redacted_vcon:
            for entry in redacted_vcon['dialog']:
                try:
                    if 'content' in entry:
                        entry['content'] = self.redact_content(entry['content'])
                    if 'transcript' in entry:
                        entry['transcript'] = self.redact_content(entry['transcript'])
                except Exception as e:
                    logger.error(f"Redaction failed: {e}")
                    failures += 1

        processing_time = time.time() - start_time
        logger.info(f"conserver.link.redact.processing_time: {processing_time}")
        logger.info(f"conserver.link.redact.failures: {failures}")

        return redacted_vcon
