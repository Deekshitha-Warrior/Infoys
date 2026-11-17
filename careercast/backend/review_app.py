"""Run: python -m streamlit run review_app.py. Uses authenticated FastAPI only."""
import os
import json
import requests
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="CareerCast Review", layout="wide")
st.title("CareerCast · Career review")
st.caption("Explore model scores, review competencies, and export your report.")
API_URL = os.getenv("CAREERCAST_API_URL", "http://127.0.0.1:8000").rstrip("/")


def request(method, path, **kwargs):
    headers = {"Authorization": "Bearer " + st.session_state.get("token", "")}
    response = requests.request(method, API_URL + path, headers=headers, timeout=60, **kwargs)
    if response.status_code == 401:
        for key in ["token", "report", "gap", "csv", "pdf"]:
            st.session_state.pop(key, None)
        raise ValueError("Session expired or email/password incorrect. Sign in again.")
    if not response.ok:
        try:
            detail = response.json().get("detail", "Request failed")
        except ValueError:
            detail = "API request failed: " + str(response.status_code)
        raise ValueError(str(detail))
    return response


if not st.session_state.get("token"):
    with st.form("login", clear_on_submit=True):
        st.subheader("Sign in with your CareerCast account")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Sign in")
    if submit:
        try:
            st.session_state["token"] = request("POST", "/api/auth/login", json={"email": email, "password": password}).json()["access_token"]
            st.rerun()
        except (requests.RequestException, ValueError) as exc:
            st.error(str(exc))
    st.info("Create your account and save your profile in the main CareerCast app first.")
    st.stop()

if st.sidebar.button("Sign out"):
    st.session_state.clear()
    st.rerun()
if st.button("Analyze saved profile"):
    try:
        st.session_state["report"] = request("GET", "/api/intelligence/recommend", params={"k": 5}).json()
        for key in ["gap", "csv", "pdf"]:
            st.session_state.pop(key, None)
    except (requests.RequestException, ValueError) as exc:
        st.error(str(exc))
report = st.session_state.get("report")
if not report:
    st.stop()
rows = report["recommendations"]
frame = pd.DataFrame([{"Career": r["career"], "Model probability (%)": r["confidence"], "Skill alignment (%)": r["alignment"]} for r in rows])
st.plotly_chart(px.bar(frame, x="Model probability (%)", y="Career", orientation="h", color_discrete_sequence=["#7955d5"]), width="stretch")
st.caption("Probabilities are uncalibrated model scores, not the chance of getting a job. Ranked order also includes skill alignment.")
st.dataframe(frame, hide_index=True)
st.download_button("Download prediction JSON", json.dumps(report, indent=2), "career-prediction.json", "application/json")
career = st.selectbox("Target career", [r["career"] for r in rows])
if st.button("Build skill development report"):
    try:
        st.session_state["gap"] = request("GET", "/api/intelligence/gap-report", params={"career": career}).json()
        st.session_state["csv"] = request("GET", "/api/intelligence/gap-report", params={"career": career, "format": "csv"}).content
        st.session_state["pdf"] = request("GET", "/api/intelligence/report.pdf", params={"career": career, "report_type": "skills"}).content
    except (requests.RequestException, ValueError) as exc:
        for key in ["gap", "csv", "pdf"]:
            st.session_state.pop(key, None)
        st.error(str(exc))
gap = st.session_state.get("gap")
if gap and gap["career"] == career:
    st.subheader("Your competency improvement plan")
    st.metric("Core-skill alignment", str(gap["alignment"]) + "%")
    for action in gap["actions"]:
        with st.expander(action["skill"], expanded=True):
            st.write(action["practice"])
            st.caption(action["evidence"])
            st.link_button("Find learning resources", action["resource_url"])
    if not gap["actions"]:
        st.success("All checklist skills are listed in your profile. Demonstrate them with portfolio evidence.")
    st.download_button("Download skill gap CSV", st.session_state["csv"], "skill-gap.csv", "text/csv")
    st.download_button("Download personalized PDF", st.session_state["pdf"], "skill-development.pdf", "application/pdf")
st.info(report["data_scope"])
