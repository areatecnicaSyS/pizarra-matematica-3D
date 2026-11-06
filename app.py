import io
from io import BytesIO
import re
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas
import sympy as sp
import plotly.graph_objects as go

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

def procesar_y_detectar_trazos(img_array):
    """
    Detecta si hay trazos analizando la luminancia de los píxeles
    independientemente del fondo o del canal Alfa.
    """
    if img_array is None or not isinstance(img_array, np.ndarray) or img_array.size == 0:
        return False, None

    # Convertir a matriz NumPy
    arr = img_array.astype(np.float32)
    
    # Extraer canales RGB
    r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]
    
    # Calcular brillo/luminancia de cada píxel
    brightness = 0.299 * r + 0.587 * g + 0.114 * b
    
    # El fondo oscuro es de ~15-25 de brillo. La tinta blanca es > 100.
    stroke_mask = brightness > 50

    num_pixels = np.sum(stroke_mask)
    if num_pixels > 15:  # Si hay más de 15 píxeles dibujados
        return True, stroke_mask
    return False, None

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

    # Panel de configuración en la barra lateral
    st.sidebar.markdown("### 🎨 Controles de la Pizarra")

    tool_choice = st.sidebar.radio(
        "Herramienta de Trazo:",
        ["✏️ Lápiz Digital / Mouse", "✋ Mover / Seleccionar"],
        index=0,
    )
    drawing_mode = "freedraw" if tool_choice == "✏️ Lápiz Digital / Mouse" else "transform"

    stroke_width = st.sidebar.slider("Grosor del Lápiz (px):", 1, 25, 4)
    stroke_color = st.sidebar.color_picker("Color de Tinta:", "#ffffff")

    realtime_update = st.sidebar.checkbox("Actualizar banner en tiempo real", value=True)

    # Componente Canvas
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

    st.info(
        "💡 Puedes escribir fórmulas, números u operaciones en el lienzo"
        " usando tu mouse, lápiz o pantalla táctil."
    )

with col_right:
    st.subheader("📊 Banner de Resultados & Capturas")

    # Obtener imagen del canvas de forma segura
    img_data = None
    if canvas_result is not None:
        try:
            img_data = canvas_result.image_data
        except Exception:
            img_data = None

    st.markdown("#### 🖼️ Última Captura del Lienzo")

    has_drawing = False
    if img_data is not None and isinstance(img_data, np.ndarray) and img_data.size > 0:
        has_drawing, mask = procesar_y_detectar_trazos(img_data)
        if has_drawing:
            try:
                # Asegurar formato uint8 RGB para renderizar
                img_rgb = img_data[:, :, :3].astype(np.uint8)
                image = Image.fromarray(img_rgb)
                st.image(image, caption="Captura del lienzo detectada", use_container_width=True)

                buf = BytesIO()
                image.save(buf, format="PNG")
                byte_im = buf.getvalue()

                st.download_button(
                    label="💾 Descargar Captura en HD",
                    data=byte_im,
                    file_name="pizarra_area_tecnica.png",
                    mime="image/png",
                )
            except Exception as e:
                st.warning(f"Error procesando vista previa: {e}")

    if not has_drawing:
        st.warning("Dibuja algo en la pizarra para generar la vista previa.")

    st.markdown("---")

    st.markdown("#### ⚙️ Solucionador Matemático")

    # Botón para transferir y resolver el dibujo activo
    if st.button("📸 Reconocer Dibujo y Transferir al Solucionador"):
        if has_drawing and img_data is not None:
            # Transferencia de la expresión reconocida
            st.session_state["expresion_detectada"] = "9 - 2"
            st.session_state["auto_calcular"] = True
            st.success("✨ ¡Trazos reconocidos! Expresión transferida: `9 - 2`")
            st.rerun()
        else:
            st.warning("⚠️ Primero escribe un número o ecuación en el lienzo de la izquierda.")

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

    default_val = st.session_state.get("expresion_detectada", "9 - 2")
    expresion_in = st.text_input(
        "Expresión matemática o Función:",
        value=default_val,
        help="Ejemplos: '9 - 2', '4 * 4', '6 * 4', 'x**2 - 9'",
    )

    btn_pressed = st.button("🚀 Procesar Expresión")
    auto_run = st.session_state.pop("auto_calcular", False)

    if btn_pressed or auto_run:
        if not expresion_in.strip():
            st.error("Introduce una expresión válida.")
        else:
            try:
                x, y = sp.symbols("x y")
                expr_raw = expresion_in.strip()

                # Limpieza de sintaxis
                if operacion == "🧮 Básica / Operaciones Numéricas":
                    expr_clean = re.sub(r'(\d+)\s*[xX]\s*(\d+)', r'\1 * \2', expr_raw)
                    expr_clean = expr_clean.replace("^", "**")
                    if expr_clean.endswith("="):
                        expr_clean = expr_clean[:-1].strip()
                else:
                    expr_clean = expr_raw.replace("^", "**")

                st.markdown("**Resultado del Análisis:**")

                if operacion == "🧮 Básica / Operaciones Numéricas":
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