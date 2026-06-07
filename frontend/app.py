import os
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from requests.exceptions import RequestException

API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8002")


def api_post(endpoint, **kwargs):
    try:
        response = requests.post(f"{API_BASE}{endpoint}", **kwargs)
        response.raise_for_status()
        return response
    except RequestException as exc:
        st.error(
            "Unable to reach the backend service. "
            f"Please confirm the backend is running at {API_BASE}."
        )
        st.error(f"Error: {exc}")
        return None
    except Exception as exc:
        st.error(f"Unexpected error: {exc}")
        return None


def init_state():
    if "page" not in st.session_state:
        st.session_state.page = "Dashboard"
    if "resume_paths" not in st.session_state:
        st.session_state.resume_paths = []
    if "results" not in st.session_state:
        st.session_state.results = None
    if "filename_counts" not in st.session_state:
        st.session_state.filename_counts = {}
    if "ai_cache" not in st.session_state:
        st.session_state.ai_cache = {}
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "selected_candidate" not in st.session_state:
        st.session_state.selected_candidate = None


def load_css():
    st.markdown(
        """
<style>
:root { color-scheme: dark; }
body, .streamlit-expanderHeader { background: #0f172a !important; color: #f8fafc !important; }
.css-18e3th9, .css-1d391kg { background-color: #0f172a !important; }
[data-testid="stSidebar"] { background: #17233d !important; color: #f8fafc !important; border-right: 1px solid rgba(255,255,255,0.08); }
.block-container { padding: 1rem 1rem 1.5rem 1rem; }
.card { background: rgba(15,23,42,0.95); border: 1px solid rgba(255,255,255,0.08); border-radius: 24px; padding: 24px; box-shadow: 0 24px 60px rgba(15,23,42,0.35); margin-bottom: 20px; }
.metric-card { background: linear-gradient(180deg, rgba(30,41,59,0.95), rgba(15,23,42,0.95)); border: 1px solid rgba(255,255,255,0.08); border-radius: 24px; padding: 20px; color: #f8fafc; transition: transform 0.2s ease; }
.metric-card:hover { transform: translateY(-3px); }
.section-title { color: #f8fafc; font-size: 1.4rem; font-weight: 700; margin-bottom: 0.65rem; }
.status-chip { display: inline-flex; padding: 6px 14px; border-radius: 999px; font-size: 0.85rem; font-weight: 700; }
.status-shortlist { background: rgba(16,185,129,0.16); color: #a7f3d0; }
.status-review { background: rgba(251,191,36,0.16); color: #fef3c7; }
.status-reject { background: rgba(248,113,113,0.16); color: #fecaca; }
.progress-shell { background: rgba(255,255,255,0.08); border-radius: 999px; height: 10px; overflow: hidden; margin-top: 12px; }
.progress-fill { height: 100%; border-radius: 999px; background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%); }
.stButton>button { background-color: #3b82f6; border-radius: 999px; color: white; border: none; padding: 0.75rem 1.25rem; }
.stButton>button:hover { background-color: #2563eb; }
.st-bf { color: #94a3b8; }
h3 { word-break: break-word; overflow-wrap: break-word; white-space: normal !important; max-width: 100%; }
.candidate-name { display: block; word-break: break-word; overflow-wrap: break-word; white-space: normal !important; max-width: 100%; margin-bottom: 8px; }
</style>
""",
        unsafe_allow_html=True,
    )


def unique_filename(name: str):
    count = st.session_state.filename_counts.get(name, 0) + 1
    st.session_state.filename_counts[name] = count
    if count == 1:
        return name
    base, ext = os.path.splitext(name)
    return f"{base}_{count}{ext}"


def upload_and_rank(files, job_description):
    if not files:
        st.error("Please upload at least one PDF resume.")
        return None
    if not job_description.strip():
        st.error("Please add a job description.")
        return None

    resume_paths = []
    failed = []
    for file in files:
        filename = unique_filename(file.name)
        with st.spinner(f"Uploading {filename}..."):
            response = api_post(
                "/upload-resume",
                files={"file": (filename, file, "application/pdf")},
                timeout=120,
            )
        if response is None:
            return None
        if response.status_code == 200:
            resume_paths.append(response.json().get("path"))
        else:
            failed.append(filename)
    if failed:
        st.error(f"Failed to upload: {', '.join(failed)}")
    if resume_paths:
        with st.spinner("Analyzing and ranking candidates..."):
            response = api_post(
                "/rank-candidates",
                json={"resume_paths": resume_paths, "job_description": job_description},
                timeout=300,
            )
        if response is None:
            return None
        if response.status_code == 200:
            st.session_state.resume_paths = resume_paths
            st.session_state.results = response.json()
            return st.session_state.results
        st.error("Backend ranking request failed. Please confirm the FastAPI server is running.")
    return None


