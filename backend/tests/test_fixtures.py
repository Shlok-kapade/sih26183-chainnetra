from app.ingest.fixtures import load_fixture, save_fixture


def test_save_and_load_fixture(tmp_path, monkeypatch):
    # Override FIXTURE_DIR to use tmp_path
    import app.ingest.fixtures as fx_mod
    monkeypatch.setattr(fx_mod, 'FIXTURE_DIR', str(tmp_path))

    test_data = {"data": [{"tx": "test123"}]}
    save_fixture("test_provider", "test_id", test_data)

    loaded = load_fixture("test_provider", "test_id")
    assert loaded == test_data

def test_load_missing_fixture(tmp_path, monkeypatch):
    import app.ingest.fixtures as fx_mod
    monkeypatch.setattr(fx_mod, 'FIXTURE_DIR', str(tmp_path))

    result = load_fixture("nonexistent", "nope")
    assert result is None
