
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
from io import BytesIO
import zipfile
import tempfile

# Cargar archivo de credenciales
uploaded_file = st.file_uploader("Sube tu archivo JSON con credenciales", type="json")
if uploaded_file is not None:
    data = json.load(uploaded_file)
    project_id = data.get("project_id", "")

    # Inicializar Firebase
    if not firebase_admin._apps:
        cred = credentials.Certificate(data)
        firebase_admin.initialize_app(cred)

    db = firestore.client()

    # Inputs de usuario
    collection_name = st.text_input("Nombre de la colección", value="respuestas")

    if st.button("Exportar"):
        # Leer datos de Firestore
        docs = db.collection(collection_name).stream()
        records = [doc.to_dict() for doc in docs]

        if records:
            df = pd.DataFrame(records)

            if project_id == "dondeestamicabezaserver":
                replacement_map = {
                    "Si te pasa algo bueno, ¿a quién le cuentas primero?": "SiTePasaAlgoBuenoAQuienLeCuentasPrimero",
                    "¿Con qué frecuencia pides consejo a tus amigos o familia?": "FrecuenciaPedirConsejo",
                    "Cuando me enfrento a los problemas, yo...": "CuandoMeEnfrentoALosProblemas",
                    "¿Cómo te identificas racialmente?": "Raza",
                    "¿Qué te mantiene con vida?": "QueTeMantieneConVida",
                    "¿Te has sentido activx y energicx durante las últimas 2 semanas?": "TeHazSentidoActivxYEnergicx",
                    "¿Dónde vives actualmente?": "Donde_Vives",
                    "¿Y si te pasa algo malo?": "YSiTePasaAlgoMalo",
                    "¿Con qué te diviertes más últimamente?": "ConQueTeDiviertes",
                    "Después de la tormenta me siento...": "DespuesDeLaTormentaMeSiento",
                    "¿Te has despertado frescx y descansadx últimamente?": "TeHazDespertadoFrescxYDescansadx",
                    "¿Cómo te imaginas en 10 años?": "TuEn10Años",
                    "Cuando veo a alguien en problemas yo...": "CuandoVeoAlguienEnProblemas",
                    "¿Quién es tu pana influencer?": "PanaInfluencer",
                    "¿Qué te gustaría hacer si el dinero no fuera un problema?": "QueTeGustariaHacer",
                    "¿Con qué géneros te identificas?": "Generos",
                    "¿Te has sentido tranquilx y relajadx últimamente?": "TeHazSentidoTranquilxYRelajadx",
                    "¿Con qué frecuencia logras tus objetivos personales?": "FrecuenciaLograrObjetivos",
                    "¿Cuál es tu actividad actual?": "ActividadActual",
                    "¿Te adaptas fácilmente a los cambios?": "TeAdaptadasALosCambios",
                    "¿Te has sentido alegre y de buen humor últimamente?": "TeHazSentidoAlegreYDeBuenHumor",
                    "¿Qué cualidades tiene tu influencer favorito?": "CualidadesDelInfluencer",
                    "¿Cuál es tu edad?": "Edad",
                    "¿Qué es lo peor de tu trabajo o estudio?": "QueEsLoPeorDeTuTrabajoOEstudio",
                    "Mi vida cotidiana ha estado llena de cosas que me interesen.": "TuVidaCotiadianaHaEstadoLlenaDeCosasQueMeInteresen",
                    "Cuando estás discutiendo con alguien tú...": "CuandoEstasDiscutiendo",
                    "¿Dónde te sientes mejor?": "DondeTeSientesMejor"
                }

                df.rename(columns=replacement_map, inplace=True)
                if "id" in df.columns:
                    df.drop(columns=["id"], inplace=True)

            # Mostrar previsualización
            st.success("Datos cargados y transformados correctamente. Vista previa:")
            st.dataframe(df.head())

            # Exportar a Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Datos")
            st.download_button("Descargar Excel", output.getvalue(), "respuestas.xlsx")
        else:
            st.warning("No se encontraron documentos en esa colección.")