def format_status(recommendation):
    if recommendation.lower().startswith("strong"):
        return "Shortlist", "status-shortlist"
    if recommendation.lower().startswith("interview"):
        return "Review", "status-review"
    return "Reject", "status-reject"


def build_metrics(rankings):
    total = len(rankings)
    average = round(sum([item["score"] for item in rankings]) / total, 1) if total else 0
    shortlisted = sum(1 for item in rankings if item["recommendation"] in ["Strong Hire", "Interview"])
    rejected = sum(1 for item in rankings if item["recommendation"] == "Reject")
    highest = max([item["score"] for item in rankings]) if total else 0
    ai_count = sum(1 for item in rankings if item.get("ai_feedback"))
    return {
        "Total Resumes Processed": total,
        "Average Match Score": average,
        "Shortlisted Candidates": shortlisted,
        "Rejected Candidates": rejected,
        "Highest Candidate Score": highest,
        "AI Analyses Generated": ai_count,
    }


def render_hero():
    st.markdown(
        """
<div class='card'>
  <div style='display:flex; justify-content:space-between; flex-wrap:wrap; gap:24px;'>
    <div style='max-width:720px;'>
      <h1 style='margin-bottom:0.3rem; color:#f8fafc;'>AI Recruitment Copilot</h1>
      <p style='margin:0; color:#cbd5e1; font-size:1rem; line-height:1.8;'>AI-powered candidate intelligence platform for modern hiring teams.</p>
      <p style='margin-top:1rem; color:#94a3b8; line-height:1.75;'>Use artificial intelligence to analyze resumes, match candidates with job descriptions, rank applicants, generate interview questions, identify skill gaps, and accelerate hiring decisions.</p>
    </div>
    <div style='display:grid; gap:12px; min-width:240px;'>
      <div style='background:rgba(59,130,246,0.14); border:1px solid rgba(59,130,246,0.22); padding:18px; border-radius:20px; color:#f8fafc;'>
        <strong>Enterprise workflow</strong><br><span style='color:#94a3b8;'>Designed for talent acquisition teams</span>
      </div>
      <div style='background:rgba(34,197,94,0.14); border:1px solid rgba(34,197,94,0.24); padding:18px; border-radius:20px; color:#f8fafc;'>
        <strong>AI-driven insights</strong><br><span style='color:#94a3b8;'>Smart hiring decisions at scale</span>
      </div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_dashboard():
    st.markdown("<div class='card'><div class='section-title'>Dashboard</div></div>", unsafe_allow_html=True)
    rankings = st.session_state.results.get("rankings", []) if st.session_state.results else []
    metrics = build_metrics(rankings)
    cols = st.columns(3)
    palette = ["#3b82f6", "#22c55e", "#f59e0b", "#ef4444", "#6366f1", "#14b8a6"]
    for index, (label, value) in enumerate(metrics.items()):
        with cols[index % 3]:
            st.markdown(
                f"""
<div class='metric-card'>
  <div style='display:flex; justify-content:space-between; align-items:center;'>
    <span style='color:#94a3b8;'>{label}</span>
    <span style='font-size:1.6rem; font-weight:700; color:{palette[index]};'>{value}</span>
  </div>
</div>
""",
                unsafe_allow_html=True,
            )
    if rankings:
        st.markdown("<div class='card'><div class='section-title'>Top Candidate Snapshot</div></div>", unsafe_allow_html=True)
        top = rankings[0]
        cols = st.columns([1.5, 1, 1])
        with cols[0]:
            st.markdown(f"### {top['candidate']}")
            st.markdown(f"<span class='status-chip status-shortlist'>{top['recommendation']}</span>", unsafe_allow_html=True)
            st.write(f"{top['ai_feedback']}")
        with cols[1]:
            st.metric("Match Score", top['score'])
            st.metric("Semantic Score", top['semantic_score'])
        with cols[2]:
            st.markdown("#### Skills Overview")
            st.write(', '.join(top['matched_skills']) or 'None')
            st.write('---')
            st.write(', '.join(top['missing_skills']) or 'None')
    else:
        st.info("Start screening resumes to see enterprise-grade candidate insights.")


def render_screening():
    st.markdown("<div class='card'><div class='section-title'>Resume Screening</div></div>", unsafe_allow_html=True)
    left, right = st.columns([2, 1], gap="large")
    with left:
        job_description = st.text_area("Job Description", height=260, key="job_input")
        uploaded_files = st.file_uploader("Upload Resumes", accept_multiple_files=True, type=["pdf"], key="resume_uploader")
        st.write("Upload multiple PDF resumes, then rank candidates with the button below.")
        if st.button("Upload & Rank Candidates", key="upload_rank"):
            upload_and_rank(uploaded_files, job_description)
    with right:
        st.markdown("<div class='card'><div class='section-title'>Live Screening Summary</div></div>", unsafe_allow_html=True)
        st.metric("Uploaded Resumes", len(st.session_state.resume_paths))
        status_text = "Ready to screen" if not st.session_state.results else "Candidates ranked"
        st.markdown(f"<strong>Status:</strong> <span style='color:#94a3b8;'>{status_text}</span>", unsafe_allow_html=True)
        if st.session_state.results:
            remaining = len(st.session_state.results.get("rankings", []))
            st.metric("Candidates Ranked", remaining)
            st.write("AI recruiter tools are available once candidates are ranked.")
        else:
            st.write("Upload resumes to begin resume screening.")


def render_rankings():
    st.markdown("<div class='card'><div class='section-title'>Candidate Rankings</div></div>", unsafe_allow_html=True)
    rankings = st.session_state.results.get("rankings", []) if st.session_state.results else []
    if not rankings:
        st.warning("No candidate rankings available. Please screen resumes first.")
        return
    compare_options = [item["candidate"] for item in rankings]
    selected_names = st.multiselect("Select candidates to compare", compare_options, default=compare_options[:3], key="compare_names")
    if selected_names:
        compare_rows = []
        for name in selected_names:
            row = next((item for item in rankings if item["candidate"] == name), None)
            if row:
                compare_rows.append({
                    "Candidate": row["candidate"],
                    "Score": row["score"],
                    "Semantic": row["semantic_score"],
                    "Skills Match": row.get("skills_match", "N/A"),
                    "Recommendation": row["recommendation"],
                })
        st.table(pd.DataFrame(compare_rows))
    for i, candidate in enumerate(rankings):
        status_label, status_class = format_status(candidate["recommendation"])
        st.markdown(
            f"""
<div class='card'>
  <div style='display:grid; grid-template-columns:1fr auto; gap:20px; align-items:start;'>
    <div style='min-width:0;'>
      <h3 style='margin:0; color:#f8fafc; word-break:break-word; overflow-wrap:break-word;'>{candidate['candidate']}</h3>
      <div style='margin-top:8px;'><span class='status-chip {status_class}'>{status_label}</span></div>
    </div>
    <div style='text-align:right; white-space:nowrap;'>
      <div style='color:#94a3b8;'>Match Score</div>
      <div style='font-size:1.45rem; font-weight:700;'>{candidate['score']}</div>
    </div>
  </div>
  <div class='progress-shell'><div class='progress-fill' style='width:{candidate['score']}%;'></div></div>
  <div style='display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-top:18px;'>
    <div style='background:rgba(255,255,255,0.03); padding:16px; border-radius:18px;'>
      <strong>Matched Skills</strong>
      <p style='color:#94a3b8; margin:8px 0 0;'>{', '.join(candidate['matched_skills'][:5]) or 'None'}</p>
    </div>
    <div style='background:rgba(255,255,255,0.03); padding:16px; border-radius:18px;'>
      <strong>Missing Skills</strong>
      <p style='color:#94a3b8; margin:8px 0 0;'>{', '.join(candidate['missing_skills'][:5]) or 'None'}</p>
    </div>
  </div>
  <div style='display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-top:18px;'>
    <span style='color:#94a3b8;'>Resume: {candidate['resume_path']}</span>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )
        action_cols = st.columns(3)
        if action_cols[0].button("View Details", key=f"view_details_{i}"):
            st.session_state.page = "Candidate Detail"
            st.session_state.selected_candidate = candidate
            st.rerun()
        if action_cols[1].button("AI Analysis", key=f"ai_analysis_{i}"):
            st.session_state.page = "AI Recruiter"
            st.session_state.ai_candidate = candidate 
            st.rerun()
        if action_cols[2].button("Interview Qs", key=f"interview_questions_{i}"):
            st.session_state.page = "AI Recruiter"
            st.session_state.ai_candidate = candidate
            st.rerun()
   

