import math
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Calculadora de Supervivencia del Trader",
    page_icon="🛡️",
    layout="centered",
)

# =========================================================
# Estilos
# =========================================================
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
        max-width: 1050px;
    }
    div[data-testid="stMetric"] {
        border: 1px solid rgba(128,128,128,0.18);
        border-radius: 14px;
        padding: 12px;
        background-color: rgba(255,255,255,0.02);
    }
    .section-card {
        padding: 1rem 1rem 0.8rem 1rem;
        border: 1px solid rgba(128,128,128,0.16);
        border-radius: 16px;
        background: rgba(255,255,255,0.015);
        margin-bottom: 1rem;
    }
    .info-box {
        padding: 16px 18px;
        border-radius: 16px;
        border: 1px solid rgba(128,128,128,0.18);
        background: rgba(255,255,255,0.02);
        line-height: 1.6;
        font-size: 0.98rem;
    }
    .logo-wrap {
        display: flex;
        justify-content: center;
        margin-bottom: 0.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# Logo
# =========================================================
st.image("LogoWLf.png", width=260)

st.title("🛡️ Calculadora de Supervivencia del Trader")
st.write(
    "Controla tu riesgo y revisa si tu combinación de Win Rate y Reward/Risk "
    "tiene verdadero potencial de ser rentable."
)

# =========================================================
# Funciones
# =========================================================
def mensaje_supervivencia(perdidas: int) -> str:
    if perdidas <= 5:
        return "⚠️ Tu margen es ajustado. Aquí no toca improvisar ni ponerse creativo de más."
    elif perdidas <= 15:
        return "👍 Tienes un margen razonable. Hay aire, pero igual conviene respetar el plan."
    return "🛡️ Tu capital tiene buena resistencia. Muy bien... pero no es licencia para volverse loco."


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


def clasificar_rr_winrate(winrate_pct: float, rr: float, tolerancia: float = 1e-9):
    expectancy = (winrate_pct / 100 * rr) - ((1 - winrate_pct / 100) * 1)

    if abs(expectancy) <= tolerancia:
        return "Break-even"
    elif expectancy > 0:
        return "Rentable"
    return "No rentable"


def color_rr(valor: str):
    if valor == "Rentable":
        return "background-color: rgba(46, 204, 113, 0.80); color: black; font-weight: 600;"
    if valor == "Break-even":
        return "background-color: rgba(241, 196, 15, 0.88); color: black; font-weight: 600;"
    return "background-color: rgba(231, 76, 60, 0.84); color: white; font-weight: 600;"


def crear_tabla_rr(winrates, rrs):
    data = {}
    for wr in winrates:
        data[f"{wr}%"] = [clasificar_rr_winrate(wr, rr) for rr in rrs]

    df = pd.DataFrame(data, index=[f"{rr}:1" for rr in rrs])
    df.index.name = "RR"
    return df


# =========================================================
# Escenario de riesgo
# =========================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown("### Configura tu escenario")

c1, c2, c3 = st.columns([1.2, 1, 1])

with c1:
    capital_real = st.number_input(
        "Capital real ($)",
        min_value=1.0,
        value=4500.0,
        step=100.0,
        format="%.2f",
        help="Tu colchón real de pérdida. Ejemplo: 4500.",
    )

with c2:
    capital_minimo = st.number_input(
        "Capital mínimo ($)",
        min_value=0.0,
        value=10.0,
        step=1.0,
        format="%.2f",
        help="Cuando el capital llegue a este nivel o menos, la simulación se detiene.",
    )

with c3:
    tipo_riesgo = st.selectbox(
        "Tipo de riesgo",
        ["Riesgo porcentual (%)", "Riesgo fijo ($)"],
    )

c4, c5 = st.columns(2)

riesgo_pct = None
riesgo_fijo = None

with c4:
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

with c5:
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

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# Resultado riesgo
# =========================================================
st.subheader("Resumen del riesgo")

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

    st.subheader("Detalle de la simulación")
    st.dataframe(
        resultado["df"],
        use_container_width=True,
        hide_index=True,
    )

st.markdown("---")

# =========================================================
# Tabla RR / Win Rate
# =========================================================
st.markdown('<div class="section-card">', unsafe_allow_html=True)
st.markdown("### Tabla RR vs Win Rate")
st.write(
    "Esta tabla te ayuda a validar si una combinación de **Reward/Risk** y "
    "**porcentaje de acierto** tiene expectativa positiva."
)

rr_col1, rr_col2 = st.columns(2)

with rr_col1:
    max_rr = st.slider(
        "RR máximo a mostrar",
        min_value=2,
        max_value=20,
        value=10,
        step=1,
    )

with rr_col2:
    winrate_inicio = st.selectbox(
        "Win Rate inicial",
        options=[10, 20, 30, 40, 50, 60, 70, 80],
        index=0,
    )

winrates = list(range(winrate_inicio, 81, 10))
rrs = list(range(1, max_rr + 1))

df_rr = crear_tabla_rr(winrates, rrs)
styled_rr = df_rr.style.map(color_rr)

st.dataframe(
    styled_rr,
    use_container_width=True,
)

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="info-box">
        <b>💡 Cómo leer esta tabla</b><br><br>
        <b>• Columnas:</b> representan tu porcentaje de acierto o <i>Win Rate</i>.<br>
        <b>• Filas:</b> representan tu relación <i>Reward/Risk</i> (por ejemplo, 3:1 significa que ganas 3 por cada 1 que arriesgas).<br>
        <b>• Verde:</b> tu combinación tiene expectativa positiva. Bien ahí, las matemáticas te acompañan.<br>
        <b>• Amarillo:</b> estás en break-even. O sea, sobrevives... pero no para presumir mucho todavía.<br>
        <b>• Rojo:</b> la combinación no es rentable a largo plazo. Mejor descubrirlo aquí que con la cuenta llorando.<br><br>
        <b>Idea clave:</b> no siempre necesitas acertar muchísimo. A veces, con un buen RR, un win rate modesto ya puede funcionar bastante bien.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("</div>", unsafe_allow_html=True)
