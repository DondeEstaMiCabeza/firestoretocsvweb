import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import json
import datetime
from firebase_admin.firestore import GeoPoint
from io import BytesIO
from collections.abc import MutableMapping

st.title("Exportar datos de Firebase a CSV")

# Función para aplanar diccionarios anidados
def flatten_dict(d, parent_key='', sep='.'):
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

uploaded_file = st.file_uploader("Sube tu archivo de credenciales de Firebase (.json)", type="json")
coleccion_nombre = st.text_input("Nombre de la colección de Firestore", value="respuestas")

if uploaded_file and st.button("Generar CSV"):
    try:
        # Inicializar Firebase desde archivo subido
        cred_dict = json.load(uploaded_file)
        st.write("Conectado al proyecto:", cred_dict.get("project_id", "No detectado"))
        cred = credentials.Certificate(cred_dict)

        # Reinicializar Firebase si ya estaba inicializado
        if firebase_admin._apps:
            firebase_admin.delete_app(firebase_admin.get_app())
        firebase_admin.initialize_app(cred)

        db = firestore.client()
        docs = db.collection(coleccion_nombre).stream()

        data = []
        all_keys = set()

        for doc in docs:
            raw_dict = doc.to_dict()
            flat_doc = flatten_dict(raw_dict)

            for key, value in flat_doc.items():
                if isinstance(value, (list, dict)):
                    flat_doc[key] = json.dumps(value)
                elif isinstance(value, datetime.datetime):
                    flat_doc[key] = value.isoformat()
                elif isinstance(value, GeoPoint):
                    flat_doc[key] = f"{value.latitude}, {value.longitude}"
                # otros tipos se dejan igual
                all_keys.add(key)

            flat_doc['id'] = doc.id
            data.append(flat_doc)

        st.write("Se encontraron", len(data), "documentos.")

        df = pd.DataFrame(data)
        df = df.reindex(columns=sorted(all_keys) + ['id'])

        # Mostrar previsualización
        st.subheader("Previsualización de los datos")
        st.dataframe(df)

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
