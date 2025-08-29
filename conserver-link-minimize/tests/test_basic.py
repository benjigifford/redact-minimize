import pytest
from unittest.mock import patch, mock_open
import yaml
from conserver_link_minimize.minimization_logic import MinimizationEngine

@pytest.fixture
def mock_config():
    return {
        'minimize_fields': [
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

def test_minimize_empty_content(mock_config):
    with patch('builtins.open', mock_open(read_data=yaml.dump(mock_config))):
        minimizer = MinimizationEngine()
        assert minimizer.minimize_content("") == ""
        assert minimizer.minimize_content(None) == ""

def test_minimize_no_sensitive_data(mock_config):
    content = "Hello world\nThis is a test"
    with patch('builtins.open', mock_open(read_data=yaml.dump(mock_config))):
        minimizer = MinimizationEngine()
        assert minimizer.minimize_content(content) == content

def test_minimize_with_sensitive_data(mock_config):
    content = "My SSN: 123-45-6789\nOther info"
    with patch('builtins.open', mock_open(read_data=yaml.dump(mock_config))):
        minimizer = MinimizationEngine()
        result = minimizer.minimize_content(content)
        assert "SSN: [MINIMIZED]" in result
        assert "123-45-6789" not in result

def test_minimize_content(mock_config):
    with patch('builtins.open', mock_open(read_data=yaml.dump(mock_config))):
        minimizer = MinimizationEngine()
        result = minimizer.minimize_content('My SSN: 123-45-6789')
        assert 'SSN: [MINIMIZED]' in result
        assert '123-45-6789' not in result

def test_run_with_vcon(mock_config, mock_vcon):
    with patch('builtins.open', mock_open(read_data=yaml.dump(mock_config))):
        minimizer = MinimizationEngine()
        result = minimizer.run(mock_vcon)
        
        assert result['version'] == mock_vcon['version']
        assert result['id'] == mock_vcon['id']
        assert '[MINIMIZED]' in result['dialog'][0]['content']
        assert '[MINIMIZED]' in result['dialog'][0]['transcript']
        assert '123-45-6789' not in result['dialog'][0]['content']
        assert '4111-1111-1111-1111' not in result['dialog'][0]['transcript']
