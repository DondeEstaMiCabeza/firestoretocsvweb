
import streamlit as st
import pandas as pd
import json
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

st.set_page_config(page_title="Firestore to CSV", layout="centered")

st.title("Descarga tu colección de Firestore como CSV")

uploaded_file = st.file_uploader("Sube tu archivo JSON con credenciales", type="json")

if uploaded_file:
    try:
        creds = json.load(uploaded_file)
        firebase_admin.initialize_app(credentials.Certificate(creds))
        db = firestore.client()

        proyecto = creds.get("project_id", "")

        collection_name = st.text_input("Nombre de la colección en Firestore")

        if collection_name:
            docs = db.collection(collection_name).stream()
            data = []

            for doc in docs:
                entry = doc.to_dict()
                entry["id"] = doc.id
                data.append(entry)

            df = pd.DataFrame(data)

            if proyecto == "dondeestamicabezaserver":
                if "id" in df.columns:
                    df.drop(columns=["id"], inplace=True)

                renames = {
                    "ActividadActual": "¿Cuál es tu actividad actual?",
                    "ConQueTeDiviertes": "¿Con qué te diviertes?",
                    "CualidadesDelInfluencer": "¿Qué cualidades valoras en un influencer?",
                    "CuandoEstasDiscutiendo": "¿Qué haces cuando estás discutiendo?",
                    "CuandoMeEnfrentoALosProblemas": "¿Qué haces cuando enfrentas un problema?",
                    "CuandoVeoAlguienEnProblemas": "¿Qué haces si ves a alguien con problemas?",
                    "DespuesDeLaTormentaMeSiento": "Después de una tormenta, ¿cómo te sientes?",
                    "DondeTeSientesMejor": "¿Dónde te sientes mejor?",
                    "Donde_Vives": "¿Dónde vives?",
                    "Edad": "¿Cuál es tu edad?",
                    "FrecuenciaLograrObjetivos": "¿Con qué frecuencia logras tus objetivos?",
                    "FrecuenciaPedirConsejo": "¿Con qué frecuencia pides consejo?",
                    "Generos": "¿Con qué género te identificas?",
                    "PanaInfluencer": "¿Tu pana influencer es?",
                    "QueEsLoPeorDeTuTrabajoOEstudio": "¿Qué es lo peor de tu trabajo o estudio?",
                    "QueTeGustariaHacer": "¿Qué te gustaría hacer?",
                    "QueTeMantieneConVida": "¿Qué te mantiene con vida?",
                    "Raza": "¿Con qué raza o etnia te identificas?",
                    "SiTePasaAlgoBuenoAQuienLeCuentasPrimero": "¿A quién le cuentas primero si te pasa algo bueno?",
                    "TeAdaptadasALosCambios": "¿Te adaptas fácilmente a los cambios?",
                    "TeHazDespertadoFrescxYDescansadx": "¿Te has despertado fresc@ y descansad@?",
                    "TeHazSentidoActivxYEnergicx": "¿Te has sentido activ@ y energic@?",
                    "TeHazSentidoAlegreYDeBuenHumor": "¿Te has sentido alegre y de buen humor?",
                    "TeHazSentidoTranquilxYRelajadx": "¿Te has sentido tranquil@ y relajad@?",
                    "TuEn10Años": "¿Cómo te ves en 10 años?",
                    "TuVidaCotiadianaHaEstadoLlenaDeCosasQueMeInteresen": "¿Tu vida diaria ha estado llena de cosas interesantes?",
                    "YSiTePasaAlgoMalo": "¿A quién le cuentas si te pasa algo malo?"
                }

                df.rename(columns=renames, inplace=True)

            st.subheader("Vista previa del DataFrame")
            st.dataframe(df)

            csv = df.to_csv(index=False).encode("utf-8")
            filename = f"{collection_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

            st.download_button("Descargar CSV", csv, filename=filename, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    except Exception as e:
        st.error(f"Error: {e}")
