import streamlit as st
import fitz  # PyMuPDF
import openai

# CONFIGURACIÓN
st.set_page_config(page_title="EvolveYourCV", layout="centered")

st.title("📈 Evolve your CV")
st.markdown("Sube tu currículum y deja que la inteligencia artificial te muestre tu próximo paso profesional.")

# SUBIR ARCHIVO
uploaded_file = st.file_uploader("📄 Sube tu CV (formato PDF)", type=["pdf"])
linkedin_url = st.text_input("🔗 O pega la URL de tu perfil de LinkedIn (opcional)")

# API KEY (configurada en Streamlit Cloud desde secrets)
openai.api_key = st.secrets["OPENAI_API_KEY"]

def extract_text_from_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text.strip()

def get_ai_recommendation(cv_text, linkedin_url=None):
    prompt = f"""
Eres un orientador laboral experto y actualizado. Analiza el siguiente perfil profesional:

CV:
{cv_text}

{f"Perfil de LinkedIn: {linkedin_url}" if linkedin_url else ""}

A partir de la experiencia, estudios y habilidades detectadas, devuelve lo siguiente:
1. Dos trayectorias profesionales posibles y realistas.
2. Puestos a los que podría aspirar pronto si mejora ciertos aspectos.
3. Cursos o formaciones recomendadas (oficiales o informales).
4. Estimación de salario por país o sector.
5. Consejos personalizados para mejorar su empleabilidad y alcanzar el trabajo ideal.

Escribe como un asesor laboral experto, claro y directo.
"""
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # Puedes cambiar a "gpt-4" si tienes acceso
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message["content"]

# PROCESAR ENTRADA
if uploaded_file:
    with st.spinner("🔎 Analizando tu CV..."):
        try:
            text = extract_text_from_pdf(uploaded_file)
            if len(text.strip()) < 100:
                st.warning("El texto extraído del PDF es muy corto. ¿Seguro que es un CV válido?")
            else:
                result = get_ai_recommendation(text, linkedin_url)
                st.success("✅ Análisis completo")
                st.markdown("### 🎯 Recomendación personalizada")
                st.markdown(result)
        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {e}")
elif linkedin_url:
    st.info("⚠️ Por ahora, el análisis de perfiles LinkedIn requiere que subas también el CV para mayor precisión.")
