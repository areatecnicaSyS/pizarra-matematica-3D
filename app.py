import numpy as np
import plotly.graph_objects as go
import streamlit as st
import sympy as sp

# Configuración de la página con el logo corporativo como favicon
st.set_page_config(
    page_title="Pizarra Matemática - Área Técnica",
    page_icon="logo.jpg",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Menú lateral con el logo corporativo
with st.sidebar:
  st.image("logo.jpg", use_container_width=True)
  st.markdown("---")
  modulo = st.selectbox(
      "Seleccionar Herramienta",
      [
          "Visualizador 3D de Funciones",
          "Factorización y Álgebra",
          "Resolución de Ecuaciones",
      ],
  )

st.title("🧮 Pizarra Matemática con Álgebra y Modelado 3D")
st.markdown(
    "Herramienta interactiva desarrollada para la resolución, factorización y"
    " visualización de funciones matemáticas en tiempo real."
)

# Definir símbolos
x, y = sp.symbols("x y")

if modulo == "Visualizador 3D de Funciones":
  st.subheader("📊 Modelado Tridimensional Dinámico")

  col1, col2 = st.sidebar.columns(2)
  a = col1.slider("Amplitud (A)", 0.5, 5.0, 1.0)
  b = col2.slider("Frecuencia (B)", -5.0, 5.0, 0.0)

  # Generación de malla 3D
  x_vals = np.linspace(-5, 5, 50)
  y_vals = np.linspace(-5, 5, 50)
  X, Y = np.meshgrid(x_vals, y_vals)
  Z = a * np.sin(np.sqrt(X**2 + Y**2) + b)

  fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale="Viridis")])
  fig.update_layout(
      title="Superficie Matemática Generada",
      autosize=True,
      scene=dict(
          xaxis_title="Eje X", yaxis_title="Eje Y", zaxis_title="Eje Z"
      ),
      height=600,
  )
  st.plotly_chart(fig, use_container_width=True)

elif modulo == "Factorización y Álgebra":
  st.subheader("⚙️ Factorización de Polinomios")

  expresion_str = st.text_input(
      "Introduce la expresión algebraica (ej: x**2 - 9 o 2*x**2 + 5*x + 2):",
      "x**2 - 9",
  )

  if expresion_str:
    try:
      expr = sp.sympify(expresion_str)
      resultado = sp.factor(expr)

      st.markdown("### Resultados:")
      st.latex(f"\\text{{Expresión original: }} {sp.latex(expr)}")
      st.latex(f"\\text{{Forma factorizada: }} {sp.latex(resultado)}")
    except Exception as e:
      st.error(
          f"Error al interpretar la expresión. Revisa la sintaxis. Detalle: {e}"
      )

elif modulo == "Resolución de Ecuaciones":
  st.subheader("🎯 Resolución de Ecuaciones Básicas (= 0)")

  ecuacion_str = st.text_input(
      "Introduce la ecuación en función de x (ej: x**2 - 4):", "x**2 - 4"
  )

  if ecuacion_str:
    try:
      expr = sp.sympify(ecuacion_str)
      soluciones = sp.solve(expr, x)

      st.markdown("### Resultados:")
      st.latex(f"\\text{{Ecuación: }} {sp.latex(expr)} = 0")
      st.write(f"**Raíces encontradas para $x$:** {soluciones}")
    except Exception as e:
      st.error(
          f"Error al procesar la ecuación. Revisa la sintaxis. Detalle: {e}"
      )