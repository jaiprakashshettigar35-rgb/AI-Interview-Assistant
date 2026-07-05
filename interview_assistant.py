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
# Configuration (change model here only!)
# ─────────────────────────────────────────
CONFIG = {
    "model": "llama-3.3-70b-versatile",
    "model_display": "LLaMA 3.3 70B",
    "max_tokens": 500,
    "temperature": 0.7,
    "app_name": "AI Interview Assistant",
    "author": "Jai Prakash Shettigar"
}

# ─────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────
st.set_page_config(
    page_title=CONFIG["app_name"],
    page_icon="🤖",
    layout="wide"
)

# ─────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #333;
        margin-bottom: 0.5rem;
    }
    .powered-by {
        text-align: center;
        color: #888;
        font-size: 0.8rem;
        margin-bottom: 1.5rem;
    }
    .workflow-box {
        background: #1a1a2e;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        margin: 10px 5px;
        border: 1px solid #333;
    }
    .resume-info-box {
        background: #1a1a2e;
        border-left: 4px solid #7c3aed;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        font-size: 0.9rem;
    }
    .skill-badge {
        display: inline-block;
        background: #7c3aed;
        color: white;
        padding: 3px 10px;
        border-radius: 20px;
        margin: 3px;
        font-size: 0.75rem;
    }
    .disclaimer-box {
        background: #2a1a1a;
        border-left: 4px solid #f59e0b;
        border-radius: 8px;
        padding: 10px 14px;
        margin: 10px 0;
        font-size: 0.8rem;
        color: #f59e0b;
    }
    .summary-box {
        background: #1a2a1a;
        border-left: 4px solid #10b981;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        font-size: 0.85rem;
        color: #d1fae5;
    }
    .footer {
        text-align: center;
        padding: 20px;
        color: #888;
        font-size: 0.8rem;
        border-top: 1px solid #333;
        margin-top: 30px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# Initialize Groq
# ─────────────────────────────────────────
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ─────────────────────────────────────────
# Helper: Extract resume text safely
# ─────────────────────────────────────────
def extract_resume_text(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    resume_text = ""
    page_count = len(reader.pages)
    for page in reader.pages:
        text = page.extract_text()
        if text:
            resume_text += text + "\n"
    return resume_text, page_count

# ─────────────────────────────────────────
# Helper: Parse resume details
# ─────────────────────────────────────────
def parse_resume_details(text, filename):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    name = lines[0] if lines else "Not found"

    # Full email
    email_match = re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z]+', text)
    email = email_match.group(0) if email_match else "Not found"

    phone_match = re.search(r'[\+]?[\d\s\-\(\)]{10,}', text)
    phone = phone_match.group(0).strip() if phone_match else "Not found"

    skill_keywords = [
        "Python", "SQL", "Excel", "Power BI", "Salesforce", "Machine Learning",
        "Data Analysis", "Leadership", "Management", "Logistics", "Compliance",
        "Groq", "Streamlit", "Communication", "Automation", "Tableau", "Java",
        "JavaScript", "React", "Django", "FastAPI", "AWS", "Azure", "Docker"
    ]
    skills = [s for s in skill_keywords if s.lower() in text.lower()]

    # Resume summary = first 3 meaningful lines
    summary_lines = [l for l in lines if len(l) > 40][:3]
    summary = " ".join(summary_lines)

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills[:12],
        "filename": filename,
        "summary": summary
    }

# ─────────────────────────────────────────
# Helper: Generate smart questions
# ─────────────────────────────────────────
def generate_smart_questions(resume_text):
    generic = [
        "Tell me about yourself.",
        "What are your key skills?",
        "Why should we hire you?",
        "What is your greatest strength?",
        "Where do you see yourself in 5 years?",
        "Describe a challenge you overcame."
    ]
    smart = []
    if "python" in resume_text.lower():
        smart.append("Tell me about your Python experience.")
    if "sql" in resume_text.lower():
        smart.append("How have you used SQL in your work?")
    if "machine learning" in resume_text.lower():
        smart.append("Describe your machine learning experience.")
    if "team" in resume_text.lower():
        smart.append("Tell me about your team leadership experience.")
    if "project" in resume_text.lower():
        smart.append("Describe your most impactful project.")
    if "logistics" in resume_text.lower():
        smart.append("How did you optimize logistics operations?")
    if "data" in resume_text.lower():
        smart.append("How have you used data to drive decisions?")
    if "power bi" in resume_text.lower():
        smart.append("How have you used Power BI in your work?")

    all_questions = smart + [q for q in generic if q not in smart]
    return all_questions[:8]

# ─────────────────────────────────────────
# Helper: Download chat as text
# ─────────────────────────────────────────
def generate_chat_download(messages, candidate_name):
    lines = [
        f"AI Interview Assistant - Chat Export",
        f"Candidate: {candidate_name}",
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"Model: {CONFIG['model_display']}",
        "=" * 50,
        ""
    ]
    for msg in messages:
        role = "Interviewer" if msg["role"] == "user" else "Candidate (AI)"
        lines.append(f"{role}:\n{msg['content']}\n")
        lines.append("-" * 40)
    return "\n".join(lines)

