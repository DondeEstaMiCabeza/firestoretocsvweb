
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import json
import io

st.title("Exportador Firestore a Excel")

uploaded_json = st.file_uploader("Sube tu archivo survey.json con credenciales", type="json")

if uploaded_json is not None:
    data = json.load(uploaded_json)
    project_id = data.get("project_id")

    # Mostrar project ID
    st.info(f"Proyecto: {project_id}")

    # Iniciar Firebase
    if not firebase_admin._apps:
        cred = credentials.Certificate(data)
        firebase_admin.initialize_app(cred)

    db = firestore.client()

    coleccion = st.text_input("Nombre de la colección", value="respuestas")

    if st.button("Exportar"):
        docs = db.collection(coleccion).stream()
        registros = []

        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id
            registros.append(data)

        if registros:
            df = pd.DataFrame(registros)

            if project_id == "dondeestamicabezaserver-dad3dcfe5244":
                reemplazos = {
                    "SiTePasaAlgoBuenoAQuienLeCuentasPrimero": "¿Si te pasa algo bueno, a quién se lo cuentas primero?",
                    "FrecuenciaPedirConsejo": "¿Con qué frecuencia pides consejo cuando tienes un problema?",
                    "CuandoMeEnfrentoALosProblemas": "Cuando me enfrento a los problemas...",
                    "Raza": "¿Cómo te identificas?",
                    "QueTeMantieneConVida": "¿Qué te mantiene con vida?",
                    "TeHazSentidoActivxYEnergicx": "Durante las últimas dos semanas, ¿te has sentido activx y llenx de energía?",
                    "Donde_Vives": "¿Dónde vives?",
                    "YSiTePasaAlgoMalo": "¿Y si te pasa algo malo?",
                    "ConQueTeDiviertes": "¿Con qué te diviertes?",
                    "DespuesDeLaTormentaMeSiento": "Después de la tormenta me siento...",
                    "TeHazDespertadoFrescxYDescansadx": "Durante las últimas dos semanas, ¿te has despertado frescx y descansadx?",
                    "TuEn10Años": "¿Cómo te imaginas en 10 años?",
                    "CuandoVeoAlguienEnProblemas": "Cuando veo a alguien con problemas...",
                    "PanaInfluencer": "Si tuvieras un pana influencer, ¿qué debería hacer?",
                    "Generos": "¿Qué géneros consumes?",
                    "QueTeGustariaHacer": "¿Qué te gustaría hacer?",
                    "TeHazSentidoTranquilxYRelajadx": "Durante las últimas dos semanas, ¿te has sentido tranquilx y relajadx?",
                    "FrecuenciaLograrObjetivos": "¿Con qué frecuencia logras tus objetivos?",
                    "ActividadActual": "¿Cuál es tu actividad principal actual?",
                    "TeAdaptadasALosCambios": "¿Qué tan fácil te adaptas a los cambios?",
                    "TeHazSentidoAlegreYDeBuenHumor": "Durante las últimas dos semanas, ¿te has sentido alegre y de buen humor?",
                    "CualidadesDelInfluencer": "¿Qué cualidades debería tener un influencer que te represente?",
                    "Edad": "¿Cuál es tu edad?",
                    "QueEsLoPeorDeTuTrabajoOEstudio": "¿Qué es lo peor de tu trabajo o tus estudios?",
                    "TuVidaCotiadianaHaEstadoLlenaDeCosasQueMeInteresen": "Mi vida cotidiana ha estado llena de cosas que me interesen.",
                    "CuandoEstasDiscutiendo": "Cuando estás discutiendo...",
                    "DondeTeSientesMejor": "¿Dónde te sientes mejor?"
                }
                df.rename(columns=reemplazos, inplace=True)
                if "id" in df.columns:
                    df.drop(columns=["id"], inplace=True)

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
                df.to_excel(writer, index=False, sheet_name="Export")
                writer.save()
            st.success("¡Exportación completada!")
            st.download_button("Descargar Excel", buffer.getvalue(), file_name="export.xlsx")