def render_candidate_detail(candidate):
    st.markdown(f"<div class='card'><h3>{candidate['candidate']}</h3></div>", unsafe_allow_html=True)
    tabs = st.tabs(["Profile", "Skills", "AI Feedback", "Interview Questions", "Summary"])
    with tabs[0]:
        st.markdown(f"**Recommendation:** {candidate['recommendation']}")
        st.markdown(f"**Match Score:** {candidate['score']}")
        st.markdown(f"**Semantic Score:** {candidate['semantic_score']}")
        st.markdown(f"**Resume:** {candidate['resume_path']}")
    with tabs[1]:
        st.markdown("#### Matched Skills")
        st.write(', '.join(candidate['matched_skills']) or 'None')
        st.markdown("#### Missing Skills")
        st.write(', '.join(candidate['missing_skills']) or 'None')
    with tabs[2]:
        st.markdown("#### AI Feedback")
        st.write(candidate.get('ai_feedback', 'No AI feedback available.'))
    with tabs[3]:
        st.markdown("#### Interview Questions")
        st.write("Generate candidate-specific interview questions in AI Recruiter.")
    with tabs[4]:
        st.markdown("#### Resume Summary")
        st.write("Generate a resume summary in AI Recruiter.")


def render_analytics():
    st.markdown("<div class='card'><div class='section-title'>Analytics</div></div>", unsafe_allow_html=True)
    rankings = st.session_state.results.get("rankings", []) if st.session_state.results else []
    if not rankings:
        st.warning("No analytics available. Please screen resumes first.")
        return
    df = pd.DataFrame(rankings)
    df["status"] = df["recommendation"].apply(lambda x: "Shortlist" if x != "Reject" else "Reject")
    score_hist = px.histogram(df, x="score", nbins=10, title="Match Score Distribution", template="plotly_dark", color_discrete_sequence=["#3b82f6"])
    top_skills = pd.Series([skill for r in rankings for skill in r.get("matched_skills", [])]).value_counts().reset_index(name="count").rename(columns={"index": "skill"})
    missing_skills = pd.Series([skill for r in rankings for skill in r.get("missing_skills", [])]).value_counts().reset_index(name="count").rename(columns={"index": "skill"})
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(score_hist, use_container_width=True)
    with col2:
        st.plotly_chart(px.bar(top_skills.head(10), x="skill", y="count", title="Top Skills Found", template="plotly_dark", color_discrete_sequence=["#22c55e"]), use_container_width=True)
    st.plotly_chart(px.bar(missing_skills.head(10), x="skill", y="count", title="Missing Skills Distribution", template="plotly_dark", color_discrete_sequence=["#f59e0b"]), use_container_width=True)
    st.plotly_chart(px.bar(df.sort_values("score", ascending=False), x="candidate", y=["score", "semantic_score"], title="Candidate Ranking Comparison", template="plotly_dark"), use_container_width=True)
    st.plotly_chart(px.pie(df, names="status", title="Shortlisted vs Rejected", template="plotly_dark", color_discrete_sequence=["#22c55e", "#ef4444"]), use_container_width=True)