# ─────────────────────────────────────────
# Header
# ─────────────────────────────────────────
st.markdown(f'<div class="main-header"><h1>🤖 {CONFIG["app_name"]}</h1></div>', unsafe_allow_html=True)
st.markdown(f'<div class="powered-by">Powered by Groq • {CONFIG["model_display"]} • Built with Streamlit</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📄 Resume Upload")
    pdf_file = st.file_uploader("Upload PDF Resume", type=["pdf"])

    if pdf_file:
        resume_text, page_count = extract_resume_text(pdf_file)
        char_count = len(resume_text)
        st.session_state["resume_text"] = resume_text
        details = parse_resume_details(resume_text, pdf_file.name)
        st.session_state["details"] = details
        st.session_state["smart_questions"] = generate_smart_questions(resume_text)
        st.success("✅ Resume Loaded!")

        # Resume file info
        st.markdown(f"""
        <div class="resume-info-box">
            <b>📄 File:</b> {pdf_file.name}<br>
            <b>📑 Pages:</b> {page_count}<br>
            <b>🔤 Characters:</b> {char_count:,}
        </div>
        """, unsafe_allow_html=True)

        # Resume summary
        if details["summary"]:
            st.markdown("### 📝 Resume Summary")
            st.markdown(f'<div class="summary-box">{details["summary"]}</div>', unsafe_allow_html=True)

        st.markdown("### 👤 Candidate")
        st.markdown(f"**Name:** {details['name']}")
        st.markdown(f"**Email:** {details['email']}")   # Full email now!
        st.markdown(f"**Phone:** {details['phone']}")

        if details["skills"]:
            st.markdown("### 🛠️ Skills Detected")
            skills_html = " ".join([f'<span class="skill-badge">{s}</span>' for s in details["skills"]])
            st.markdown(f'<div>{skills_html}</div>', unsafe_allow_html=True)

    st.markdown("---")

    # Smart or generic questions
    if "smart_questions" in st.session_state:
        st.markdown("### 💡 Suggested Questions")
        for q in st.session_state["smart_questions"]:
            if st.button(q, use_container_width=True):
                st.session_state["quick_question"] = q
    else:
        st.markdown("### 💡 Sample Questions")
        for q in ["Tell me about yourself.", "What are your key skills?", "Why should we hire you?"]:
            if st.button(q, use_container_width=True):
                st.session_state["quick_question"] = q

    st.markdown("---")

    # Reset button
    if st.button("🔄 Reset Conversation", use_container_width=True, type="primary"):
        st.session_state["messages"] = []
        st.rerun()

    # Download chat button
    if "messages" in st.session_state and len(st.session_state["messages"]) > 0:
        candidate_name = st.session_state.get("details", {}).get("name", "Candidate")
        chat_text = generate_chat_download(st.session_state["messages"], candidate_name)
        st.download_button(
            label="💾 Download Chat",
            data=chat_text,
            file_name=f"interview_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )

    # Disclaimer
    st.markdown("""
    <div class="disclaimer-box">
        ⚠️ <b>Disclaimer:</b> AI responses are generated from the uploaded resume and may not perfectly reflect real-world experience. Use as a practice tool only.
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# MAIN CHAT AREA
# ─────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "resume_text" not in st.session_state:
    # Welcome screen
    st.markdown("### 👋 Welcome! Here's how it works:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="workflow-box">
            <div style="font-size:2rem">1️⃣</div>
            <h3>Upload Resume</h3>
            <p>Upload your PDF resume from the sidebar on the left</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="workflow-box">
            <div style="font-size:2rem">2️⃣</div>
            <h3>Ask Questions</h3>
            <p>Type interview questions or pick from suggested ones</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="workflow-box">
            <div style="font-size:2rem">3️⃣</div>
            <h3>Get AI Responses</h3>
            <p>AI answers as you, based only on your resume!</p>
        </div>
        """, unsafe_allow_html=True)
    st.info("👈 Start by uploading your PDF resume from the sidebar!")

else:
    # Display chat history
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Handle quick question
    question = st.session_state.pop("quick_question", None)
    user_input = st.chat_input("Ask an interview question...")
    if user_input:
        question = user_input

    if question:
        st.session_state["messages"].append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        system_prompt = f"""You are the owner of this resume being interviewed for a job.
Answer all questions based ONLY on the resume provided.
Speak in first person naturally and confidently.
Never invent or assume experience not in the resume.
If the resume doesn't contain the answer, clearly say you don't have that information.
Keep answers professional, concise and impactful (3-5 sentences).

RESUME:
{st.session_state['resume_text']}"""

        messages = [{"role": "system", "content": system_prompt}]
        for msg in st.session_state["messages"]:
            messages.append({"role": msg["role"], "content": msg["content"]})

        with st.chat_message("assistant"):
            with st.spinner("🤖 Analyzing resume and generating answer..."):
                response = client.chat.completions.create(
                    model=CONFIG["model"],
                    messages=messages,
                    max_tokens=CONFIG["max_tokens"],
                    temperature=CONFIG["temperature"]
                )
                answer = response.choices[0].message.content
                st.write(answer)

        st.session_state["messages"].append({"role": "assistant", "content": answer})

# ─────────────────────────────────────────
# Footer
# ─────────────────────────────────────────
st.markdown(f"""
<div class="footer">
    Built by <b>{CONFIG["author"]}</b> &nbsp;|&nbsp;
    Python • Streamlit • Groq API • {CONFIG["model_display"]}
</div>
""", unsafe_allow_html=True)