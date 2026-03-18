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
    "antes de quedarse sin margen."
)

st.markdown("---")
st.subheader("Configura tu escenario")

capital_real = st.number_input(
    "Capital real que puedes arriesgar ($)",
    min_value=1.0,
    value=4500.0,
    step=100.0,
    format="%.2f",
    help="Ejemplo: si la cuenta dice 150k, pero realmente solo puedes perder 4,500, aquí va 4,500.",
)

tipo_riesgo = st.selectbox(
    "Tipo de riesgo",
    ["Riesgo porcentual (%)", "Riesgo fijo ($)"],
)

if tipo_riesgo == "Riesgo porcentual (%)":
    riesgo_pct = st.number_input(
        "Riesgo por operación (%)",
        min_value=0.01,
        max_value=99.99,
        value=5.0,
        step=0.1,
        format="%.2f",
    )
else:
    riesgo_fijo = st.number_input(
        "Riesgo por operación ($)",
        min_value=1.0,
        value=300.0,
        step=10.0,
        format="%.2f",
    )

st.markdown("---")


def mensaje_supervivencia(perdidas: int) -> str:
    if perdidas <= 5:
        return "⚠️ Tu margen es bastante ajustado. Conviene operar con mucha precisión."
    elif perdidas <= 15:
        return "👍 Tienes un margen razonable, pero sigue siendo importante cuidar cada entrada."
    return "🛡️ Tu capital tiene buen margen de resistencia. Aun así, la disciplina sigue mandando."


def calcular_modo_porcentaje(capital: float, riesgo_porcentaje: float):
    riesgo_decimal = riesgo_porcentaje / 100

    if riesgo_decimal <= 0:
        return None, "El riesgo porcentual debe ser mayor que 0."
    if riesgo_decimal >= 1:
        return None, "El riesgo porcentual debe ser menor que 100%."

    balance_actual = capital
    historial = []
    contador = 0

    # Parar cuando el capital llegue a $1 o menos
    while balance_actual > 1 and contador < 10000:
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

    df = pd.DataFrame(historial)

    return {
        "perdidas": contador,
        "capital_final": round(balance_actual, 2),
        "df": df,
        "descripcion": (
            f"Si arriesgas **{riesgo_porcentaje:.2f}%** por operación sobre el capital restante, "
            f"podrías soportar aproximadamente **{contador} pérdidas consecutivas** "
            f"hasta quedar con **$1 o menos**."
        ),
    }, None


def calcular_modo_fijo(capital: float, riesgo_dolares: float):
    if riesgo_dolares <= 0:
        return None, "El riesgo fijo debe ser mayor que 0."
    if riesgo_dolares > capital:
        return None, "El riesgo fijo no puede ser mayor que el capital real disponible."

    perdidas_posibles = math.floor(capital / riesgo_dolares)
    sobrante = capital - (perdidas_posibles * riesgo_dolares)

    historial = []
    balance_actual = capital

    for i in range(1, perdidas_posibles + 1):
        balance_actual -= riesgo_dolares
        historial.append(
            {
                "Trade perdido #": i,
                "Pérdida ($)": round(riesgo_dolares, 2),
                "Capital restante ($)": round(balance_actual, 2),
                "Capital restante (%)": round((balance_actual / capital) * 100, 2),
            }
        )

    df = pd.DataFrame(historial)

    return {
        "perdidas": perdidas_posibles,
        "capital_final": round(sobrante, 2),
        "df": df,
        "descripcion": (
            f"Si pierdes **${riesgo_dolares:,.2f}** por operación, "
            f"podrías soportar **{perdidas_posibles} pérdidas consecutivas** "
            f"antes de quedarte sin margen suficiente para otra pérdida completa."
        ),
    }, None


st.subheader("Resumen")

if tipo_riesgo == "Riesgo porcentual (%)":
    resultado, error = calcular_modo_porcentaje(capital_real, riesgo_pct)
else:
    resultado, error = calcular_modo_fijo(capital_real, riesgo_fijo)

if error:
    st.error(error)
else:
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Pérdidas consecutivas posibles", resultado["perdidas"])

    with col2:
        if tipo_riesgo == "Riesgo porcentual (%)":
            st.metric("Capital final", f"${resultado['capital_final']:,.2f}")
        else:
            st.metric("Capital restante", f"${resultado['capital_final']:,.2f}")

    st.info(mensaje_supervivencia(resultado["perdidas"]))
    st.write(resultado["descripcion"])

    st.markdown("---")
    st.subheader("Detalle de la simulación")
    st.dataframe(
        resultado["df"],
        use_container_width=True,
        hide_index=True,
    )
