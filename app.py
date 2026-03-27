import streamlit as st
import json
import os
from PIL import Image

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(page_title="🛒 Lo Compro o no??", layout="wide")

ARCHIVO_DATOS = "mis_compras_pro.json"
CARPETA_FOTOS = "fotos_productos"

if not os.path.exists(CARPETA_FOTOS):
    os.makedirs(CARPETA_FOTOS)

# Memoria para el mensaje de éxito tras el refresco
if 'mensaje_exito' not in st.session_state:
    st.session_state.mensaje_exito = None

def cargar_datos():
    if os.path.exists(ARCHIVO_DATOS):
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: return {}
    return {}

def guardar_datos(datos):
    with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

datos = cargar_datos()
lista_nombres = sorted(list(datos.keys()))

# --- BARRA LATERAL (Añadir Producto) ---
with st.sidebar:
    st.header("➕ Nuevo Producto")
    
    nombre_nuevo = st.text_input("Nombre del producto*").lower().strip()
    comentario_nuevo = st.text_area("Comentarios*")
    
    # Calificación con circulitos (Radio botones)
    puntuacion_nueva = st.radio(
        "Calificación*",
        options=["🔴 Malo", "🟠 Pasable", "🟢 Bueno"],
        index=None, 
        help="Selecciona una opción"
    )
    
    archivo_foto = st.file_uploader("📷 Foto (Opcional)", type=["jpg", "png", "jpeg"])
    
    st.caption("* Campos obligatorios")

    if st.button("💾 GUARDAR PRODUCTO", type="primary"):
        # VALIDACIÓN: No deja crear si falta información esencial
        if not nombre_nuevo or not comentario_nuevo or not puntuacion_nueva:
            st.error("❌ Error: Debes rellenar todos los campos obligatorios (*).")
        else:
            ruta_foto = None
            if archivo_foto:
                ruta_foto = os.path.join(CARPETA_FOTOS, f"{nombre_nuevo}.jpg")
                img = Image.open(archivo_foto).convert("RGB")
                img.save(ruta_foto, "JPEG")
            
            datos[nombre_nuevo] = {
                "comentario": comentario_nuevo, 
                "estado": puntuacion_nueva, 
                "foto": ruta_foto
            }
            guardar_datos(datos)
            
            # Guardamos el mensaje con el tick y el pulgar
            st.session_state.mensaje_exito = f"✅ 👍 ¡Producto '{nombre_nuevo.upper()}' creado correctamente!"
            st.rerun()

# --- CUERPO PRINCIPAL ---
st.title("🛒 Recuerdas este producto?")

# Mostrar mensaje de éxito sin globos
if st.session_state.mensaje_exito:
    st.success(st.session_state.mensaje_exito)
    st.session_state.mensaje_exito = None # Se limpia para la próxima vez

# BUSCADOR CON AUTOCOMPLETADO
seleccion = st.selectbox(
    "🔍 Empieza a escribir para buscar un producto:",
    options=[""] + lista_nombres,
    format_func=lambda x: "Escribe aquí..." if x == "" else x.upper()
)

if seleccion:
    info = datos[seleccion]
    with st.container(border=True):
        col1, col2 = st.columns([1, 2])
        with col1:
            if info.get("foto") and os.path.exists(info["foto"]):
                st.image(info["foto"], use_container_width=True)
            else:
                st.info("📷 Sin foto guardada")
        with col2:
            st.subheader(f"{info['estado']} - {seleccion.upper()}")
            st.markdown(f"**Tu opinión:** \n{info['comentario']}")
            
            # Espacio para separar el botón de borrar
            st.write("")
            if st.button(f"🗑️ Eliminar '{seleccion}'"):
                if info.get("foto") and os.path.exists(info["foto"]):
                    try: os.remove(info["foto"])
                    except: pass
                del datos[seleccion]
                guardar_datos(datos)
                st.rerun()
else:
    st.info("💡 Haz clic en el buscador de arriba y empieza a escribir para encontrar tus notas.")