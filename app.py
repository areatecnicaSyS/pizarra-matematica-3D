from io import BytesIO
import numpy as np
from PIL import Image
import plotly.graph_objects as go
import streamlit as st
from streamlit_drawable_canvas import st_canvas
import sympy as sp

# ---------------------------------------------------------
# Configuración inicial de la página
# ---------------------------------------------------------
st.set_page_config(
    page_title="Pizarra Digital - Área Técnica",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos CSS personalizados para adaptar el diseño corporativo
st.markdown(
    """
    <style>
    .main {
        background-color: #0f172a;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
    }
    .stSelectbox, .stTextInput {
        color: #f8fafc;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Barra Lateral (Sidebar) con Logo y Controles de Dibujo
# ---------------------------------------------------------
with st.sidebar:
  try:
    st.image("logo.png", use_container_width=True)
  except Exception:
    st.title("Área Técnica")

  st.markdown("---")
  st.subheader("🎨 Controles de la Pizarra")

  # Herramientas de dibujo
  drawing_mode = st.radio(
      "Herramienta de Trazo:",
      ("freedraw", "transform"),
      format_func=lambda x: (
          "✏️ Lápiz Digital / Mouse"
          if x == "freedraw"
          else "🔍 Mover / Seleccionar"
      ),
  )

  stroke_width = st.slider("Grosor del Lápiz (px):", 1, 25, 3)

  stroke_color = st.color_picker("Color de Tinta:", "#FFFFFF")
  bg_color = "#0f172a"  # Fondo oscuro corporativo

  # Desactivado por defecto para evitar sobrecargar la CPU del servidor gratuito de Streamlit
  realtime_update = st.checkbox(
      "Actualizar banner en tiempo real", value=False
  )

st.title("🧮 Pizarra Digital Interactiva con Solucionador Algebraico")
st.markdown(
    "Dibuja o escribe tus expresiones con lápiz digital/mouse, captura el"
    " lienzo y resuelve polinomios o ecuaciones en tiempo real."
)

col_canvas, col_results = st.columns([7, 5])

# ---------------------------------------------------------
# Columna Izquierda: Lienzo de Dibujo Táctil / Digital
# ---------------------------------------------------------
with col_canvas:
  st.subheader("🖋️ Lienzo de Dibujo")

  # Componente Canvas de Streamlit con drawing_mode asegurado en formato string minúscula
  mode = "freedraw" if drawing_mode == "freedraw" else "transform"

  canvas_result = st_canvas(
      fill_color="rgba(255, 255, 255, 0.0)",  # Fondo transparente para trazado
      stroke_width=stroke_width,
      stroke_color=stroke_color,
      background_color=bg_color,
      update_streamlit=realtime_update,
      height=500,
      drawing_mode=mode,
      key="main_canvas",
  )

  st.info(
      "💡 Puedes dibujar con mouse, lápiz digital o pantalla táctil en el área"
      " oscura superior."
  )

# ---------------------------------------------------------
# Columna Derecha: Banner de Capturas y Resultados SymPy
# ---------------------------------------------------------
with col_results:
  st.subheader("📊 Banner de Resultados & Capturas")

  # 1. Muestra de Captura del Canvas
  st.markdown("#### 🖼️ Última Captura del Lienzo")

  # Validación segura para evitar RuntimeError si canvas_result no tiene aún datos de imagen
  has_image = (
      canvas_result is not None
      and getattr(canvas_result, "image_data", None) is not None
  )

  if has_image:
    try:
      # Convertir arreglo numpy a imagen PIL
      img_data = canvas_result.image_data.astype(np.uint8)
      image = Image.fromarray(img_data)

      # Mostrar la imagen capturada en el banner
      st.image(image, caption="Captura procesada de la pizarra", width=380)

      # Botón para descargar la captura
      buf = BytesIO()
      image.save(buf, format="PNG")
      byte_im = buf.getvalue()

      st.download_button(
          label="💾 Descargar Captura en HD",
          data=byte_im,
          file_name="pizarra_area_tecnica.png",
          mime="image/png",
      )
    except Exception:
      st.warning(
          "Dibuja algo en la pizarra para actualizar la vista previa."
      )
  else:
    st.warning("Dibuja algo en la pizarra para generar la vista previa.")

  st.markdown("---")

  # 2. Solucionador Algebraico Integrado (SymPy)
  st.markdown("#### ⚙️ Solucionador Algebraico")

  operacion = st.selectbox(
      "Operación a realizar:",
      [
          "Factorizar Polinomio",
          "Resolver Ecuación (= 0)",
          "Expandir / Simplificar",
      ],
  )

  expresion_input = st.text_input(
      "Expresión matemática:",
      value="x**2 - 9",
      help="Utiliza sintaxis de Python/SymPy (ej: x**2 - 9 o 2*x**2 + 5*x + 2)",
  )

  if st.button("🚀 Procesar Expresión"):
    if expresion_input:
      try:
        x = sp.symbols("x")
        expr = sp.sympify(expresion_input)

        st.markdown("##### **Resultado de la Resolución:**")

        if operacion == "Factorizar Polinomio":
          res = sp.factor(expr)
          st.latex(f"\\text{{Original: }} {sp.latex(expr)}")
          st.latex(f"\\text{{Factorizado: }} {sp.latex(res)}")

        elif operacion == "Resolver Ecuación (= 0)":
          sol = sp.solve(expr, x)
          st.latex(f"{sp.latex(expr)} = 0")
          st.write(f"**Soluciones encontradas:** `{sol}`")

        elif operacion == "Expandir / Simplificar":
          exp = sp.expand(expr)
          st.latex(f"\\text{{Expresión Expandida: }} {sp.latex(exp)}")

      except Exception as e:
        st.error(
            f"Error al interpretar la expresión. Revisa la sintaxis. Detalle:"
            f" {e}"
        )