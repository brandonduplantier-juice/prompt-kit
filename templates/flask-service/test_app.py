"""
Smoke tests. Run before any deploy: python -m pytest -q

These use dummy credentials and never hit the network. They prove the service imports,
rejects bad auth, validates input, and returns the contracted JSON shape. They do not
prove the upstream integration works. That needs live credentials, and it is a separate
step you must not skip.
"""

import importlib.util
import os
import pathlib

os.environ["API_KEY"] = "test-key"
os.environ["SENTRY_DSN"] = ""

spec = importlib.util.spec_from_file_location(
    "app_under_test", pathlib.Path(__file__).parent / "app.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
client = mod.app.test_client()


def test_health_is_open():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"


def test_missing_key_is_rejected():
    assert client.get("/enrich?key=abc").status_code == 401


def test_wrong_key_is_rejected():
    r = client.get("/enrich?key=abc", headers={"X-API-Key": "wrong"})
    assert r.status_code == 401


def test_missing_parameter_is_rejected():
    r = client.get("/enrich", headers={"X-API-Key": "test-key"})
    assert r.status_code == 400
    assert r.get_json()["error"] == "missing_parameter"


def test_oversized_parameter_is_rejected():
    r = client.get("/enrich?key=" + "x" * 65, headers={"X-API-Key": "test-key"})
    assert r.status_code == 400


def test_response_shape_is_contracted(monkeypatch):
    monkeypatch.setattr(mod, "call_upstream", lambda *a, **k: ({"field_a": 1}, None))
    r = client.get("/enrich?key=abc", headers={"X-API-Key": "test-key"})
    assert r.status_code == 200
    body = r.get_json()
    for field in ("key", "field_a", "field_b", "errors"):
        assert field in body, f"contract broken, missing {field}"
