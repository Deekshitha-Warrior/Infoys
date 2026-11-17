"""Exercise the review UI against a dedicated synthetic API account.
Run with the API test server running: python scripts/check_review.py --api-url URL
Uses synthetic feedback; never include its responses in a real pilot study.
"""
import argparse
import json
import os
from pathlib import Path
from unittest.mock import patch
import requests
from streamlit.testing.v1 import AppTest

parser = argparse.ArgumentParser()
parser.add_argument("--api-url", default="http://127.0.0.1:8014")
args = parser.parse_args()
os.environ["CAREERCAST_API_URL"] = args.api_url
# This script is only for a test server/database, never a production URL.
if not args.api_url.startswith(("http://127.0.0.1:", "http://localhost:")):
    raise SystemExit("Use a dedicated local test server with a disposable database.")
profile = {"technical_skills": ["python", "sql", "git"], "degree": "Synthetic test degree"}
identity = {"email": "milestone4-synthetic@example.com", "password": "SyntheticReview2026!"}
response = requests.post(args.api_url + "/api/auth/register", json={**identity, "name": "Synthetic Review", "confirm_password": identity["password"]}, timeout=30)
if response.status_code == 409:
    response = requests.post(args.api_url + "/api/auth/login", json=identity, timeout=30)
response.raise_for_status()
headers = {"Authorization": "Bearer " + response.json()["access_token"]}
response = requests.post(args.api_url + "/api/profile/me", headers=headers, json=profile, timeout=30)
response.raise_for_status()
app = Path(__file__).resolve().parents[1] / "backend/careercast_tools/review.py"
at = AppTest.from_file(str(app), default_timeout=45).run()
at.text_input[0].set_value(identity["email"])
at.text_input[1].set_value(identity["password"])
next(b for b in at.button if b.label == "Sign in").click().run()
assert not at.exception, at.exception
next(b for b in at.button if b.label == "Analyze saved profile").click().run()
assert not at.exception, at.exception
assert len(at.multiselect[0].value) == 2
assert len(at.dataframe) >= 2
next(b for b in at.button if b.label == "Build skill development report").click().run()
assert not at.exception, at.exception
assert at.session_state["pdf"].startswith(b"%PDF-")
assert b"career,skill,status" in at.session_state["csv"]

class SyntheticUpload:
    def getvalue(self):
        return json.dumps([profile, {"technical_skills": ["react", "html", "css"]}]).encode()
    @property
    def size(self):
        return len(self.getvalue())

# AppTest does not simulate browser file uploads; inject the file widget's value.
# Actual JSON validation/analytics still run through the authenticated HTTP API.
with patch("streamlit.file_uploader", return_value=SyntheticUpload()):
    next(b for b in at.button if b.label == "Analyze uploaded cohort").click().run()
assert not at.exception, at.exception
assert at.session_state["cohort"]["profile_count"] == 2
print("Review UI passed: login, comparison, probability charts, PDF/CSV export and uploaded cohort analytics.")
