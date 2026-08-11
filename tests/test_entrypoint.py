import importlib.util
from pathlib import Path

import support_app


def test_production_entrypoint_constructs_an_app(monkeypatch):
    sentinel = object()
    monkeypatch.setattr(support_app, "create_app", lambda: sentinel)
    path = Path(__file__).resolve().parents[1] / "app.py"
    spec = importlib.util.spec_from_file_location("ticketing_entrypoint_test", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    assert module.app is sentinel
