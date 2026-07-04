# 🤖 AI Interview Assistant

An AI-powered interview assistant that simulates a job candidate by answering interview questions based on information extracted from an uploaded PDF resume.

Built by **Jai Prakash Shettigar**

---

## 🌐 Live Demo
👉 [Try it here](https://your-app-name.streamlit.app) ← update after deployment

---

## ✨ Features

- 📄 **PDF Resume Upload** — Upload any PDF resume instantly
- 👤 **Auto Resume Parsing** — Extracts name, email, phone and skills automatically
- 📝 **Resume Summary** — Shows first meaningful lines of resume after upload
- 📊 **Resume Info** — Shows filename, page count and character count
- 💬 **AI Interview Simulation** — Answers questions as the candidate in first person
- 💡 **Smart Questions** — Suggests questions based on YOUR resume content
- 🔄 **Reset Conversation** — Start fresh anytime
- 💾 **Download Chat** — Save full interview conversation as .txt file
- ⚠️ **AI Disclaimer** — Reminds users responses are AI generated
- 🎨 **Clean UI** — Sidebar layout with dark theme
- 📱 **Responsive** — Works on mobile and desktop
- ⚙️ **Config Driven** — Change AI model in one place, updates everywhere

---

## 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Web UI framework |
| Groq API | LLM inference engine |
| LLaMA 3.3 70B | AI language model |
| PyPDF2 | PDF text extraction |
| python-dotenv | Environment variable management |

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/jaiprakashshettigar35-rgb/AI-Interview-Assistant.git
cd AI-Interview-Assistant
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate.bat

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create .env file
```bash
# Create a .env file and add your Groq API key
GROQ_API_KEY=your_groq_api_key_here
```

### 5. Run the app
```bash
streamlit run interview_assistant.py
```

### 6. Open browser
```
http://localhost:8501
```

---

## 🔑 Getting Free Groq API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up for free account
3. Go to API Keys section
4. Create new key
5. Copy and paste into your `.env` file

---

## 📁 Project Structure

```
AI-Interview-Assistant/
│
├── interview_assistant.py  ← Main application
├── requirements.txt        ← Python dependencies
├── README.md              ← Project documentation
├── .gitignore             ← Ignores .env and venv
└── .env                   ← API keys (never share!)
```

---

## 🚀 How to Use

```
1️⃣  Upload your PDF resume from the sidebar
         ↓
2️⃣  View auto-extracted details (name, skills, summary)
         ↓
3️⃣  Pick a suggested question or type your own
         ↓
4️⃣  Get AI response as the candidate
         ↓
5️⃣  Download the conversation when done!
```

---

## ⚙️ Configuration

All settings are in one place at the top of `interview_assistant.py`:

```python
CONFIG = {
    "model": "llama-3.3-70b-versatile",  # Change model here
    "model_display": "LLaMA 3.3 70B",    # Updates footer automatically
    "max_tokens": 500,
    "temperature": 0.7,
    "app_name": "AI Interview Assistant",
    "author": "Jai Prakash Shettigar"
}
```

---

## ⚠️ Disclaimer

AI responses are generated from the uploaded resume and may not perfectly reflect real-world experience. This tool is intended for interview practice purposes only.

---

## 🌐 Deploy on Streamlit Cloud

1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Click "New app"
5. Select this repository
6. Set main file: `interview_assistant.py`
7. Add secret: `GROQ_API_KEY = your_key`
8. Click Deploy!

---

## 👨‍💻 Author

**Jai Prakash Shettigar**
- LinkedIn: [linkedin.com/in/jai-prakash-964a81b8](https://linkedin.com/in/jai-prakash-964a81b8)
- Email: jaiprakashshettigar35@gmail.com

---

## 📄 License

This project is open source and available under the MIT License.