def render_ai_recruiter():
    st.markdown("<div class='card'><div class='section-title'>AI Recruiter Assistant</div></div>", unsafe_allow_html=True)
    left, right = st.columns([3, 1], gap="large")
    with left:
        st.markdown("#### Chat with your AI recruiter")
        default_query = st.session_state.get("pending_query", "")
        query = st.text_input("Enter a recruiter question", value=default_query, key="chat_input")

        if "pending_query" in st.session_state:
            del st.session_state["pending_query"]
            
        if st.button("Send Message", key="chat_send"):
            if query.strip():
                with st.spinner("Getting AI response..."):
                    resp = api_post(
                        "/chat",
                        json={"prompt": query, "resume_paths": st.session_state.resume_paths},
                        timeout=300,
                    )
                if resp is None:
                    return
                if resp.status_code == 200:
                    response_text = resp.json().get("response", "")
                    st.session_state.chat_history.append((query, response_text))
                else:
                    st.error("AI recruiter request failed.")
        for user_text, bot_text in reversed(st.session_state.chat_history):
            st.markdown(f"**You:** {user_text}")
            st.markdown(f"**Recruiter:** {bot_text}")
    with right:
        st.markdown("#### Suggested Questions")
        suggestions = [
            "Who is the best backend engineer?",
            "Which candidate has AWS experience?",
            "Compare top 3 candidates.",
            "Generate interview questions.",
            "Who has the highest semantic match?",
        ]
        for suggestion in suggestions:
            if st.button(suggestion, key=suggestion):
                st.session_state["pending_query"] = suggestion
                st.rerun()
    st.markdown("---")
    st.subheader("Candidate AI Tools")
    rankings = st.session_state.results.get("rankings", []) if st.session_state.results else []
    if not rankings:
        st.info("Rank candidates first to enable candidate-specific AI tools.")
        return
    candidate_name = st.selectbox("Select candidate", [item["candidate"] for item in rankings], key="ai_candidate")
    selected = next((item for item in rankings if item["candidate"] == candidate_name), rankings[0])
    button_cols = st.columns(3)
    with button_cols[0]:
        if st.button("Extract Strengths", key="btn_strengths"):
            cache_key = f"strengths_{candidate_name}"
            if cache_key not in st.session_state.ai_cache:
                with st.spinner("Extracting strengths..."):
                    resp = api_post(
                        "/extract-strengths",
                        json={"resume_path": selected["resume_path"]},
                        timeout=300,
                    )
                if resp is None:
                    return
                st.session_state.ai_cache[cache_key] = resp.json().get("strengths", []) if resp.status_code == 200 else []
            strengths = st.session_state.ai_cache[cache_key]
            st.markdown("#### Strengths")
            for item in strengths:
                st.write(f"- {item}")
    with button_cols[1]:
        if st.button("Summarize Resume", key="btn_summary"):
            cache_key = f"summary_{candidate_name}"
            if cache_key not in st.session_state.ai_cache:
                with st.spinner("Summarizing resume..."):
                    resp = api_post(
                        "/summarize-resume",
                        json={"resume_path": selected["resume_path"]},
                        timeout=300,
                    )
                if resp is None:
                    return
                st.session_state.ai_cache[cache_key] = resp.json().get("summary", []) if resp.status_code == 200 else []
            summary = st.session_state.ai_cache[cache_key]
            st.markdown("#### Resume Summary")
            for item in summary:
                st.write(f"- {item}")
    with button_cols[2]:
        if st.button("Interview Questions", key="btn_questions"):
            cache_key = f"questions_{candidate_name}"
            if cache_key not in st.session_state.ai_cache:
                with st.spinner("Generating interview questions..."):
                    resp = api_post(
                        "/generate-interview-questions",
                        json={"resume_path": selected["resume_path"], "job_description": st.session_state.get("job_input", "")},
                        timeout=300,
                    )
                if resp is None:
                    return
                st.session_state.ai_cache[cache_key] = resp.json().get("questions", []) if resp.status_code == 200 else []
            questions = st.session_state.ai_cache[cache_key]
            st.markdown("#### Interview Questions")
            for question in questions:
                st.write(f"- {question}")


