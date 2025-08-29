import json
from pathlib import Path
from conserver_link_minimize.minimization_logic import MinimizationEngine

def test_run_with_vcon():
    """Test minimization with a complete vCon document."""
    engine = MinimizationEngine()
    
    test_vcon = {
        'version': '0.3.0',
        'id': 'test-123',
        'dialog': [
            {
                'id': 'msg1',
                'content': 'SSN: 123-45-6789',
                'transcript': 'Credit Card: 4111-1111-1111-1111'
            }
        ]
    }

    result = engine.run(test_vcon)
    
    # Check structure preservation
    assert result['version'] == test_vcon['version']
    assert result['id'] == test_vcon['id']
    
    # Check content minimization
    dialog = result['dialog'][0]
    assert '123-45-6789' not in dialog['content']
    assert '4111-1111-1111-1111' not in dialog['transcript']
    assert '[MINIMIZED]' in dialog['content']
    assert '[MINIMIZED]' in dialog['transcript']