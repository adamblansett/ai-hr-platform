#!/usr/bin/env python3
"""
CLI simulation script for upstream ai-recruiter offer acceptance handoff webhook.
Generates an HMAC-SHA256 signed payload and transmits it to ai-hr-platform.
"""

import argparse
import hashlib
import hmac
import json
import sys
import uuid
from datetime import date, datetime, timedelta, timezone
import urllib.request
import urllib.error

DEFAULT_SECRET = "dev-shared-recruiter-webhook-secret-key"
DEFAULT_ORG_ID = "11111111-1111-1111-1111-111111111111"
DEFAULT_ENDPOINT = "http://localhost:8000/api/v1/webhooks/recruiter/offer-accepted"

def main():
    parser = argparse.ArgumentParser(description="Simulate ai-recruiter candidate offer acceptance handoff")
    parser.add_argument("--url", default=DEFAULT_ENDPOINT, help="Target webhook endpoint")
    parser.add_argument("--secret", default=DEFAULT_SECRET, help="Shared HMAC secret key")
    parser.add_argument("--org-id", default=DEFAULT_ORG_ID, help="Target tenant organization UUID")
    parser.add_argument("--first-name", default="Marcus", help="Candidate first name")
    parser.add_argument("--last-name", default="Vance", help="Candidate last name")
    parser.add_argument("--email", default=None, help="Candidate email (defaults to unique email)")
    parser.add_argument("--role", default="Senior Distributed Systems Architect", help="Job title")
    parser.add_argument("--department", default="Engineering", help="Department")
    parser.add_argument("--manager-email", default="manager.sarah@acme.corp", help="Manager email")

    args = parser.parse_args()

    unique_suffix = uuid.uuid4().hex[:6]
    candidate_email = args.email or f"marcus.{unique_suffix}@candidate.dev"
    candidate_id = f"cand_recruiter_{unique_suffix}"
    event_id = f"evt_{uuid.uuid4().hex[:10]}"
    hire_date = (date.today() + timedelta(days=14)).isoformat()

    payload_dict = {
        "event_id": event_id,
        "event_type": "candidate.offer_accepted",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "organization_id": args.org_id,
        "candidate": {
            "recruiter_candidate_id": candidate_id,
            "first_name": args.first_name,
            "last_name": args.last_name,
            "email": candidate_email,
            "phone": "+1-555-019-8833",
            "job_title": args.role,
            "department": args.department,
            "hire_date": hire_date,
            "employment_type": "FULL_TIME",
            "manager_email": args.manager_email,
            "offer_signed_doc_url": f"https://storage.internal/recruiter/offers/{candidate_id}_signed.pdf",
            "custom_fields": {
                "recruiting_lead": "talent.team@acme.corp",
                "referral_source": "GitHub Open Source Contributor"
            }
        }
    }

    raw_json_bytes = json.dumps(payload_dict).encode("utf-8")

    # Compute HMAC-SHA256 signature
    sig = hmac.new(
        args.secret.encode("utf-8"),
        raw_json_bytes,
        hashlib.sha256
    ).hexdigest()

    signature_header = f"sha256={sig}"

    print("================================================================")
    print("🚀 Simulating ai-recruiter Candidate Offer Acceptance Webhook")
    print("================================================================")
    print(f"Target URL:         {args.url}")
    print(f"Event ID:           {event_id}")
    print(f"Candidate:          {args.first_name} {args.last_name} ({candidate_email})")
    print(f"Job Title:          {args.role}")
    print(f"Department:         {args.department}")
    print(f"Manager Email:      {args.manager_email}")
    print(f"HMAC Signature:     {signature_header}")
    print("----------------------------------------------------------------")

    req = urllib.request.Request(
        args.url,
        data=raw_json_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Recruiter-Signature": signature_header,
            "User-Agent": "ai-recruiter-webhook-dispatch/1.0"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            status_code = response.getcode()
            response_body = response.read().decode("utf-8")
            res_json = json.loads(response_body)

            print(f"✅ Webhook Accepted! HTTP {status_code}")
            print(f"Success:             {res_json.get('success')}")
            print(f"Message:             {res_json.get('message')}")
            print(f"Employee ID:         {res_json.get('employee_id')}")
            print(f"Tasks Created:       {res_json.get('onboarding_tasks_created')}")
            print(f"External IdP ID:     {res_json.get('external_idp_id')}")
            print("================================================================")
            sys.exit(0)

    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"❌ Webhook Rejected: HTTP {e.code} {e.reason}")
        print(f"Details: {error_body}")
        print("================================================================")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Connection Failed: {str(e)}")
        print("Ensure the backend is running (`uvicorn backend.app.main:app` or docker compose).")
        print("================================================================")
        sys.exit(1)

if __name__ == "__main__":
    main()
