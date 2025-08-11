def test_import():
    from conserver_link_minimize import run_minimization
    assert callable(run_minimization)
