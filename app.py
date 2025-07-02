
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import os
import json

# Cargar el archivo JSON
with open("survey.json") as source:
    cred_data = json.load(source)

project_id = cred_data.get("project_id", "")

# Inicializar Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_data)
    firebase_admin.initialize_app(cred)

db = firestore.client()

st.title("Exportar respuestas de Firebase a Excel")

coleccion = st.text_input("Nombre de la colección de Firestore", value="respuestas")

if st.button("Exportar a Excel"):
    docs = db.collection(coleccion).stream()

    datos = []
    for doc in docs:
        d = doc.to_dict()
        d["id"] = doc.id
        datos.append(d)

    if not datos:
        st.warning("No se encontraron documentos en la colección.")
    else:
        df = pd.DataFrame(datos)

        # Reglas especiales si el proyecto es 'dondeestamicabezaserver'
        if project_id == "dondeestamicabezaserver":
            # Diccionario de mapeo exacto
            columnas_mapeadas = [
                "Si te pasa algo bueno ¿a quién se lo cuentas primero?",
                "¿Con qué frecuencia pides consejo a otras personas antes de tomar decisiones importantes?",
                "Cuando me enfrento a los problemas...",
                "¿Con cuál raza te identificas más?",
                "¿Qué te mantiene con vida hoy?",
                "Últimamente ¿te has sentido activx y energicx?",
                "¿Dónde vives actualmente?",
                "¿Y si te pasa algo malo?",
                "¿Con qué te diviertes últimamente?",
                "Después de la tormenta me siento...",
                "¿Te has despertado frescx y descansadx últimamente?",
                "¿Cómo te ves en 10 años?",
                "Cuando veo a alguien con problemas...",
                "Imagina que eres un Pana Influencer...",
                "¿Qué te gustaría hacer o lograr este año?",
                "¿Con qué géneros te identificas?",
                "Últimamente ¿te has sentido tranquilx y relajadx?",
                "¿Con qué frecuencia logras lo que te propones?",
                "¿Qué haces actualmente? (ocupación)",
                "¿Te adaptas con facilidad a los cambios?",
                "Últimamente ¿te has sentido alegre y de buen humor?",
                "¿Qué cualidades tendría tu influencer ideal?",
                "¿Cuántos años tienes?",
                "¿Qué es lo peor de tu trabajo o estudio?",
                "Tu vida cotidiana ha estado llena de cosas que te interesen.",
                "Cuando estás discutiendo con alguien...",
                "¿Dónde te sientes mejor?"
            ]

            claves_originales = [
                "SiTePasaAlgoBuenoAQuienLeCuentasPrimero", "FrecuenciaPedirConsejo",
                "CuandoMeEnfrentoALosProblemas", "Raza", "QueTeMantieneConVida",
                "TeHazSentidoActivxYEnergicx", "Donde_Vives", "YSiTePasaAlgoMalo",
                "ConQueTeDiviertes", "DespuesDeLaTormentaMeSiento",
                "TeHazDespertadoFrescxYDescansadx", "TuEn10Años",
                "CuandoVeoAlguienEnProblemas", "PanaInfluencer", "QueTeGustariaHacer",
                "Generos", "TeHazSentidoTranquilxYRelajadx", "FrecuenciaLograrObjetivos",
                "ActividadActual", "TeAdaptadasALosCambios", "TeHazSentidoAlegreYDeBuenHumor",
                "CualidadesDelInfluencer", "Edad", "QueEsLoPeorDeTuTrabajoOEstudio",
                "TuVidaCotiadianaHaEstadoLlenaDeCosasQueMeInteresen",
                "CuandoEstasDiscutiendo", "DondeTeSientesMejor"
            ]

            renombrar_dict = dict(zip(claves_originales, columnas_mapeadas))
            df.rename(columns=renombrar_dict, inplace=True)

            if "id" in df.columns:
                df.drop(columns=["id"], inplace=True)

        # Crear archivo Excel
        excel_path = "respuestas_exportadas.xlsx"
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="Respuestas")
            writer.sheets["Respuestas"].cell(row=1, column=1).value = "Respuestas exportadas"

        st.success(f"Archivo Excel generado: {excel_path}")
        st.download_button("Descargar Excel", data=open(excel_path, "rb").read(), file_name="respuestas_exportadas.xlsx")

        # Previsualización
        st.subheader("Previsualización")
        st.dataframe(df.head())
