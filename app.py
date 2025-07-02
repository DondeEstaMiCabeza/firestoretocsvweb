
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import json
import io

def main():
    st.title("Exportador Firestore a Excel")

    uploaded_file = st.file_uploader("Sube tu archivo JSON con credenciales", type="json")
    collection_name = st.text_input("Nombre de la colección", value="respuestas")

    if uploaded_file and collection_name:
        data = json.load(uploaded_file)

        if "project_id" not in data:
            st.error("El archivo JSON no contiene 'project_id'.")
            return

        project_id = data["project_id"]

        # Inicializar Firebase
        if not firebase_admin._apps:
            cred = credentials.Certificate(data)
            firebase_admin.initialize_app(cred, {"projectId": project_id})

        db = firestore.client()
        docs = db.collection(collection_name).stream()

        rows = []
        for doc in docs:
            d = doc.to_dict()
            d["id"] = doc.id
            rows.append(d)

        if not rows:
            st.warning("No se encontraron documentos en la colección.")
            return

        df = pd.DataFrame(rows)

        # Borrar columna id si coincide el project_id
        if project_id == "dondeestamicabezaserver" and "id" in df.columns:
            df.drop(columns=["id"], inplace=True)

        # Reemplazar encabezados si project_id y colección coinciden
        if project_id == "dondeestamicabezaserver" and collection_name == "respuestas":
            encabezados = [
                "SiTePasaAlgoBuenoAQuienLeCuentasPrimero", "FrecuenciaPedirConsejo", "CuandoMeEnfrentoALosProblemas",
                "Raza", "QueTeMantieneConVida", "TeHazSentidoActivxYEnergicx", "Donde_Vives", "YSiTePasaAlgoMalo",
                "ConQueTeDiviertes", "DespuesDeLaTormentaMeSiento", "TeHazDespertadoFrescxYDescansadx", "TuEn10Años",
                "CuandoVeoAlguienEnProblemas", "PanaInfluencer", "Generos", "QueTeGustariaHacer", "TeHazSentidoTranquilxYRelajadx",
                "FrecuenciaLograrObjetivos", "ActividadActual", "TeAdaptadasALosCambios", "TeHazSentidoAlegreYDeBuenHumor",
                "CualidadesDelInfluencer", "Edad", "QueEsLoPeorDeTuTrabajoOEstudio", "TuVidaCotiadianaHaEstadoLlenaDeCosasQueMeInteresen",
                "CuandoEstasDiscutiendo", "DondeTeSientesMejor"
            ]
            if len(encabezados) == len(df.columns):
                df.columns = encabezados
            else:
                for i, col in enumerate(df.columns):
                    if i < len(encabezados):
                        df.rename(columns={col: encabezados[i]}, inplace=True)

        st.subheader("Previsualización de datos:")
        st.dataframe(df)

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Datos")
        st.download_button(
            label="Descargar Excel",
            data=output.getvalue(),
            file_name="exported_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()
