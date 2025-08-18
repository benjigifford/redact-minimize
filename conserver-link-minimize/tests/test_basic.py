from conserver_link_minimize.minimization_logic import minimize_document

def test_keep_simple_fields():
    document = {
        "abc": 123,
        "efg": "hello",
        "xyz": "should be removed"
    }
    
    config = {
        "analysis": [{
            "fields": ["abc", "efg"],
            "action": "keep"
        }]
    }
    
    result = minimize_document(document, config)
    assert result == {"abc": 123, "efg": "hello"}

def test_drop_simple_fields():
    document = {
        "abc": 123,
        "efg": "hello",
        "xyz": "should be kept"
    }
    
    config = {
        "analysis": [{
            "fields": ["abc", "efg"],
            "action": "drop"
        }]
    }
    
    result = minimize_document(document, config)
    assert result == {"xyz": "should be kept"}

def test_nested_array_fields():
    document = {
        "foo": {
            "bar": [
                {"baz": 1, "other": "remove"},
                {"baz": 2, "other": "remove"}
            ]
        }
    }
    
    config = {
        "analysis": [{
            "fields": ["foo.bar[].baz"],
            "action": "keep"
        }]
    }
    
    result = minimize_document(document, config)
    assert result == {
        "foo": {
            "bar": [
                {"baz": 1},
                {"baz": 2}
            ]
        }
    }

def test_import():
    from conserver_link_minimize import run_minimization
    assert callable(run_minimization)
