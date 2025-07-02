import streamlit as st
import pandas as pd
import json
from google.oauth2 import service_account
from google.cloud import firestore
from io import BytesIO

st.set_page_config(page_title="Exportador Firestore a Excel")

st.title("Exportador Firestore a Excel")

uploaded_file = st.file_uploader("Sube tu archivo JSON con credenciales", type="json")

if uploaded_file:
    credentials_info = json.load(uploaded_file)
    project_id = credentials_info.get("project_id", "")

    try:
        credentials = service_account.Credentials.from_service_account_info(credentials_info)
        db = firestore.Client(credentials=credentials, project=project_id)

        docs = db.collection("respuestas").stream()
        data = [doc.to_dict() for doc in docs]

        if not data:
            st.warning("No se encontraron documentos en la colección 'respuestas'.")
        else:
            df = pd.DataFrame(data)

            if project_id == "dondeestamicabezaserver":
                if "id" in df.columns:
                    df.drop(columns=["id"], inplace=True)

                rename_map = {
                    "SiTePasaAlgoBuenoAQuienLeCuentasPrimero": "¿Si te pasa algo bueno a quién le cuentas primero?",
                    "FrecuenciaPedirConsejo": "¿Con qué frecuencia pides consejo?",
                    "CuandoEstasTristeQueHaces": "¿Qué haces cuando estás triste?",
                    "CualEsTuMayorMiedo": "¿Cuál es tu mayor miedo?",
                    "TienesAmigosQueTeEscuchan": "¿Tienes amigos que te escuchan?",
                    "TeSientesSolxFrecuentemente": "¿Te sientes solx frecuentemente?",
                    "ConfiasEnTusPadres": "¿Confías en tus padres?",
                    "TeSientesEscuchadoPorAdultos": "¿Te sientes escuchado por adultos?",
                    "Nombre": "Nombre",
                    "Edad": "Edad"
                }

                df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns}, inplace=True)

            st.subheader("Vista previa de los datos")
            st.dataframe(df)

            output = BytesIO()
            df.to_excel(output, index=False)
            st.download_button(
                label="Descargar Excel",
                data=output.getvalue(),
                file_name="respuestas_exportadas.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.error(f"Error al conectar a Firestore: {e}")
