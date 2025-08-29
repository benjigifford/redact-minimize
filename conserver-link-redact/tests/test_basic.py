import pytest
from unittest.mock import patch, mock_open
import yaml
from conserver_link_redact.redaction_logic import RedactionEngine

@pytest.fixture
def mock_config():
    return {
        'redact_patterns': [
            'SSN:',
            'Credit Card:',
            'Password:'
        ]
    }

@pytest.fixture
def mock_vcon():
    return {
        'version': '0.3.0',
        'id': 'test-123',
        'dialog': [
            {
                'id': 'dialog-1',
                'content': 'My SSN: 123-45-6789',
                'transcript': 'Credit Card: 4111-1111-1111-1111'
            }
        ]
    }

def test_redact_empty_content(mock_config):
    with patch('builtins.open', mock_open(read_data=yaml.dump(mock_config))):
        engine = RedactionEngine()
        assert engine.redact_content("") == ""
        assert engine.redact_content(None) == ""

def test_redact_with_sensitive_data(mock_config):
    with patch('builtins.open', mock_open(read_data=yaml.dump(mock_config))):
        engine = RedactionEngine()
        content = "My SSN: 123-45-6789\nOther info"
        result = engine.redact_content(content)
        assert "[REDACTED]" in result
        assert "SSN: 123-45-6789" not in result

def test_run_with_vcon(mock_config, mock_vcon):
    with patch('builtins.open', mock_open(read_data=yaml.dump(mock_config))):
        engine = RedactionEngine()
        result = engine.run(mock_vcon)
        
        assert result['version'] == mock_vcon['version']
        assert result['id'] == mock_vcon['id']
        assert '[REDACTED]' in result['dialog'][0]['content']
        assert '[REDACTED]' in result['dialog'][0]['transcript']

def test_multi_pattern_redaction(mock_config):
    with patch('builtins.open', mock_open(read_data=yaml.dump(mock_config))):
        engine = RedactionEngine()
        content = "SSN: 123-45-6789\nCredit Card: 4111-1111-1111-1111"
        result = engine.redact_content(content)
        assert content not in result
        assert result.count("[REDACTED]") == 2
