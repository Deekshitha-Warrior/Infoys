"""Run: python -m streamlit run review_app.py. Uses authenticated FastAPI only."""
import os
import json
import hashlib
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
def personal_review():
    if st.button("Analyze saved profile"):
        try:
            st.session_state["report"] = request("GET", "/api/intelligence/recommend", params={"k": 5}).json()
            for key in ["gap", "csv", "pdf"]:
                st.session_state.pop(key, None)
        except (requests.RequestException, ValueError) as exc:
            st.error(str(exc))
    report = st.session_state.get("report")
    if not report:
        st.info("Analyze your saved profile to compare careers and export reports.")
        return
    rows = report["recommendations"]
    frame = pd.DataFrame([{"Career": r["career"], "Model probability (%)": r["confidence"], "Skill alignment (%)": r["alignment"]} for r in rows])
    st.plotly_chart(px.bar(frame, x="Model probability (%)", y="Career", orientation="h", color_discrete_sequence=["#7955d5"]), width="stretch")
    st.caption("Probabilities are uncalibrated model scores, not the chance of getting a job. Ranked order also includes skill alignment.")
    st.dataframe(frame, hide_index=True)
    st.subheader("Compare career paths")
    selection = st.multiselect("Careers to compare", [r["career"] for r in rows], default=[r["career"] for r in rows[:2]])
    selected = [r for r in rows if r["career"] in selection]
    if selected:
        comparison = pd.DataFrame([{ "Career": r["career"], "Match index /100": r["ranking_score"], "Model probability (%)": r["confidence"], "Skill alignment (%)": r["alignment"], "Skills to build": ", ".join(r["missing_skills"]) or "No gaps in checklist" } for r in selected])
        st.dataframe(comparison, hide_index=True)
        chart = frame[frame["Career"].isin(selection)].melt(id_vars="Career", var_name="Measure", value_name="Score")
        st.plotly_chart(px.bar(chart, x="Career", y="Score", color="Measure", barmode="group"), width="stretch")
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

    st.subheader("Help evaluate recommendation relevance")
    st.caption("Optional feedback. Ratings 4 or 5 count as satisfied in the user acceptance report. No satisfaction score is claimed without real responses.")
    with st.form("satisfaction"):
        rating = st.selectbox("How satisfied are you with the relevance of these recommendations?", [None, 1, 2, 3, 4, 5], format_func=lambda value: "Choose a rating" if value is None else f"{value} / 5")
        submit_feedback = st.form_submit_button("Share recommendation feedback")
    if submit_feedback:
        if rating is None:
            st.warning("Choose a rating before submitting.")
        else:
            try:
                request("POST", "/api/intelligence/recommendation-feedback", json={"profile_hash": report["profile_hash"], "rating": rating})
                st.success("Thank you. Your feedback has been saved.")
            except (requests.RequestException, ValueError) as exc:
                st.error(str(exc))


def cohort_review():
    st.subheader("Cohort analytics")
    st.write("Upload a JSON list of 1–1,000 structured profiles you are authorized to analyze. Use deidentified skill and education fields; names, email addresses and resumes are not needed.")
    st.caption("Results describe only this uploaded cohort. They never include other CareerCast accounts. The API does not persist the uploaded profiles.")
    upload = st.file_uploader("Structured cohort JSON", type=["json"])
    if st.button("Analyze uploaded cohort"):
        st.session_state.pop("cohort", None)
        if upload is None:
            st.warning("Choose a JSON file first.")
        elif upload.size > 2 * 1024 * 1024:
            st.error("Use a JSON file smaller than 2 MB.")
        else:
            try:
                profiles = json.loads(upload.getvalue().decode("utf-8-sig"))
                if not isinstance(profiles, list):
                    raise ValueError("Supply a JSON list of structured profiles.")
                st.session_state["cohort"] = request("POST", "/api/intelligence/cohort", json={"profiles": profiles}).json()
                st.session_state["cohort_source"] = hashlib.sha256(upload.getvalue()).hexdigest()
            except (UnicodeError, ValueError, requests.RequestException) as exc:
                st.error(str(exc))
    result = st.session_state.get("cohort")
    if result and upload is not None and st.session_state.get("cohort_source") == hashlib.sha256(upload.getvalue()).hexdigest():
        st.metric("Profiles analyzed", result["profile_count"])
        st.metric("Mean top-career skill alignment", str(result["average_skill_alignment"]) + "%")
        st.caption("Mean alignment = sum of top-career alignment percentages / profiles. Career share = profiles assigned to that top career / cohort size × 100.")
        distribution = pd.DataFrame(result["career_distribution"])
        st.plotly_chart(px.bar(distribution, x="career", y="count", color_discrete_sequence=["#7955d5"]), width="stretch")
        st.dataframe(pd.DataFrame(result["common_skill_gaps"]), hide_index=True)
        st.download_button("Download cohort summary JSON", json.dumps(result, indent=2), "cohort-summary.json", "application/json")
        st.download_button("Download career distribution CSV", distribution.to_csv(index=False), "career-distribution.csv", "text/csv")
        st.caption(result["scope"])


personal_tab, cohort_tab = st.tabs(["Career review and comparison", "Cohort analytics"])
with personal_tab:
    personal_review()
with cohort_tab:
    cohort_review()
