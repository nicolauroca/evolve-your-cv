
import streamlit as st
import fitz  # PyMuPDF
from openai import OpenAI

# PAGE CONFIGURATION
st.set_page_config(page_title="EvolveYourCV", layout="centered")

st.title("📈 EvolveYourCV")

# LANGUAGE SELECTION
language = st.selectbox("🌍 Choose your language / Elige tu idioma", ["English", "Español"])

# TEXTS
texts = {
    "English": {
        "intro": "Upload your resume and let AI guide your next best career steps.",
        "upload": "📄 Upload your CV (PDF only)",
        "linkedin": "🔗 Or paste your LinkedIn profile URL (optional)",
        "growth": "What kind of growth are you looking for?",
        "growth_options": ["Horizontal (explore new areas)", "Vertical (go deeper in your field)"],
        "analyzing": "🔎 Analyzing your CV...",
        "short": "The extracted text seems too short. Is this a valid resume?",
        "complete": "✅ Analysis complete",
        "recommendation": "### 🎯 Personalized Career Recommendation",
        "model": "🧠 *Model used:*",
        "only_linkedin": "⚠️ For best results, please upload your CV as well.",
        "error": "❌ Error:",
    },
    "Español": {
        "intro": "Sube tu currículum y deja que la IA te oriente en tu próximo paso profesional.",
        "upload": "📄 Sube tu CV (solo PDF)",
        "linkedin": "🔗 O pega la URL de tu perfil de LinkedIn (opcional)",
        "growth": "¿Qué tipo de crecimiento estás buscando?",
        "growth_options": ["Horizontal (explorar nuevas áreas)", "Vertical (profundizar en tu campo)"],
        "analyzing": "🔎 Analizando tu CV...",
        "short": "El texto extraído es muy corto. ¿Es un CV válido?",
        "complete": "✅ Análisis completado",
        "recommendation": "### 🎯 Recomendación profesional personalizada",
        "model": "🧠 *Modelo utilizado:*",
        "only_linkedin": "⚠️ Para mejores resultados, sube también tu currículum.",
        "error": "❌ Error:",
    }
}

# SHOW UI
st.markdown(texts[language]["intro"])
uploaded_file = st.file_uploader(texts[language]["upload"], type=["pdf"])
linkedin_url = st.text_input(texts[language]["linkedin"])
growth_choice = st.radio(texts[language]["growth"], texts[language]["growth_options"])

# OPENROUTER CLIENT
client = OpenAI(api_key=st.secrets["OPENROUTER_API_KEY"], base_url="https://openrouter.ai/api/v1")

# FREE MODELS LIST
FREE_MODELS = [
    "mistralai/mistral-7b-instruct:free",
    "openchat/openchat-7b:free",
    "gryphe/mythomax-l2-13b:free",
    "undi95/toppy-m-7b:free",
    "thebloke/zephyr-7b-beta-GGUF:free"
]

# PDF TEXT EXTRACTION
def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "".join([page.get_text() for page in doc]).strip()

# AI RESPONSE FUNCTION
def get_ai_recommendation(cv_text=None, linkedin_url=None):
    tone = {
        "English": "friendly and professional, speaking directly to the user using 'you'",
        "Español": "profesional pero cercano, dirigiéndote al usuario de tú"
    }[language]

    focus = {
        "English": {
            "Horizontal": "horizontal growth: explore new paths or roles related to your profile",
            "Vertical": "vertical growth: advance in your current area or role"
        },
        "Español": {
            "Horizontal": "crecimiento horizontal: explorar nuevos caminos o roles relacionados con tu perfil",
            "Vertical": "crecimiento vertical: avanzar en tu área o rol actual"
        }
    }[language]["Horizontal" if "Horizontal" in growth_choice else "Vertical"]

    prompt = f'''
You are an experienced career advisor. Be {tone}.
Focus on {focus}.
Use recent and updated information.

Read, analyze and understand the following profile:

{f"LinkedIn: {linkedin_url}" if linkedin_url else ""}

{f"Resume: {cv_text}" if cv_text else ""}

Return, as an expert on all the jobs and careers showed on the profile, this information:
1. Two possible and realistic career paths.
3. Two roles they could aim for soon with some improvement.
4. Recommended training or courses of each role (formal or informal).
5. Estimated salary ranges for each role (based on location or industry).
6. Personalized advice to grow professionally according to the recommended roles.

Answer in {language}.
Answer with good formatting for understanding all the information.
'''

    for model in FREE_MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            return response.choices[0].message.content, model
        except Exception as e:
            if hasattr(e, 'status_code') and e.status_code in [400, 429]:
                continue
            else:
                raise RuntimeError(f"{texts[language]['error']} {e}")
    raise RuntimeError("All models failed or quota exceeded.")

# MAIN EXECUTION
if uploaded_file > '' or linkedin_url > '':
    with st.spinner(texts[language]["analyzing"]):
        try:
            if uploaded_file:
                cv_text = extract_text_from_pdf(uploaded_file)
                if len(cv_text) < 100:
                    st.warning(texts[language]["short"])
                result, model_used = get_ai_recommendation(cv_text, linkedin_url)
                st.success(texts[language]["complete"])
                st.markdown(texts[language]["recommendation"])
                st.markdown(f"{texts[language]['model']} `{model_used}`")
                st.markdown(result)
        except Exception as e:
            st.error(f"{texts[language]['error']} {e}")
