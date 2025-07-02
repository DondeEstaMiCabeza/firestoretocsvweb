import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import json
import datetime
from firebase_admin.firestore import GeoPoint
from io import BytesIO
from collections.abc import MutableMapping

st.title("Exportar datos de Firebase a Excel (.xlsx)")

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

if uploaded_file and st.button("Generar Excel"):
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
                all_keys.add(key)

            flat_doc['id'] = doc.id
            data.append(flat_doc)

        st.write("Se encontraron", len(data), "documentos.")

        df = pd.DataFrame(data)

        # Cargar el archivo de credenciales y verificar el project_id
        import json
        expected_project_id = "dondeestamicabezaserver"
        target_collection = "respuestas"
        try:
            with open(credentials_path, "r") as f:
                credentials_data = json.load(f)
                project_id = credentials_data.get("project_id", "")
        except Exception as e:
            st.error(f"Error al leer las credenciales: {e}")
            return

        # Si el project_id y colección coinciden, aplicar la lógica de reemplazo
        if project_id == expected_project_id and collection_name == target_collection:
            field_name_map = {
                "SiTePasaAlgoBuenoAQuienLeCuentasPrimero": "¿Si te pasa algo bueno, a quién se lo cuentas primero?",
                "FrecuenciaPedirConsejo": "¿Con qué frecuencia pides consejo cuando no sabes qué hacer?",
                "CuandoMeEnfrentoALosProblemas": "Cuando me enfrento a los problemas...",
                "Raza": "¿Cuál es tu identidad étnico-racial?",
                "QueTeMantieneConVida": "¿Qué te mantiene con vida?",
                "TeHazSentidoActivxYEnergicx": "Durante las últimas dos semanas ¿Te has sentido activx y llenx de energía?",
                "Donde_Vives": "¿Dónde vives?",
                "YSiTePasaAlgoMalo": "¿Y si te pasa algo malo?",
                "ConQueTeDiviertes": "¿Con qué te diviertes?",
                "DespuesDeLaTormentaMeSiento": "Después de la tormenta me siento...",
                "TeHazDespertadoFrescxYDescansadx": "Durante las últimas dos semanas ¿Te has despertado frescx y descansadx?",
                "TuEn10Años": "¿Cómo te ves en 10 años?",
                "CuandoVeoAlguienEnProblemas": "Cuando veo que alguien tiene problemas...",
                "PanaInfluencer": "¿Quién es tu pana influencer?",
                "Generos": "¿Con qué género(s) te identificas?",
                "QueTeGustariaHacer": "¿Qué te gustaría hacer?",
                "TeHazSentidoTranquilxYRelajadx": "Durante las últimas dos semanas ¿Te has sentido tranquilx y relajadx?",
                "FrecuenciaLograrObjetivos": "¿Con qué frecuencia logras lo que te propones?",
                "ActividadActual": "¿Cuál es tu actividad actual?",
                "TeAdaptadasALosCambios": "¿Te adaptas con facilidad a los cambios?",
                "TeHazSentidoAlegreYDeBuenHumor": "Durante las últimas dos semanas ¿Te has sentido alegre y de buen humor?",
                "CualidadesDelInfluencer": "¿Qué cualidades debe tener un influencer para que te inspire?",
                "Edad": "¿Cuántos años tienes?",
                "QueEsLoPeorDeTuTrabajoOEstudio": "¿Qué es lo peor de tu trabajo o de tu estudio?",
                "TuVidaCotiadianaHaEstadoLlenaDeCosasQueMeInteresen": "Durante las últimas dos semanas ¿Tu vida cotidiana ha estado llena de cosas que te interesen?",
                "CuandoEstasDiscutiendo": "Cuando estás discutiendo con alguien...",
                "DondeTeSientesMejor": "¿Dónde te sientes mejor?"
            }

            df.rename(columns=field_name_map, inplace=True)

            # Eliminar columna 'id' si está presente
            if 'id' in df.columns:
                df.drop(columns=['id'], inplace=True)

        df = df.reindex(columns=sorted(all_keys) + ['id'])

        # Mostrar previsualización
        st.subheader("Previsualización de los datos")
        st.dataframe(df)

        # Guardar como Excel en memoria
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Respuestas')
        buffer.seek(0)

        st.success("¡Excel generado exitosamente!")
        st.download_button(
            label="Descargar Excel",
            data=buffer,
            file_name="datos_exportados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
