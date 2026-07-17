"""
Flask service template.

Shape follows the amazon-sourcing enrich service: API-key auth, input validation,
per-call error isolation, backoff on rate limits, one normalized JSON response.

Replace SERVICE_NAME and the placeholder logic. Do not remove the auth check.
"""

import os
import time
import logging
from functools import wraps

import requests
from flask import Flask, jsonify, request

# ---------------------------------------------------------------- config

SERVICE_NAME = "service-name-here"
API_KEY = os.environ.get("API_KEY")
UPSTREAM_BASE = os.environ.get("UPSTREAM_BASE", "")
REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", "20"))

logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
log = logging.getLogger(SERVICE_NAME)

app = Flask(__name__)

# Sentry only when a DSN is present, so local runs stay quiet.
_dsn = os.environ.get("SENTRY_DSN")
if _dsn:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration

    sentry_sdk.init(dsn=_dsn, integrations=[FlaskIntegration()], traces_sample_rate=0.0)
    log.info("sentry enabled")

# ---------------------------------------------------------------- auth


def require_api_key(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not API_KEY:
            log.error("API_KEY not configured, refusing all requests")
            return jsonify({"error": "server_misconfigured"}), 500
        if request.headers.get("X-API-Key") != API_KEY:
            return jsonify({"error": "unauthorized"}), 401
        return fn(*args, **kwargs)

    return wrapper


# ---------------------------------------------------------------- upstream


def call_upstream(path, params=None, max_attempts=4):
    """
    One upstream call with exponential backoff on 429 and 5xx.

    Returns (data, error). Never raises. Callers isolate per-call failure so one
    bad upstream does not take down the whole response.
    """
    delay = 1.0
    for attempt in range(1, max_attempts + 1):
        try:
            resp = requests.get(
                f"{UPSTREAM_BASE}{path}",
                params=params or {},
                timeout=REQUEST_TIMEOUT,
                headers={"User-Agent": f"{SERVICE_NAME}/1.0"},
            )
        except requests.RequestException as exc:
            if attempt == max_attempts:
                return None, f"network_error: {type(exc).__name__}"
            time.sleep(delay)
            delay *= 2
            continue

        if resp.status_code == 200:
            try:
                return resp.json(), None
            except ValueError:
                return None, "bad_json_from_upstream"

        if resp.status_code in (429, 500, 502, 503, 504) and attempt < max_attempts:
            retry_after = resp.headers.get("Retry-After")
            wait = float(retry_after) if retry_after and retry_after.isdigit() else delay
            log.warning("upstream %s, attempt %s, waiting %ss", resp.status_code, attempt, wait)
            time.sleep(wait)
            delay *= 2
            continue

        return None, f"upstream_{resp.status_code}"

    return None, "exhausted_retries"


# ---------------------------------------------------------------- logic


def build_result(key):
    """
    Pure-ish logic. Returns the normalized output object.

    Fields the upstream cannot supply stay explicitly null with a documented reason.
    Do not silently drop them, downstream consumers depend on a stable shape.
    """
    data, err = call_upstream("/endpoint", {"id": key})

    return {
        "key": key,
        "field_a": (data or {}).get("field_a"),
        "field_b": None,  # upstream does not expose this, see README
        "errors": [err] if err else [],
    }


# ---------------------------------------------------------------- routes


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": SERVICE_NAME}), 200


@app.get("/enrich")
@require_api_key
def enrich():
    key = (request.args.get("key") or "").strip()
    if not key:
        return jsonify({"error": "missing_parameter", "parameter": "key"}), 400
    if len(key) > 64:
        return jsonify({"error": "invalid_parameter", "parameter": "key"}), 400

    return jsonify(build_result(key)), 200


@app.errorhandler(404)
def not_found(_):
    return jsonify({"error": "not_found"}), 404


@app.errorhandler(500)
def server_error(_):
    log.exception("unhandled error")
    return jsonify({"error": "internal_error"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
