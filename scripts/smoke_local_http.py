"""Read-only smoke of running API and built web; no healthy-infrastructure claim."""

import json
import urllib.error
import urllib.request

results = {}
for label, url, expected in [
    ("api", "http://127.0.0.1:8000/api/v1/health", 200),
    ("readiness", "http://127.0.0.1:8000/api/v1/ready", 503),
    ("web", "http://127.0.0.1:3000", 200),
]:
    try:
        response = urllib.request.urlopen(url, timeout=10)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        body = response.read().decode("utf-8")
        assert response.status == expected, (label, response.status)
        if label == "web":
            assert '<html lang="ar" dir="rtl"' in body
            assert "الخدمة غير جاهزة حاليًا" in body
            assert "إجابات تبدأ من معرفة متجرك." in body
        results[label] = {"status": response.status, "expected": expected, "passed": True}
print(
    json.dumps(
        {
            "results": results,
            "scope": "live API/Next loopback HTTP with unavailable dependencies; no visual QA",
        }
    )
)