def render_settings():
    st.markdown("<div class='card'><div class='section-title'>Settings</div></div>", unsafe_allow_html=True)
    st.write("This workspace is optimized for enterprise recruiting. Future settings can include company branding, API integrations, and custom candidate workflows.")


def main():
    init_state()
    load_css()
    with st.sidebar:
        st.title("AI Copilot")
        st.markdown("<div style='color:#94a3b8; margin-bottom:18px;'>Professional recruiter dashboard</div>", unsafe_allow_html=True)
        pages = [
            "Dashboard",
            "Resume Screening",
            "Candidate Rankings",
            "Candidate Detail",
            "Analytics",
            "AI Recruiter",
                "Settings",
        ]
        selected = st.radio("Navigation", pages, index=pages.index(st.session_state.page) if st.session_state.page in pages else 0)
        st.session_state.page = selected
    if st.session_state.page == "Dashboard":
        render_hero()
        render_dashboard()
    elif st.session_state.page == "Resume Screening":
        render_screening()
    elif st.session_state.page == "Candidate Rankings":
        render_rankings()
    elif st.session_state.page == "Analytics":
        render_analytics()
    elif st.session_state.page == "Candidate Detail":

        if st.session_state.selected_candidate is not None:
            render_candidate_detail(
                st.session_state.selected_candidate
        )
        else:
            st.warning("No candidate selected.")
        
    elif st.session_state.page == "AI Recruiter":
        render_ai_recruiter()
    else:
        render_settings()


if __name__ == "__main__":
    main()
