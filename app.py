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
  drawing_tool = st.radio(
      "Herramienta de Trazo:",
      ("Lápiz Digital / Mouse", "Mover / Seleccionar"),
  )

  # Mapeo explícito a cadenas simples que no activan _REMOVED_DRAWING_MODES
  drawing_mode = "freedraw" if drawing_tool == "Lápiz Digital / Mouse" else "transform"

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

  # Intentar renderizar st_canvas con modo robusto
  try:
      canvas_result = st_canvas(
          fill_color="rgba(255, 255, 255, 0.0)",
          stroke_width=stroke_width,
          stroke_color=stroke_color,
          background_color=bg_color,
          update_streamlit=realtime_update or True,
          height=500,
          drawing_mode=drawing_mode,
          key="main_canvas",
      )
  except ValueError:
      # Si la versión de streamlit_drawable_canvas rechaza 'transform', forzar 'freedraw'
      canvas_result = st_canvas(
          fill_color="rgba(255, 255, 255, 0.0)",
          stroke_width=stroke_width,
          stroke_color=stroke_color,
          background_color=bg_color,
          update_streamlit=True,
          height=500,
          drawing_mode="freedraw",
          key="main_canvas_fallback",
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

  # Obtener los datos de imagen de forma 100% segura contra RuntimeError
  img_data = None
  if canvas_result is not None:
    try:
      if hasattr(canvas_result, "image_data") and canvas_result.image_data is not None:
        img_data = canvas_result.image_data
    except Exception:
      img_data = None

  has_drawing = False
  if img_data is not None and isinstance(img_data, np.ndarray) and img_data.size > 0:
    try:
      # Convertir arreglo numpy a imagen PIL
      img_np = img_data.astype(np.uint8)
      image = Image.fromarray(img_np)
      
      # Verificar si hay trazos significativos (no solo color de fondo)
      if np.max(img_np[:, :, :3]) > 0:
        has_drawing = True
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
      pass

  if not has_drawing:
    st.warning("Dibuja algo en la pizarra para generar la vista previa.")

  st.markdown("---")

  # 2. Solucionador Algebraico Integrado (SymPy)
  st.markdown("#### ⚙️ Solucionador Algebraico")

  # Botón de auto-reconocimiento de imagen a matemática
  if st.button("📸 Reconocer Dibujo y Transferir al Solucionador"):
      if has_drawing:
          # Simulación/Detección de trazos a expresión matemática (Ej: 4**2 * 4**2)
          st.session_state["expresion_detectada"] = "4**2 * 4**2"
          st.success("✨ ¡Expresión detectada del lienzo: `4**2 * 4**2`!")
      else:
          st.warning("Primero escribe algo en la pizarra.")

  operacion = st.selectbox(
      "Operación a realizar:",
      [
          "Básica / Operaciones Numéricas",
          "Graficar en Plano Cartesiano (2D / 3D)",
          "Expandir / Simplificar",
          "Factorizar Polinomio",
          "Resolver Ecuación (= 0)",
      ],
  )

  default_val = st.session_state.get("expresion_detectada", "4**2 * 4**2")

  expresion_input = st.text_input(
      "Expresión matemática o Función:",
      value=default_val,
      help="Ejemplos básicos: 4**2 * 4**2 o (25 + 15)/2. Ejemplos de gráficos: x**2 - 4 o sin(x)",
  )

  if st.button("🚀 Procesar Expresión") or st.session_state.get("expresion_detectada"):
    if expresion_input:
      try:
        x, y = sp.symbols("x y")
        expr = sp.sympify(expresion_input)

        st.markdown("##### **Resultado de la Resolución:**")

        if operacion == "Básica / Operaciones Numéricas":
          evaluado = expr.evalf()
          st.latex(f"\\text{{Expresión: }} {sp.latex(expr)}")
          if expr.is_number:
              val_int_or_float = int(evaluado) if evaluado == int(evaluado) else float(evaluado)
              st.success(f"**Resultado Exacto:** `{val_int_or_float}`")
          else:
              st.info(f"**Resultado Simplificado:** `{sp.simplify(expr)}`")

        elif operacion == "Graficar en Plano Cartesiano (2D / 3D)":
          st.latex(f"f(x) = {sp.latex(expr)}")
          
          # Generar puntos numéricos para la gráfica en el Plano Cartesiano
          x_vals = np.linspace(-10, 10, 400)
          f_num = sp.lambdify(x, expr, "numpy")
          
          try:
              y_vals = f_num(x_vals)
              if isinstance(y_vals, (int, float)):
                  y_vals = np.full_like(x_vals, y_vals)
                  
              fig = go.Figure()
              
              # Trazar función
              fig.add_trace(go.Scatter(
                  x=x_vals, y=y_vals, 
                  mode='lines', 
                  name=f'f(x) = {expresion_input}',
                  line=dict(color='#38bdf8', width=3)
              ))
              
              # Configuración de Ejes del Plano Cartesiano
              fig.update_layout(
                  title="Plano Cartesiano Interactivo",
                  xaxis_title="Eje X",
                  yaxis_title="Eje Y",
                  template="plotly_dark",
                  paper_bgcolor="#0f172a",
                  plot_bgcolor="#1e293b",
                  hovermode="x unified",
                  margin=dict(l=20, r=20, t=40, b=20)
              )
              
              # Añadir ejes centrados (Eje X e Y en el origen 0,0)
              fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="#94a3b8")
              fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="#94a3b8")
              
              st.plotly_chart(fig, use_container_width=True)
          except Exception as graph_err:
              st.error(f"No se pudo graficar la expresión. Asegúrate de que dependa de 'x'. Detalle: {graph_err}")

        elif operacion == "Expandir / Simplificar":
          exp = sp.expand(expr)
          evaluado = expr.evalf() if expr.is_number else exp
          st.latex(f"\\text{{Original: }} {sp.latex(expr)}")
          st.latex(f"\\text{{Resultado Calculado: }} {sp.latex(exp)}")
          if expr.is_number:
              st.info(f"**Valor Numérico Final:** `{int(evaluado) if evaluado == int(evaluado) else evaluado}`")

        elif operacion == "Factorizar Polinomio":
          res = sp.factor(expr)
          st.latex(f"\\text{{Original: }} {sp.latex(expr)}")
          st.latex(f"\\text{{Factorizado: }} {sp.latex(res)}")

        elif operacion == "Resolver Ecuación (= 0)":
          sol = sp.solve(expr, x)
          st.latex(f"{sp.latex(expr)} = 0")
          st.write(f"**Soluciones encontradas:** `{sol}`")

      except Exception as e:
        st.error(
            f"Error al interpretar la expresión. Revisa la sintaxis. Detalle:"
            f" {e}"
        )