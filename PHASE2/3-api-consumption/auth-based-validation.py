#!/usr/bin/env python3
import os
from datetime import datetime, timezone
import httpx
import jwt

BASE = "http://127.0.0.1:8000"
USERNAME = os.getenv("DEMO_USERNAME", "demouser1")
PASSWORD = os.getenv("DEMO_PASSWORD", "demopass1")
SECRET = os.getenv("JWT_SECRET", "blahblah$$%$%")

passed = failed = 0

def check(label, ok, detail=""):
    global passed, failed
    print(f"[{'PASS' if ok else 'FAIL'}] {label} {detail}")
    passed += int(bool(ok))
    failed += int(not ok)


with httpx.Client(base_url=BASE, timeout=5.0) as client:

    r = client.get("/products")
    check("Public GET /products", r.status_code == 200, f"HTTP {r.status_code}")

    payload = {"name": "P4", "price": 5000, "in_stock": True}
    r = client.post("/products", json=payload)
    check("Public POST /products", r.status_code == 201, f"HTTP {r.status_code}")

    # Send an invalid token, we should expected 401 status
    r = client.post("/products", json=payload, headers={"Authorization": "Bearer invalid.token.value"})
    check("Protected POST invalid token -> 401", r.status_code == 401, f"HTTP {r.status_code}")


    # Try to Obtain a token with invalid creds
    r = client.post("/auth/token", data={"username": "demouser1", "password": "wrong-password"})
    check("Invalid login -> 401", r.status_code == 401, f"HTTP {r.status_code}")

    # Try to Obtain a token with valid creds
    r = client.post("/auth/token", data={"username": "demouser1", "password": "demopass1"})
    check("Valid login -> 200", r.status_code == 200, f"HTTP {r.status_code}")

    # Get the token from valid login
    token = r.json().get("access_token") if r.status_code == 200 else None
    check("Valid login -> bearer token", r.status_code == 200 and bool(token), f"HTTP {r.status_code}")

    if token:
        print("Token is present, let's create a product! ")
        payload = {"name": "P5", "price": 5000, "in_stock": True}

        # request without token - should fail
        r = client.post("/products", json=payload)
        check("Public POST /products", r.status_code == 401, f"HTTP {r.status_code}")

        # request with token
        r = client.post("/products", json=payload, headers={"Authorization": f"Bearer {token}"})
        check("Public POST /products", r.status_code == 201, f"HTTP {r.status_code}")

        



