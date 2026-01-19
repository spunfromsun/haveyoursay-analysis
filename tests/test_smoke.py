def test_imports():
    import haveyoursay_analysis.api as api
    import haveyoursay_analysis.files as files
    import haveyoursay_analysis.cli as cli

    assert api is not None
    assert files is not None
    assert cli is not None
