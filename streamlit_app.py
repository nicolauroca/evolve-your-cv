
import streamlit as st
import fitz  # PyMuPDF
from openai import OpenAI

# PAGE CONFIGURATION
st.set_page_config(page_title="EvolveYourCV", layout="centered")

st.title("📈 EvolveYourCV")
st.markdown(
    "Upload your resume and let artificial intelligence guide your next best career steps. "
    "The analysis is automatic, personalized, and free."
)

# FILE UPLOAD & LINKEDIN INPUT
uploaded_file = st.file_uploader("📄 Upload your CV (PDF format only)", type=["pdf"])
linkedin_url = st.text_input("🔗 Or paste your LinkedIn profile URL (optional)")

# OPENROUTER CLIENT (API key set in Streamlit secrets)
client = OpenAI(
    api_key=st.secrets["OPENROUTER_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

# EXTRACT TEXT FROM PDF
def extract_text_from_pdf(file):
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"Could not read the PDF: {e}")

# REQUEST TO OPENROUTER
def get_ai_recommendation(cv_text, linkedin_url=None):
    cv_text = cv_text[:6000]  # truncate if needed
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
    try:
        response = client.chat.completions.create(
            model="mistral/mistral-7b-instruct:free",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        if hasattr(e, 'status_code') and e.status_code == 429:
            raise RuntimeError(
                "You have reached the free request limit for now. "
                "Please wait a few hours and try again, or check your usage on OpenRouter."
            )
        else:
            raise RuntimeError(f"Could not get a response from the model: {e}")

# MAIN LOGIC
if uploaded_file:
    with st.spinner("🔎 Analyzing your CV..."):
        try:
            text = extract_text_from_pdf(uploaded_file)
            if len(text) < 100:
                st.warning("The extracted text seems too short. Is this a valid resume?")
            else:
                result = get_ai_recommendation(text, linkedin_url)
                st.success("✅ Analysis complete")
                st.markdown("### 🎯 Personalized Career Recommendation")
                st.markdown(result)
        except Exception as e:
            st.error(f"❌ Error: {e}")
elif linkedin_url:
    st.info("⚠️ For best results, please upload your CV in addition to the LinkedIn profile.")
