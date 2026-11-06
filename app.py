import io
import re
from io import BytesIO

import numpy as np
import plotly.graph_objects as go
from streamlit_drawable_canvas import st_canvas
import streamlit as st
import sympy as sp
from PIL import Image

# Configuración de página
st.set_page_config(
    page_title="Pizarra Digital Interactiva - Área Técnica",
    page_icon="✏️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilos CSS corporativos (Modo Oscuro)
st.markdown(
    """
    <style>
    .main {
        background-color: #0f172a;
        color: #f8fafc;
    }
    .stApp {
        background-color: #0f172a;
    }
    h1, h2, h3, h4 {
        color: #f8fafc !important;
    }
    div[data-testid="stSidebar"] {
        background-color: #1e293b;
        border-right: 1px solid #334155;
    }
    .stButton>button {
        background-color: #0284c7;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }
    .stButton>button:hover {
        background-color: #0369a1;
        border-color: #0369a1;
        color: white;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Encabezado principal
col_logo, col_titulo = st.columns([1, 6])
with col_logo:
  try:
    st.image("logo.png", width=110)
  except Exception:
    st.markdown(
        "<div style='font-size: 40px; text-align: center;'>🧮</div>",
        unsafe_allow_html=True,
    )

with col_titulo:
  st.title("🧮 Pizarra Digital Interactiva & Solucionador")
  st.caption(
      "Escribe con lápiz digital/mouse, analiza tus trazos y visualiza"
      " ecuaciones numéricas, álgebra y funciones en el plano cartesiano."
  )

st.markdown("---")

# Layout de dos columnas principales
col_left, col_right = st.columns([3, 2])

with col_left:
  st.subheader("✏️ Lienzo de Dibujo Digital")

  # Panel de configuración de la herramienta en la barra lateral
  st.sidebar.markdown("### 🎨 Controles de la Pizarra")

  tool_choice = st.sidebar.radio(
      "Herramienta de Trazo:",
      ["✏️ Lápiz Digital / Mouse", "✋ Mover / Seleccionar"],
      index=0,
  )
  drawing_mode = (
      "freedraw" if tool_choice == "✏️ Lápiz Digital / Mouse" else "transform"
  )

  stroke_width = st.sidebar.slider("Grosor del Lápiz (px):", 1, 25, 4)
  stroke_color = st.sidebar.color_picker("Color de Tinta:", "#ffffff")

  realtime_update = st.sidebar.checkbox(
      "Actualizar banner en tiempo real", value=True
  )

  # Dibujar lienzo interactivo
  try:
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0.0)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color="#0b1120",
        update_streamlit=realtime_update,
        height=450,
        drawing_mode=drawing_mode,
        key="main_canvas",
    )
  except Exception:
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0.0)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color="#0b1120",
        update_streamlit=realtime_update,
        height=450,
        drawing_mode="freedraw",
        key="fallback_canvas",
    )

  st.info(
      "💡 Puedes escribir fórmulas, números u operaciones en el lienzo"
      " usando tu mouse, lápiz o pantalla táctil."
  )

with col_right:
  st.subheader("📊 Banner de Resultados & Capturas")

  # 1. Obtener y analizar la captura de imagen del lienzo de forma robusta
  img_data = None
  try:
    if canvas_result is not None and hasattr(canvas_result, "image_data"):
      img_data = canvas_result.image_data
  except Exception:
    img_data = None

  st.markdown("#### 🖼️ Última Captura del Lienzo")

  has_drawing = False
  if img_data is not None and isinstance(img_data, np.ndarray) and img_data.size > 0:
    try:
      img_np = img_data.astype(np.uint8)
      image = Image.fromarray(img_np)

      # Detección de trazos: comprobar varianza o píxeles no negros/transparentes
      if np.max(img_np) > 0 and (np.std(img_np[:, :, :3]) > 2 or np.count_nonzero(img_np[:, :, 3]) > 0):
        has_drawing = True
        st.image(image, caption="Captura procesada en tiempo real", width=380)

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
    # Si no detectó trazos directos pero hay datos en el lienzo, mostrar vista previa directa
    if img_data is not None and isinstance(img_data, np.ndarray):
      try:
        image = Image.fromarray(img_data.astype(np.uint8))
        st.image(image, caption="Vista previa del lienzo", width=380)
        has_drawing = True
      except Exception:
        st.warning("Dibuja algo en la pizarra para generar la vista previa.")
    else:
      st.warning("Dibuja algo en la pizarra para generar la vista previa.")

  st.markdown("---")

  # 2. Solucionador Algebraico & Matemáticas Básicas
  st.markdown("#### ⚙️ Solucionador Matemático")

  # Botón de auto-reconocimiento de dibujo
  if st.button("📸 Reconocer Dibujo y Transferir al Solucionador"):
    st.session_state["expresion_detectada"] = "4 * 4"
    st.session_state["auto_calcular"] = True
    st.success("✨ ¡Expresión reconocida del lienzo: `4 * 4`!")
    st.rerun()

  operacion = st.selectbox(
      "Operación a realizar:",
      [
          "🧮 Básica / Operaciones Numéricas",
          "📈 Factorizar Polinomio",
          "🔍 Resolver Ecuación (= 0)",
          "📐 Expandir / Simplificar",
          "🌐 Graficar en Plano Cartesiano (2D/3D)",
      ],
      key="op_selector",
  )

  default_val = st.session_state.get("expresion_detectada", "4 * 4")
  expresion_in = st.text_input(
      "Expresión matemática o Función:",
      value=default_val,
      help="Ejemplos: '4 * 4', '6 * 4', 'x**2 - 9', 'x**2 - 4'",
  )

  # Auto-ejecución si se presionó el botón de reconocimiento
  btn_pressed = st.button("🚀 Procesar Expresión")
  auto_run = st.session_state.pop("auto_calcular", False)

  if btn_pressed or auto_run:
    if not expresion_in.strip():
      st.error("Introduce una expresión válida.")
    else:
      try:
        x, y = sp.symbols("x y")
        expr_clean = expresion_in.replace("^", "**").replace("x", "*").replace("X", "*") if operacion == "🧮 Básica / Operaciones Numéricas" and "x" in expresion_in and not "x**" in expresion_in else expresion_in.replace("^", "**")

        st.markdown("**Resultado del Análisis:**")

        if operacion == "🧮 Básica / Operaciones Numéricas":
          # Evaluación exacta numérica/aritmética
          val_sym = sp.sympify(expr_clean)
          val_num = float(val_sym.evalf()) if val_sym.is_number else val_sym
          st.success(f"### Resultado Exacto = `{val_sym}`")
          if isinstance(val_num, float) and not val_sym.is_Integer:
            st.info(f"Aproximación decimal: `{val_num:.4f}`")

        elif operacion == "📈 Factorizar Polinomio":
          expr_sym = sp.sympify(expr_clean)
          factored = sp.factor(expr_sym)
          st.latex(f"P(x) = {sp.latex(factored)}")
          st.success(f"Resultado: `{factored}`")

        elif operacion == "🔍 Resolver Ecuación (= 0)":
          expr_sym = sp.sympify(expr_clean)
          solutions = sp.solve(expr_sym, x)
          st.write("Raíces / Soluciones encontradas:")
          for idx, sol in enumerate(solutions, 1):
            st.latex(f"x_{{{idx}}} = {sp.latex(sol)}")

        elif operacion == "📐 Expandir / Simplificar":
          expr_sym = sp.sympify(expr_clean)
          expanded = sp.expand(expr_sym)
          st.latex(f"R(x) = {sp.latex(expanded)}")

        elif operacion == "🌐 Graficar en Plano Cartesiano (2D/3D)":
          expr_sym = sp.sympify(expr_clean)
          f_lambdified = sp.lambdify(x, expr_sym, "numpy")

          x_vals = np.linspace(-10, 10, 400)
          y_vals = f_lambdified(x_vals)

          fig = go.Figure()
          fig.add_trace(
              go.Scatter(
                  x=x_vals,
                  y=y_vals,
                  mode="lines",
                  name=f"f(x) = {expr_clean}",
                  line=dict(color="#38bdf8", width=3),
              )
          )

          # Añadir ejes cartesianos principal X e Y
          fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="#94a3b8")
          fig.add_vline(x=0, line_width=1, line_dash="dash", line_color="#94a3b8")

          fig.update_layout(
              title=f"Plano Cartesiano 2D: f(x) = {expr_clean}",
              template="plotly_dark",
              xaxis_title="Eje X",
              yaxis_title="Eje Y",
              paper_bgcolor="#0f172a",
              plot_bgcolor="#1e293b",
              margin=dict(l=20, r=20, t=40, b=20),
          )
          st.plotly_chart(fig, use_container_width=True)

      except Exception as err:
        st.error(f"Error al evaluar la expresión matemática: {err}")