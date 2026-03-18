import math
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Calculadora de Supervivencia del Trader",
    page_icon="🛡️",
    layout="centered",
)

st.title("🛡️ Calculadora de Supervivencia del Trader")
st.write(
    "Descubre cuántas pérdidas consecutivas puede soportar tu capital real "
    "antes de llegar a tu límite mínimo."
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }
    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,0.20);
        border-radius: 12px;
        padding: 12px;
        background-color: rgba(255,255,255,0.02);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown("### Configura tu escenario")

col1, col2, col3 = st.columns([1.2, 1, 1])

with col1:
    capital_real = st.number_input(
        "Capital real ($)",
        min_value=1.0,
        value=4500.0,
        step=100.0,
        format="%.2f",
        help="Tu colchón real de pérdida. Ejemplo: 4500.",
    )

with col2:
    capital_minimo = st.number_input(
        "Capital mínimo ($)",
        min_value=0.0,
        value=10.0,
        step=1.0,
        format="%.2f",
        help="Cuando el capital llegue a este nivel o menos, la simulación se detiene.",
    )

with col3:
    tipo_riesgo = st.selectbox(
        "Tipo de riesgo",
        ["Riesgo porcentual (%)", "Riesgo fijo ($)"],
    )

if capital_minimo >= capital_real:
    st.warning("El capital mínimo debe ser menor que el capital real para que la simulación tenga sentido.")

col4, col5 = st.columns([1, 1])

riesgo_pct = None
riesgo_fijo = None

with col4:
    if tipo_riesgo == "Riesgo porcentual (%)":
        riesgo_pct = st.number_input(
            "Riesgo por operación (%)",
            min_value=0.01,
            max_value=99.99,
            value=3.0,
            step=0.1,
            format="%.2f",
        )
    else:
        st.text_input("Riesgo por operación (%)", value="No aplica", disabled=True)

with col5:
    if tipo_riesgo == "Riesgo fijo ($)":
        riesgo_fijo = st.number_input(
            "Riesgo por operación ($)",
            min_value=0.01,
            value=300.0,
            step=10.0,
            format="%.2f",
        )
    else:
        st.text_input("Riesgo por operación ($)", value="No aplica", disabled=True)

st.markdown("---")


def mensaje_supervivencia(perdidas: int) -> str:
    if perdidas <= 5:
        return "⚠️ Tu margen es ajustado. Conviene operar con mucha precisión."
    elif perdidas <= 15:
        return "👍 Tienes un margen razonable, pero sigue siendo clave cuidar cada entrada."
    return "🛡️ Tu capital tiene buena resistencia. Aun así, la disciplina sigue mandando."


def calcular_modo_porcentaje(capital: float, riesgo_porcentaje: float, capital_min: float):
    riesgo_decimal = riesgo_porcentaje / 100

    if riesgo_decimal <= 0:
        return None, "El riesgo porcentual debe ser mayor que 0."
    if riesgo_decimal >= 1:
        return None, "El riesgo porcentual debe ser menor que 100%."
    if capital_min >= capital:
        return None, "El capital mínimo debe ser menor que el capital real."

    balance_actual = capital
    historial = []
    contador = 0

    while balance_actual > capital_min and contador < 10000:
        perdida = balance_actual * riesgo_decimal
        balance_actual -= perdida
        contador += 1

        historial.append(
            {
                "Trade perdido #": contador,
                "Pérdida ($)": round(perdida, 2),
                "Capital restante ($)": round(balance_actual, 2),
                "Capital restante (%)": round((balance_actual / capital) * 100, 2),
            }
        )

        if balance_actual <= capital_min:
            break

    df = pd.DataFrame(historial)

    return {
        "perdidas": contador,
        "capital_final": round(balance_actual, 2),
        "df": df,
        "descripcion": (
            f"Si arriesgas **{riesgo_porcentaje:.2f}%** por operación sobre el capital restante, "
            f"podrías soportar aproximadamente **{contador} pérdidas consecutivas** "
            f"hasta llegar a **${capital_min:,.2f} o menos**."
        ),
    }, None


def calcular_modo_fijo(capital: float, riesgo_dolares: float, capital_min: float):
    if riesgo_dolares <= 0:
        return None, "El riesgo fijo debe ser mayor que 0."
    if capital_min >= capital:
        return None, "El capital mínimo debe ser menor que el capital real."

    historial = []
    balance_actual = capital
    contador = 0

    while balance_actual - riesgo_dolares >= capital_min and contador < 10000:
        balance_actual -= riesgo_dolares
        contador += 1

        historial.append(
            {
                "Trade perdido #": contador,
                "Pérdida ($)": round(riesgo_dolares, 2),
                "Capital restante ($)": round(balance_actual, 2),
                "Capital restante (%)": round((balance_actual / capital) * 100, 2),
            }
        )

    df = pd.DataFrame(historial)

    return {
        "perdidas": contador,
        "capital_final": round(balance_actual, 2),
        "df": df,
        "descripcion": (
            f"Si pierdes **${riesgo_dolares:,.2f}** por operación, "
            f"podrías soportar **{contador} pérdidas consecutivas** "
            f"antes de tocar tu límite mínimo de **${capital_min:,.2f}**."
        ),
    }, None


st.subheader("Resumen")

if tipo_riesgo == "Riesgo porcentual (%)":
    resultado, error = calcular_modo_porcentaje(capital_real, riesgo_pct, capital_minimo)
else:
    resultado, error = calcular_modo_fijo(capital_real, riesgo_fijo, capital_minimo)

if error:
    st.error(error)
else:
    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric("Pérdidas posibles", resultado["perdidas"])

    with m2:
        st.metric("Capital final", f"${resultado['capital_final']:,.2f}")

    with m3:
        st.metric("Límite mínimo", f"${capital_minimo:,.2f}")

    st.info(mensaje_supervivencia(resultado["perdidas"]))
    st.write(resultado["descripcion"])

    st.markdown("---")
    st.subheader("Detalle de la simulación")
    st.dataframe(
        resultado["df"],
        use_container_width=True,
        hide_index=True,
    )
