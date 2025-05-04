
import streamlit as st
import fitz  # PyMuPDF
from openai import OpenAI

# CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="EvolveYourCV", layout="centered")

st.title("📈 EvolveYourCV")
st.markdown(
    "Sube tu currículum y deja que la inteligencia artificial te muestre tu próximo paso profesional. "
    "Todo el análisis es automático, personalizado y gratuito."
)

# SUBIDA DE ARCHIVO Y PERFIL DE LINKEDIN
uploaded_file = st.file_uploader("📄 Sube tu CV (formato PDF)", type=["pdf"])
linkedin_url = st.text_input("🔗 O pega la URL de tu perfil de LinkedIn (opcional)")

# CLIENTE DE OPENAI (usando secrets en Streamlit Cloud)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# FUNCIÓN PARA EXTRAER TEXTO DE PDF
def extract_text_from_pdf(file):
    try:
        doc = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"Error al leer el PDF: {e}")

# FUNCIÓN PRINCIPAL QUE HACE LA LLAMADA A OPENAI
def get_ai_recommendation(cv_text, linkedin_url=None):
    cv_text = cv_text[:6000]  # recortar para evitar límites de tokens
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
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content

# PROCESAMIENTO DE ENTRADA
if uploaded_file:
    with st.spinner("🔎 Analizando tu CV..."):
        try:
            text = extract_text_from_pdf(uploaded_file)
            if len(text) < 100:
                st.warning("El texto extraído del CV es muy corto. ¿Estás seguro de que es un documento válido?")
            else:
                result = get_ai_recommendation(text, linkedin_url)
                st.success("✅ Análisis completo")
                st.markdown("### 🎯 Recomendación personalizada")
                st.markdown(result)
        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {e}")
elif linkedin_url:
    st.info("⚠️ Por ahora, el análisis de LinkedIn requiere que subas también el CV para obtener mejores resultados.")
