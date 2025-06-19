import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import json
import datetime
from firebase_admin.firestore import GeoPoint
from io import BytesIO

st.title("Exportar datos de Firebase a CSV")

uploaded_file = st.file_uploader("Sube tu archivo de credenciales de Firebase (.json)", type="json")
coleccion_nombre = st.text_input("Nombre de la colección de Firestore", value="respuestas")

if uploaded_file and st.button("Generar CSV"):
    try:
        # Inicializar Firebase desde archivo subido
        cred_dict = json.load(uploaded_file)
        cred = credentials.Certificate(cred_dict)

        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)

        db = firestore.client()
        docs = db.collection(coleccion_nombre).stream()

        data = []
        all_keys = set()

        for doc in docs:
            doc_dict = doc.to_dict()
            flat_doc = {}

            for key, value in doc_dict.items():
                if isinstance(value, (dict, list)):
                    flat_doc[key] = json.dumps(value)
                elif isinstance(value, datetime.datetime):
                    flat_doc[key] = value.isoformat()
                elif isinstance(value, GeoPoint):
                    flat_doc[key] = f"{value.latitude}, {value.longitude}"
                else:
                    flat_doc[key] = value
                all_keys.add(key)

            flat_doc['id'] = doc.id
            data.append(flat_doc)

        df = pd.DataFrame(data)
        df = df.reindex(columns=sorted(all_keys) + ['id'])

        # Guardar en memoria
        buffer = BytesIO()
        df.to_csv(buffer, index=False, encoding='utf-8-sig')
        buffer.seek(0)

        st.success("¡CSV generado exitosamente!")
        st.download_button(
            label="Descargar CSV",
            data=buffer,
            file_name="datos_exportados.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
