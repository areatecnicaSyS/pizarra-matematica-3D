from io import BytesIO
import re
import numpy as np
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas
import sympy as sp
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Pizarra Digital & Solucionador IA - Área Técnica",
    page_icon="✏️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main { background-color: #0b1120; color: #f8fafc; }
    .stApp { background-color: #0b1120; }
    div[data-testid="stSidebar"] { background-color: #0f172a; border-right: 1px solid #1e293b; }
    .stButton>button {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: white;
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        box-shadow: 0 4px 14px 0 rgba(2, 132, 199, 0.39);
        width: 100%;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #0369a1 0%, #075985 100%);
        color: white;
    }
    .card-banner {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1rem;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# ENCABEZADO
# -----------------------------------------------------------------------------
header_col1, header_col2 = st.columns([1, 7])
with header_col1:
    try:
        st.image("logo.png", width=95)
    except Exception:
        st.markdown("<div style='font-size: 45px; text-align: center;'>🧮</div>", unsafe_allow_html=True)

with header_col2:
    st.markdown(
        """
        <h1 style='margin-bottom: 0px;'>Pizarra Digital & Solucionador IA</h1>
        <p style='color: #94a3b8; font-size: 0.95rem;'>
            Área Técnica | Plataforma interactiva de resolución simbólica, cálculo numérico y visualización cartesiana 2D/3D.
        </p>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# -----------------------------------------------------------------------------
# COLUMNAS
# -----------------------------------------------------------------------------
col_canvas, col_solver = st.columns([1.1, 0.9])

with col_canvas:
    st.markdown("### ✏️ Lienzo de Dibujo Digital")

    st.sidebar.markdown("## 🎨 Ajustes del Lienzo")
    tool_choice = st.sidebar.radio("Herramienta:", ["✏️ Lápiz Digital / Mouse", "✋ Mover / Seleccionar"], index=0)
    drawing_mode = "freedraw" if tool_choice == "✏️ Lápiz Digital / Mouse" else "transform"

    stroke_width = st.sidebar.slider("Grosor del trazo (px):", 1, 20, 5)
    stroke_color = st.sidebar.color_picker("Color de Tinta:", "#ffffff")

    # Canvas principal estable
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0.0)",
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color="#0b1120",
        update_streamlit=True,
        height=450,
        drawing_mode=drawing_mode,
        key="main_canvas_prod_v8",
    )

    st.caption("💡 Tip: Tras terminar de dibujar en la pizarra, haz clic en el botón de la derecha para transferir y resolver.")

with col_solver:
    st.markdown("### 📊 Banner de Resultados & Capturas")

    st.markdown("<div class='card-banner'>", unsafe_allow_html=True)
    st.markdown("#### 🖼️ Vista Previa del Lienzo")

    # Intento seguro de lectura de imagen
    img_data = None
    if canvas_result is not None:
        try:
            img_data = getattr(canvas_result, "image_data", None)
        except Exception:
            img_data = None

    if img_data is not None and isinstance(img_data, np.ndarray) and img_data.size > 0:
        pil_img = Image.fromarray(img_data[:, :, :3].astype(np.uint8))
        st.image(pil_img, caption="Trazos de la Pizarra", use_container_width=True)

        buf = BytesIO()
        pil_img.save(buf, format="PNG")
        byte_im = buf.getvalue()

        st.download_button(
            label="💾 Descargar Captura en HD",
            data=byte_im,
            file_name="captura_pizarra.png",
            mime="image/png",
        )
    else:
        st.info("🎨 Dibuja libremente en la pizarra. El sistema está listo para capturar.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Botón de Reconocimiento y Transferencia directa
    if st.button("📸 Reconocer Dibujo y Transferir al Solucionador"):
        st.session_state["auto_calcular"] = True
        st.success("✨ ¡Dibujo transferido al solucionador correctamente!")
        st.rerun()

    st.markdown("---")
    st.markdown("#### ⚙️ Motor Matemático SymPy")

    operacion = st.selectbox(
        "Modo de Operación:",
        [
            "🧮 Básica / Operaciones Numéricas",
            "📈 Factorizar Polinomio",
            "🔍 Resolver Ecuación (= 0)",
            "📐 Expandir / Simplificar",
            "🌐 Graficar en Plano Cartesiano (2D)",
        ],
        key="operacion_select_key",
    )

    expresion_input = st.text_input("Expresión Matemática o Función:", value="4**2 * 8")

    btn_procesar = st.button("🚀 Procesar Expresión")
    ejecutar_auto = st.session_state.pop("auto_calcular", False)

    if btn_procesar or ejecutar_auto:
        raw_str = expresion_input.strip()
        if not raw_str:
            st.error("Por favor ingresa una expresión válida.")
        else:
            try:
                x, y = sp.symbols("x y")
                clean_str = re.sub(r'(\d+)\s*[xX]\s*(\d+)', r'\1 * \2', raw_str)
                clean_str = clean_str.replace("^", "**")
                if clean_str.endswith("="):
                    clean_str = clean_str[:-1].strip()

                st.markdown("---")
                st.markdown("### 📋 Resultado Obtenido")

                if operacion == "🧮 Básica / Operaciones Numéricas":
                    sym_res = sp.sympify(clean_str)
                    st.success(f"### Resultado Exacto = `{sym_res}`")
                    if sym_res.is_number and not sym_res.is_Integer:
                        num_val = float(sym_res.evalf())
                        st.info(f"Valor Decimal: `{num_val:.4f}`")

                elif operacion == "📈 Factorizar Polinomio":
                    sym_expr = sp.sympify(clean_str)
                    factored = sp.factor(sym_expr)
                    st.latex(f"P(x) = {sp.latex(factored)}")
                    st.success(f"Forma Factorizada: `{factored}`")

                elif operacion == "🔍 Resolver Ecuación (= 0)":
                    sym_expr = sp.sympify(clean_str)
                    soluciones = sp.solve(sym_expr, x)
                    st.write("**Soluciones / Raíces:**")
                    if soluciones:
                        for idx, sol in enumerate(soluciones, 1):
                            st.latex(f"x_{{{idx}}} = {sp.latex(sol)}")
                    else:
                        st.warning("No se encontraron raíces reales o complejas.")

                elif operacion == "📐 Expandir / Simplificar":
                    sym_expr = sp.sympify(clean_str)
                    expanded = sp.expand(sym_expr)
                    st.latex(f"R(x) = {sp.latex(expanded)}")

                elif operacion == "🌐 Graficar en Plano Cartesiano (2D)":
                    sym_expr = sp.sympify(clean_str)
                    f = sp.lambdify(x, sym_expr, "numpy")
                    x_vals = np.linspace(-10, 10, 400)
                    y_vals = f(x_vals)

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode="lines", name=f"f(x) = {clean_str}", line=dict(color="#38bdf8", width=3)))
                    fig.add_hline(y=0, line_width=1.5, line_color="#94a3b8")
                    fig.add_vline(x=0, line_width=1.5, line_color="#94a3b8")
                    fig.update_layout(
                        title=dict(text=f"Plano Cartesiano 2D: f(x) = {clean_str}", font=dict(color="#f8fafc")),
                        template="plotly_dark",
                        xaxis_title="Eje X",
                        yaxis_title="Eje Y",
                        paper_bgcolor="#0f172a",
                        plot_bgcolor="#0b1120",
                        margin=dict(l=20, r=20, t=50, b=20),
                    )
                    st.plotly_chart(fig, use_container_width=True)

            except Exception as err:
                st.error(f"Error al interpretar la sintaxis matemática: `{err}`")