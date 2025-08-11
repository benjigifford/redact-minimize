def test_import():
    from conserver_link_redact import run_redaction
    assert callable(run_redaction)
