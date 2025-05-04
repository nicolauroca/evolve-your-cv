
import streamlit as st
import fitz  # PyMuPDF
from openai import OpenAI

# PAGE CONFIG
st.set_page_config(page_title="EvolveYourCV", layout="centered")

st.title("📈 EvolveYourCV")
st.markdown(
    "Upload your resume and let artificial intelligence guide your next best career steps. "
    "The analysis is automatic, personalized, and free."
)

# FILE UPLOAD & LINKEDIN INPUT
uploaded_file = st.file_uploader("📄 Upload your CV (PDF format only)", type=["pdf"])
linkedin_url = st.text_input("🔗 Or paste your LinkedIn profile URL (optional)")

# OPENROUTER CLIENT
client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

# FREE MODELS LIST (in priority order)
FREE_MODELS = [
    "mistralai/mistral-7b-instruct:free",
    "openchat/openchat-7b:free",
    "gryphe/mythomax-l2-13b:free",
    "undi95/toppy-m-7b:free",
    "thebloke/zephyr-7b-beta-GGUF:free"
]

# PDF TEXT EXTRACTION
def extract_text_from_pdf(file):
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"Could not read the PDF: {e}")

# MODEL FALLBACK LOGIC
def get_ai_recommendation(cv_text, linkedin_url=None):
    cv_text = cv_text[:6000]  # truncate to stay under token limits
    prompt = f"""
You are a professional and up-to-date career advisor. Analyze the following profile:

Resume:
{cv_text}

{f"LinkedIn profile: {linkedin_url}" if linkedin_url else ""}

Provide the following:
1. Two realistic and meaningful career paths.
2. Job roles the person could reach soon with some improvements.
3. Recommended training or courses (formal or informal).
4. Estimated salary ranges based on country or sector.
5. Personalized tips to improve their employability and get closer to their dream job.

Write clearly, professionally, and as a top-tier career expert.
"""
    last_error = None
    for model in FREE_MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return response.choices[0].message.content, model
        except Exception as e:
            if hasattr(e, 'status_code') and e.status_code == 429:
                last_error = e  # quota exceeded, try next model
            elif hasattr(e, 'status_code') and e.status_code == 400:
                continue  # invalid model, skip
            else:
                last_error = e
                break
    if last_error:
        raise RuntimeError(f"All free models failed or quota was exceeded. Last error: {last_error}")
    else:
        raise RuntimeError("No models available or reachable at the moment.")

# MAIN APP FLOW
if uploaded_file:
    with st.spinner("🔎 Analyzing your CV..."):
        try:
            text = extract_text_from_pdf(uploaded_file)
            if len(text) < 100:
                st.warning("The extracted text seems too short. Is this a valid resume?")
            else:
                result, model_used = get_ai_recommendation(text, linkedin_url)
                st.success("✅ Analysis complete")
                st.markdown(f"### 🎯 Personalized Career Recommendation")
                st.markdown(f"🧠 *Model used: `{model_used}`*")
                st.markdown(result)
        except Exception as e:
            st.error(f"❌ Error: {e}")
elif linkedin_url:
    st.info("⚠️ For best results, please upload your CV in addition to the LinkedIn profile.")
