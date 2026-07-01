import gradio as gr
import os

from dotenv import load_dotenv
from openai import OpenAI
from resume_reader import load_resume

# ============================
# Load Environment Variables
# ============================
load_dotenv(".env")

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

# ============================
# Load Resume
# ============================
resume = load_resume()

print("✅ Resume loaded!")
print("Characters:", len(resume))
print("✅ Groq API Key loaded!")

# ============================
# AI Candidate Function
# ============================
def candidate(message, history):

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": f"""
You are Jai Prakash.

This resume belongs to you.

Resume:
{resume}

You are attending a real job interview.

Rules:

1. Always answer in FIRST PERSON.
   Example:
   "I have worked..."
   "My strength is..."

2. Never say:
   - "According to the resume"
   - "The resume states"
   - "The candidate"
   - "The resume mentions"

3. Never say you are an AI.

4. Never ask anyone to update or improve the resume.

5. Behave exactly like Jai Prakash sitting in an interview.

6. Give professional interview answers.

7. If something is NOT mentioned in the resume, simply say:
"I don't have that information in my resume."

8. Keep answers confident, natural and concise.

9. Never make up fake experience.

10. Always sound like a human candidate.
"""
            },
            {
                "role": "user",
                "content": message
            }
        ]
    )

    return response.choices[0].message.content


# ============================
# Gradio Chat Interface
# ============================
demo = gr.ChatInterface(
    fn=candidate,
    title="🤖 AI Interview Candidate",
    description="Ask interview questions and the AI will answer as Jai Prakash."
)

# ============================
# Launch App
# ============================
demo.launch()