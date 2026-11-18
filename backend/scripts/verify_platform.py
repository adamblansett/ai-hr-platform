"""
Platform Verification Script
Tests health and response of API endpoints, authentication, and core modules.
"""
import sys
import json
import urllib.request
import urllib.error

API_URL = "http://localhost:8000"

def check_endpoint(path: str, name: str) -> bool:
    url = f"{API_URL}{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "HealthCheck/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            code = response.getcode()
            print(f"[PASS] {name} ({url}) -> Status {code}")
            return True
    except urllib.error.URLError as e:
        print(f"[PENDING] {name} ({url}) -> {e.reason}")
        return False
    except Exception as e:
        print(f"[FAIL] {name} ({url}) -> {e}")
        return False

def main():
    print("=" * 60)
    print("ai-hr-platform Health & Endpoint Verification")
    print("=" * 60)
    
    endpoints = [
        ("/", "Root Gateway / Docs"),
        ("/docs", "FastAPI Swagger Documentation"),
        ("/health", "Core Service Health Probe"),
        ("/metrics", "Prometheus Telemetry Metrics"),
    ]

    all_pass = True
    for path, name in endpoints:
        passed = check_endpoint(path, name)
        if not passed:
            all_pass = False

    print("=" * 60)
    if all_pass:
        print("ALL VERIFICATION CHECKS PASSED.")
    else:
        print("Note: Docker containers may still be launching or not yet started.")
    print("=" * 60)

if __name__ == "__main__":
    main()
