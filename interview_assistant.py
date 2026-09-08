import os
import re
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
import PyPDF2
from datetime import datetime

try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    load_dotenv()
    api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

# ─────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────
CONFIG = {
    "model": "mixtral-8x7b-32768",  # ✅ UPDATED: Changed from llama-3.3-70b-versatile
    "model_display": "Mixtral 8x7B",  # ✅ UPDATED: Display name
    "max_tokens": 500,
    "temperature": 0.7,
    "app_name": "ResumeIntel",
    "author": "Jai Prakash Shettigar"
}

# ─────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────
st.set_page_config(
    page_title=CONFIG["app_name"],
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────
# State Initialization
# ─────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "user_email" not in st.session_state:
    st.session_state["user_email"] = ""

if "users_db" not in st.session_state:
    # Pre-seeded users for instant login testing
    st.session_state["users_db"] = {
        "alex@example.com": "password123",
        "demo@resumeintel.ai": "demo123"
    }

if "theme" not in st.session_state:
    st.session_state["theme"] = "light"

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "active_nav" not in st.session_state:
    st.session_state["active_nav"] = "Analyzer"

if "sidebar_view" not in st.session_state:
    st.session_state["sidebar_view"] = "Saved Analysis"

# ─────────────────────────────────────────
# Dynamic CSS Design System (Light & Dark Themes)
# ─────────────────────────────────────────
is_dark = st.session_state["theme"] == "dark"

bg_color = "#0f172a" if is_dark else "#f8fafc"
sidebar_bg = "#1e293b" if is_dark else "#f1f5f9"
card_bg = "#1e293b" if is_dark else "#ffffff"
text_color = "#f8fafc" if is_dark else "#0f172a"
muted_text = "#94a3b8" if is_dark else "#64748b"
border_color = "#334155" if is_dark else "#e2e8f0"
primary_accent = "#38bdf8" if is_dark else "#0ea5e9"
pill_active_bg = "rgba(56, 189, 248, 0.18)" if is_dark else "#0ea5e9"
pill_active_text = "#38bdf8" if is_dark else "#ffffff"
doc_bg = "#090d16" if is_dark else "#ffffff"
doc_text = "#f1f5f9" if is_dark else "#1e293b"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}

    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 1px solid {border_color} !important;
    }}

    /* Top Navigation Bar */
    .nav-bar {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem 1.5rem;
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 12px;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.04);
    }}
    .nav-brand {{
        font-weight: 800;
        font-size: 1.25rem;
        color: {text_color};
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    .nav-brand-logo {{
        background: {primary_accent};
        color: #ffffff;
        padding: 4px 8px;
        border-radius: 8px;
        font-size: 0.85rem;
    }}
    .nav-tabs-group {{
        display: flex;
        gap: 0.5rem;
        background: {sidebar_bg};
        padding: 4px;
        border-radius: 8px;
        border: 1px solid {border_color};
    }}
    .nav-tab-item {{
        padding: 6px 16px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 600;
        color: {muted_text};
        cursor: pointer;
    }}
    .nav-tab-active {{
        background: {card_bg};
        color: {primary_accent};
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }}

    /* Left Sidebar Menu Styles */
    .sidebar-section-title {{
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: {muted_text};
        margin: 1rem 0 0.5rem 0;
    }}
    .sidebar-nav-item {{
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.6rem 0.85rem;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 600;
        color: {muted_text};
        margin-bottom: 0.25rem;
    }}
    .sidebar-nav-active {{
        background: {pill_active_bg};
        color: {pill_active_text};
    }}

    /* Main Workspace Header */
    .workspace-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 1.25rem;
        padding-bottom: 1rem;
        border-bottom: 1px solid {border_color};
    }}
    .workspace-title {{
        font-size: 1.6rem;
        font-weight: 800;
        color: {text_color};
        margin: 0;
    }}
    .workspace-sub {{
        font-size: 0.85rem;
        color: {muted_text};
        margin-top: 0.25rem;
    }}

    /* Resume Document Viewer Card */
    .resume-viewer-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
    }}
    .resume-viewer-top {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 0.75rem;
        margin-bottom: 1rem;
        border-bottom: 1px solid {border_color};
        font-size: 0.85rem;
        font-weight: 600;
        color: {muted_text};
    }}
    .resume-paper {{
        background: {doc_bg};
        color: {doc_text};
        border: 1px solid {border_color};
        border-radius: 8px;
        padding: 1.5rem;
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
        line-height: 1.6;
        max-height: 420px;
        overflow-y: auto;
    }}

    /* Right Column Insights */
    .readiness-card {{
        background: {"rgba(56, 189, 248, 0.1)" if is_dark else "#e0f2fe"};
        border: 1px solid {"rgba(56, 189, 248, 0.3)" if is_dark else "#bae6fd"};
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }}
    .readiness-title {{
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 0.5rem;
    }}
    .readiness-desc {{
        font-size: 0.85rem;
        line-height: 1.5;
        color: {muted_text};
    }}

    /* Question Category Tags */
    .question-category-tag {{
        display: inline-block;
        font-size: 0.65rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #38bdf8;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }}

    /* Confidence Card */
    .confidence-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 12px;
        padding: 1rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-top: 1.5rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
    }}
    .confidence-badge {{
        background: {primary_accent};
        color: #ffffff;
        font-weight: 800;
        font-size: 1.25rem;
        border-radius: 8px;
        min-width: 60px;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    /* Chat Styles */
    .stChatMessage {{
        background: {card_bg};
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }}

</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────

def extract_resume_text(pdf_file):
    """Extract text from PDF resume"""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text, len(reader.pages)
    except Exception as e:
        st.error(f"Error reading PDF: {e}")
        return "", 0

def parse_resume_details(resume_text, filename):
    """Parse key details from resume using regex patterns"""
    details = {
        "name": "Unknown Candidate",
        "email": "",
        "phone": "",
        "skills": [],
        "filename": filename,
        "raw_text": resume_text
    }
    
    lines = resume_text.split('\n')
    if lines:
        details["name"] = lines[0].strip() or "Unknown Candidate"
    
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    emails = re.findall(email_pattern, resume_text)
    if emails:
        details["email"] = emails[0]
    
    phone_pattern = r'(\d{3}[-.]?\d{3}[-.]?\d{4}|\+\d{1,3}\s?\d{1,14})'
    phones = re.findall(phone_pattern, resume_text)
    if phones:
        details["phone"] = phones[0]
    
    skill_keywords = ["Python", "JavaScript", "Java", "C++", "SQL", "HTML", "CSS", 
                      "React", "Vue", "Angular", "Node.js", "Django", "Flask",
                      "AWS", "Azure", "Docker", "Kubernetes", "Git", "Linux",
                      "Machine Learning", "Data Analysis", "UI/UX", "Product Design"]
    
    details["skills"] = [skill for skill in skill_keywords if skill.lower() in resume_text.lower()]
    
    return details

def generate_chat_download(messages, candidate_name):
    """Generate downloadable chat transcript"""
    content = f"Interview Transcript - {candidate_name}\n"
    content += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    content += "=" * 50 + "\n\n"
    
    for msg in messages:
        role = "CANDIDATE" if msg["role"] == "assistant" else "INTERVIEWER"
        content += f"\n[{role}]\n{msg['content']}\n"
        content += "-" * 40 + "\n"
    
    return content

# ─────────────────────────────────────────
# Top Bar with Theme Toggle
# ─────────────────────────────────────────
col_theme, col_spacer, col_user, col_logout = st.columns([1, 5, 1.5, 1])

with col_theme:
    theme_toggle = st.toggle("🌙", value=(st.session_state["theme"] == "dark"), label_visibility="collapsed")
    if theme_toggle != (st.session_state["theme"] == "dark"):
        st.session_state["theme"] = "dark" if theme_toggle else "light"
        st.rerun()

with col_spacer:
    pass

if st.session_state["authenticated"]:
    with col_user:
        user_disp = st.session_state['user_email'].split('@')[0]
        st.markdown(f"<div style='padding-top:6px; font-weight:600; font-size:0.85rem;'>👤 {user_disp}</div>", unsafe_allow_html=True)

    with col_logout:
        if st.button("Log Out", key="top_logout", use_container_width=True):
            st.session_state["authenticated"] = False
            st.rerun()

st.markdown("<hr style='margin:0.5rem 0 1.25rem 0; border:none; border-top:1px solid rgba(148,163,184,0.2);'>", unsafe_allow_html=True)

# ─────────────────────────────────────────
# SIDEBAR (ResumeIntel Style)
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-section-title">HISTORY • YOUR RECENT ACTIVITY</div>', unsafe_allow_html=True)

    sb_item1 = "Recent Uploads"
    sb_item2 = "Saved Analysis"
    sb_item3 = "Interview History"
    sb_item4 = "Settings"

    if st.button(f"🕒 {sb_item1}", use_container_width=True):
        st.session_state["sidebar_view"] = sb_item1
    if st.button(f"📊 {sb_item2}", use_container_width=True, type="primary"):
        st.session_state["sidebar_view"] = sb_item2
    if st.button(f"💬 {sb_item3}", use_container_width=True):
        st.session_state["sidebar_view"] = sb_item3
    if st.button(f"⚙️ {sb_item4}", use_container_width=True):
        st.session_state["sidebar_view"] = sb_item4

    st.markdown("---")
    st.markdown("### Upload PDF Resume")
    pdf_file = st.file_uploader("Upload PDF Resume", type=["pdf"], label_visibility="collapsed")

    if pdf_file:
        resume_text, page_count = extract_resume_text(pdf_file)
        st.session_state["resume_text"] = resume_text
        details = parse_resume_details(resume_text, pdf_file.name)
        st.session_state["details"] = details
        st.session_state["page_count"] = page_count
        st.success(f"Loaded: {pdf_file.name}")

    st.markdown("---")
    if st.button("🔄 Reset Interview", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()

    if "messages" in st.session_state and len(st.session_state["messages"]) > 0:
        cand_name = st.session_state.get("details", {}).get("name", "Candidate")
        chat_txt = generate_chat_download(st.session_state["messages"], cand_name)
        st.download_button("💾 Export Transcript", data=chat_txt, file_name="interview_transcript.txt", mime="text/plain", use_container_width=True)

    st.markdown("""
    <div style="margin-top:2rem; font-size:0.75rem; color:#94a3b8;">
        <b>Help Center</b> &nbsp;•&nbsp; Privacy Policy
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# MAIN 3-COLUMN LAYOUT
# ─────────────────────────────────────────

# Default candidate sample data if no PDF uploaded yet
if "details" not in st.session_state:
    sample_text = """ALEX RIVERS
Senior Product Designer • alex.rivers@example.com • 415-555-0198

EXPERIENCE:
Global Tech Solutions (2019 - Present)
Lead Product Designer
- Spearheaded the redesign of core enterprise dashboard, resulting in 24% increase in user retention.
- Established comprehensive design system reducing front-end development time by 30%.
- Mentored a team of 4 junior designers and collaborated with cross-functional stakeholders.

Creative Stream Inc. (2016 - 2019)
UI/UX Designer
- Developed mobile-first interfaces for high-traffic e-commerce platforms."""

    st.session_state["details"] = {
        "name": "Alex Rivers",
        "email": "alex.rivers@example.com",
        "phone": "415-555-0198",
        "skills": ["Product Design", "UI/UX", "Leadership", "Design System"],
        "filename": "alex_rivers_resume_2024.pdf",
        "raw_text": sample_text
    }
    st.session_state["resume_text"] = sample_text
    st.session_state["page_count"] = 2

details = st.session_state["details"]
page_count = st.session_state.get("page_count", 1)

# Workspace Title Bar
col_w1, col_w2 = st.columns([7, 3])
with col_w1:
    st.markdown(f'''
    <div class="workspace-header">
        <div>
            <h1 class="workspace-title">{details["name"]} - Analysis</h1>
            <div class="workspace-sub">Resume for {details["name"]} • File: {details["filename"]}</div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

with col_w2:
    btn1, btn2 = st.columns(2)
    with btn1:
        if st.button("📥 Export PDF", use_container_width=True):
            st.info("Exporting PDF report...")
    with btn2:
        if st.button(" Share Report", use_container_width=True, type="primary"):
            st.success("Share link copied!")

# 2-Column Split: Center Resume Document & AI Chat | Right Readiness Panel
col_center, col_right = st.columns([6.5, 3.5])

with col_center:
    # Resume Preview Box
    st.markdown(f'''
    <div class="resume-viewer-card">
        <div class="resume-viewer-top">
            <span>📄 {details["filename"]}</span>
            <span>Page 1 / {page_count}</span>
        </div>
        <div class="resume-paper">
            <pre style="white-space: pre-wrap; font-family: inherit; margin: 0;">{details["raw_text"]}</pre>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # Interactive AI Interview Simulation Chat
    st.markdown("### 💬 AI Candidate Interview Session")

    for msg in st.session_state["messages"]:
        avatar = "👤" if msg["role"] == "user" else "⚡"
        with st.chat_message(msg["role"], avatar=avatar):
            st.write(msg["content"])

    # Handle quick questions or user chat input
    q_trigger = st.session_state.pop("quick_question", None)
    user_q = st.chat_input("Ask an interview question to the candidate...")

    if user_q:
        q_trigger = user_q

    if q_trigger:
        st.session_state["messages"].append({"role": "user", "content": q_trigger})
        with st.chat_message("user", avatar="👤"):
            st.write(q_trigger)

        system_prompt = f"""You are {details['name']} being interviewed for a job based on your resume.
Answer all questions based ONLY on your resume information.
Speak in first person naturally, professionally, and confidently.
Keep responses impactful and concise (3-4 sentences).

RESUME:
{st.session_state['resume_text']}"""

        messages = [{"role": "system", "content": system_prompt}]
        for msg in st.session_state["messages"]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        with st.chat_message("assistant", avatar="⚡"):
            with st.spinner("AI Candidate analyzing resume and answering..."):
                res = client.chat.completions.create(
                    model=CONFIG["model"],
                    messages=messages,
                    max_tokens=CONFIG["max_tokens"],
                    temperature=CONFIG["temperature"]
                )
                ans = res.choices[0].message.content
                st.write(ans)

        st.session_state["messages"].append({"role": "assistant", "content": ans})

with col_right:
    # AI Interview Readiness Box
    st.markdown("""
    <div class="readiness-card">
        <div class="readiness-title">✨ AI Interview Readiness</div>
        <div class="readiness-desc">
            Based on this resume, we've identified 4 high-probability questions recruiters will ask. Focus on your specific metrics to stand out.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### High-Probability Questions")

    # Categorized Questions matching screenshot
    st.markdown('<div class="question-category-tag">BEHAVIORAL QUESTION</div>', unsafe_allow_html=True)
    q_beh = "Tell me about your background and core design philosophy."
    if st.button(q_beh, use_container_width=True, key="q1"):
        st.session_state["quick_question"] = q_beh

    st.markdown('<div class="question-category-tag">TECHNICAL DEPTH</div>', unsafe_allow_html=True)
    q_tech = "How did you establish your design system to reduce dev time by 30%?"
    if st.button(q_tech, use_container_width=True, key="q2"):
        st.session_state["quick_question"] = q_tech

    st.markdown('<div class="question-category-tag">LEADERSHIP</div>', unsafe_allow_html=True)
    q_lead = "How do you approach mentoring junior designers while managing your own workload?"
    if st.button(q_lead, use_container_width=True, key="q3"):
        st.session_state["quick_question"] = q_lead

    st.markdown('<div class="question-category-tag">IMPACT & METRICS</div>', unsafe_allow_html=True)
    q_imp = "How did you achieve a 24% increase in user retention at Global Tech Solutions?"
    if st.button(q_imp, use_container_width=True, key="q4"):
        st.session_state["quick_question"] = q_imp

    # Match Confidence Score Card
    st.markdown("""
    <div class="confidence-card">
        <div class="confidence-badge">85%</div>
        <div>
            <div style="font-weight:700; font-size:0.85rem;">Score Confidence</div>
            <div style="font-size:0.75rem; color:#94a3b8;">Based on job description match</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div style="text-align:center; margin-top:3rem; padding:1.5rem; color:#94a3b8; font-size:0.8rem; border-top:1px solid {border_color};">
    {CONFIG["app_name"]} &nbsp;•&nbsp; Built by <b>{CONFIG["author"]}</b> &nbsp;•&nbsp; Python • Streamlit • Groq {CONFIG["model_display"]}
</div>
""", unsafe_allow_html=True)
