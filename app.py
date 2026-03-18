import math
import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Calculadora de Ruina",
    page_icon="💀",
    layout="centered",
)

st.title("💀 Calculadora de Ruina del Trader")
st.write(
    "Descubre cuántas pérdidas consecutivas puedes soportar antes de mandar la cuenta al más allá."
)

st.markdown("---")

# =========================
# Inputs
# =========================
st.subheader("Datos de entrada")

capital_real = st.number_input(
    "Capital real disponible para perder ($)",
    min_value=1.0,
    value=4500.0,
    step=100.0,
    format="%.2f",
    help="Ejemplo: si la cuenta dice 150k, pero realmente solo puedes perder 4,500, aquí va 4,500.",
)

col1, col2 = st.columns(2)

with col1:
    riesgo_pct = st.number_input(
        "Riesgo porcentual por operación (%)",
        min_value=0.01,
        max_value=100.0,
        value=5.0,
        step=0.1,
        format="%.2f",
    )

with col2:
    riesgo_fijo = st.number_input(
        "Riesgo fijo por operación ($)",
        min_value=1.0,
        value=300.0,
        step=10.0,
        format="%.2f",
    )

max_filas = st.slider(
    "Máximo de filas a mostrar en las tablas",
    min_value=5,
    max_value=100,
    value=20,
    step=5,
)

st.markdown("---")


# =========================
# Helper functions
# =========================
def calcular_modo_porcentaje(capital: float, riesgo_porcentaje: float):
    riesgo_decimal = riesgo_porcentaje / 100

    if riesgo_decimal <= 0:
        return None, "El riesgo porcentual debe ser mayor que 0."
    if riesgo_decimal >= 1:
        return None, "El riesgo porcentual debe ser menor que 100%."

    balance_actual = capital
    historial = []
    contador = 0

    # Definimos ruina práctica cuando queda menos de 1 centavo
    while balance_actual > 0.01 and contador < 10000:
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
    }, None


def mensaje_supervivencia(perdidas: int):
    if perdidas <= 5:
        return "💀 Vas muy apretado. Un mal día y se apaga la película."
    elif perdidas <= 15:
        return "⚠️ Hay margen, pero no para andar regalando entradas."
    else:
        return "🛡️ Tienes aire, pero tampoco te vengas arriba."


# =========================
# Calculations
# =========================
resultado_pct, error_pct = calcular_modo_porcentaje(capital_real, riesgo_pct)
resultado_fijo, error_fijo = calcular_modo_fijo(capital_real, riesgo_fijo)

st.subheader("Resultados")

col_pct, col_fijo = st.columns(2)

with col_pct:
    st.markdown("### 📊 Modo porcentual")
    if error_pct:
        st.error(error_pct)
    else:
        st.metric(
            "Pérdidas consecutivas posibles",
            resultado_pct["perdidas"],
        )
        st.metric(
            "Capital final",
            f"${resultado_pct['capital_final']:,.2f}",
        )
        st.info(mensaje_supervivencia(resultado_pct["perdidas"]))
        st.write(
            f"Si arriesgas **{riesgo_pct:.2f}%** por operación sobre el capital restante, "
            f"podrías soportar aproximadamente **{resultado_pct['perdidas']} pérdidas consecutivas**."
        )

with col_fijo:
    st.markdown("### 💵 Modo fijo")
    if error_fijo:
        st.error(error_fijo)
    else:
        st.metric(
            "Pérdidas consecutivas posibles",
            resultado_fijo["perdidas"],
        )
        st.metric(
            "Capital sobrante",
            f"${resultado_fijo['capital_final']:,.2f}",
        )
        st.info(mensaje_supervivencia(resultado_fijo["perdidas"]))
        st.write(
            f"Si pierdes **${riesgo_fijo:,.2f}** por operación, "
            f"podrías soportar **{resultado_fijo['perdidas']} pérdidas consecutivas**."
        )

st.markdown("---")

# =========================
# Comparison
# =========================
st.subheader("Comparación rápida")

comparacion_data = {
    "Modo": ["Porcentaje (%)", "Fijo ($)"],
    "Riesgo usado": [f"{riesgo_pct:.2f}%", f"${riesgo_fijo:,.2f}"],
    "Pérdidas posibles": [
        resultado_pct["perdidas"] if resultado_pct else "N/A",
        resultado_fijo["perdidas"] if resultado_fijo else "N/A",
    ],
    "Capital final": [
        f"${resultado_pct['capital_final']:,.2f}" if resultado_pct else "N/A",
        f"${resultado_fijo['capital_final']:,.2f}" if resultado_fijo else "N/A",
    ],
}

df_comparacion = pd.DataFrame(comparacion_data)
st.dataframe(df_comparacion, use_container_width=True, hide_index=True)

st.markdown("---")

# =========================
# Tables
# =========================
st.subheader("Simulación detallada")

tab1, tab2 = st.tabs(["📊 Riesgo porcentual", "💵 Riesgo fijo"])

with tab1:
    if resultado_pct:
        st.dataframe(
            resultado_pct["df"].head(max_filas),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.warning("No se pudo generar la simulación porcentual.")

with tab2:
    if resultado_fijo:
        st.dataframe(
            resultado_fijo["df"].head(max_filas),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.warning("No se pudo generar la simulación de monto fijo.")
