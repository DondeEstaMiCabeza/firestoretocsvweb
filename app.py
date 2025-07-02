import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from io import BytesIO
import json

st.set_page_config(page_title="Exportador Firestore a Excel")

st.title("Exportador Firestore a Excel")
st.markdown("Sube tu archivo JSON con credenciales")

# Cargar archivo JSON
json_file = st.file_uploader("Elige el archivo JSON", type="json")

project_id_input = st.text_input("Proyecto:", placeholder="ej. midatabase")
collection_name = st.text_input("Nombre de la colección", value="respuestas")

if json_file and project_id_input and collection_name:
    json_bytes = json_file.read()
    json_dict = json.loads(json_bytes)

    # Validación del proyecto
    if json_dict.get("project_id") != project_id_input:
        st.error("El project_id del JSON no coincide con el ingresado.")
        st.stop()

    # Inicializar Firebase
    if not firebase_admin._apps:
        cred = credentials.Certificate(json_dict)
        firebase_admin.initialize_app(cred)

    db = firestore.client()

    # Obtener documentos de la colección
    docs = db.collection(collection_name).stream()
    data = [doc.to_dict() for doc in docs]

    if not data:
        st.warning("La colección está vacía.")
        st.stop()

    df = pd.DataFrame(data)

    # Renombrar columnas si es el proyecto especificado
    if project_id_input == "dondeestamicabezaserver":
        replacements = {
            "¿Si te pasa algo bueno, a quién se lo cuentas primero?": "SiTePasaAlgoBuenoAQuienLeCuentasPrimero",
            "¿Con qué frecuencia pides consejo cuando tienes un problema?": "FrecuenciaPedirConsejo",
            "Cuando me enfrento a los problemas tiendo a...": "CuandoMeEnfrentoALosProblemas",
            "¿Con qué raza te identificas más?": "Raza",
            "¿Qué te mantiene con vida en los días difíciles?": "QueTeMantieneConVida",
            "¿Te has sentido activx y energicx últimamente?": "TeHazSentidoActivxYEnergicx",
            "¿Dónde vives?": "Donde_Vives",
            "¿Y si te pasa algo malo, a quién se lo cuentas primero?": "YSiTePasaAlgoMalo",
            "¿Con qué te diviertes últimamente?": "ConQueTeDiviertes",
            "Después de la tormenta me siento...": "DespuesDeLaTormentaMeSiento",
            "¿Te has despertado frescx y descansadx últimamente?": "TeHazDespertadoFrescxYDescansadx",
            "¿Cómo te imaginas en 10 años?": "TuEn10Años",
            "Cuando veo a alguien con problemas tiendo a...": "CuandoVeoAlguienEnProblemas",
            "¿Qué características tendría un pana influencer que sigas?": "PanaInfluencer",
            "¿Qué género(s) consumes más?": "Generos",
            "¿Qué te gustaría hacer si el dinero no fuera un problema?": "QueTeGustariaHacer",
            "¿Te has sentido tranquilx y relajadx últimamente?": "TeHazSentidoTranquilxYRelajadx",
            "¿Con qué frecuencia logras tus objetivos personales?": "FrecuenciaLograrObjetivos",
            "¿Qué estás haciendo actualmente (trabajo, estudio, etc.)?": "ActividadActual",
            "¿Te adaptas con facilidad a los cambios?": "TeAdaptadasALosCambios",
            "¿Te has sentido alegre y de buen humor últimamente?": "TeHazSentidoAlegreYDeBuenHumor",
            "¿Qué cualidades debe tener un influencer que sigas?": "CualidadesDelInfluencer",
            "¿Qué edad tienes?": "Edad",
            "¿Qué es lo peor de tu trabajo o estudios actualmente?": "QueEsLoPeorDeTuTrabajoOEstudio",
            "Mi vida cotidiana ha estado llena de cosas que me interesen": "TuVidaCotiadianaHaEstadoLlenaDeCosasQueMeInteresen",
            "Cuando estás discutiendo con alguien sueles...": "CuandoEstasDiscutiendo",
            "¿Dónde te sientes mejor?": "DondeTeSientesMejor"
        }

        df.rename(columns=replacements, inplace=True)
        if "id" in df.columns:
            del df["id"]

    st.success("Datos cargados correctamente. Vista previa:")
    st.dataframe(df.head())

    # Descargar como Excel
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="respuestas")

    st.download_button(
        label="📥 Descargar Excel",
        data=output.getvalue(),
        file_name="respuestas_exportadas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
