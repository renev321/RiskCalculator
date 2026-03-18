import math
import streamlit as st

st.set_page_config(
    page_title="Account Blow-Up Calculator",
    page_icon="📉",
    layout="centered",
)

st.title("📉 Account Blow-Up Calculator")
st.write(
    "Estimate how many consecutive losing trades it would take to heavily damage "
    "or nearly blow up an account based on a fixed percentage risk per trade."
)

with st.sidebar:
    st.header("Inputs")

    account_size = st.number_input(
        "Account size ($)",
        min_value=1.0,
        value=50000.0,
        step=1000.0,
        format="%.2f",
    )

    risk_percent = st.number_input(
        "Risk per trade (%)",
        min_value=0.01,
        max_value=99.99,
        value=1.0,
        step=0.1,
        format="%.2f",
    )

    blowup_threshold = st.slider(
        "Blow-up threshold (% of original account remaining)",
        min_value=1,
        max_value=50,
        value=10,
        step=1,
        help="Example: 10 means the account is considered basically blown once only 10% remains.",
    )

    max_losses_to_show = st.slider(
        "Max losses to simulate",
        min_value=10,
        max_value=500,
        value=100,
        step=10,
    )

risk_decimal = risk_percent / 100
threshold_decimal = blowup_threshold / 100
threshold_balance = account_size * threshold_decimal

st.subheader("How the math works")
st.latex(r"Balance_n = InitialBalance \times (1 - risk)^n")

if risk_decimal <= 0:
    st.warning("Please use a risk greater than 0%.")
elif risk_decimal >= 1:
    st.error("Risk per trade must be below 100% for this calculation.")
else:
    losses_to_threshold = math.ceil(
        math.log(threshold_balance / account_size) / math.log(1 - risk_decimal)
    )

    current_balance = account_size
    balances = []

    for loss_number in range(1, max_losses_to_show + 1):
        loss_amount = current_balance * risk_decimal
        current_balance -= loss_amount

        balances.append(
            {
                "Loss Number": loss_number,
                "Loss Amount ($)": round(loss_amount, 2),
                "Remaining Balance ($)": round(current_balance, 2),
                "Remaining (%)": round((current_balance / account_size) * 100, 2),
            }
        )

    st.subheader("Result")

    col1, col2 = st.columns(2)
    col1.metric("Losses to threshold", losses_to_threshold)
    col2.metric("Threshold balance", f"${threshold_balance:,.2f}")

    st.info(
        f"With an account of ${account_size:,.2f} risking {risk_percent:.2f}% per loss, "
        f"it would take about {losses_to_threshold} consecutive losses to fall to "
        f"{blowup_threshold}% of the original balance."
    )

    st.subheader("Simulation Table")
    st.dataframe(balances, use_container_width=True)

    if losses_to_threshold <= max_losses_to_show:
        threshold_row = next(
            (row for row in balances if row["Loss Number"] == losses_to_threshold),
            None,
        )
        if threshold_row:
            st.success(
                f"At loss #{losses_to_threshold}, the balance would be about "
                f"${threshold_row['Remaining Balance ($)']:,.2f} "
                f"({threshold_row['Remaining (%)']}% remaining)."
            )
    else:
        st.warning(
            "The threshold was not reached within the current simulation range. "
            "Increase 'Max losses to simulate' to see it in the table."
        )
