
import pandas as pd
import streamlit as st

from allocation import allocate_resources


st.set_page_config(
    page_title="OpenRelief",
    page_icon="🌍",
    layout="wide",
)

st.title("🌍 OpenRelief")
st.subheader("Every resource. The right place. Less left unmet.")

st.write(
    "An open-source resource allocation planner for community drives, "
    "charities, schools, and relief organizations."
)

st.info(
    "OpenRelief supports planning, not deciding who deserves help. "
    "Check your information and review every recommendation before "
    "distributing resources."
)

# Example data so first-time users can explore the app.
sample_stock = pd.DataFrame(
    [
        {"item": "Books", "quantity": 100},
        {"item": "Notebooks", "quantity": 60},
        {"item": "Winter coats", "quantity": 25},
    ]
)

sample_needs = pd.DataFrame(
    [
        {
            "recipient": "Community School A",
            "item": "Books",
            "needed": 40,
            "already_has": 10,
            "priority": 5,
            "max_can_receive": 40,
        },
        {
            "recipient": "Community School B",
            "item": "Books",
            "needed": 50,
            "already_has": 5,
            "priority": 4,
            "max_can_receive": 45,
        },
        {
            "recipient": "Community School A",
            "item": "Notebooks",
            "needed": 30,
            "already_has": 5,
            "priority": 4,
            "max_can_receive": 30,
        },
        {
            "recipient": "Community Centre C",
            "item": "Winter coats",
            "needed": 35,
            "already_has": 5,
            "priority": 5,
            "max_can_receive": 25,
        },
    ]
)

st.markdown("### 1. Available resources")
st.caption(
    "Enter each resource and the number of usable units available."
)

stock = st.data_editor(
    sample_stock,
    num_rows="dynamic",
    use_container_width=True,
    key="stock_editor",
    column_config={
        "item": st.column_config.TextColumn("Resource name"),
        "quantity": st.column_config.NumberColumn(
            "Available quantity", min_value=0, step=1
        ),
    },
)

st.markdown("### 2. Recipient needs")
st.caption(
    "Priority: 1 = lower urgency, 5 = highest urgency. "
    "Maximum they can receive prevents over-allocation."
)

needs = st.data_editor(
    sample_needs,
    num_rows="dynamic",
    use_container_width=True,
    key="needs_editor",
    column_config={
        "recipient": st.column_config.TextColumn("Recipient"),
        "item": st.column_config.TextColumn("Resource needed"),
        "needed": st.column_config.NumberColumn(
            "Total needed", min_value=0, step=1
        ),
        "already_has": st.column_config.NumberColumn(
            "Already has", min_value=0, step=1
        ),
        "priority": st.column_config.NumberColumn(
            "Priority (1–5)", min_value=1, max_value=5, step=1
        ),
        "max_can_receive": st.column_config.NumberColumn(
            "Maximum they can receive", min_value=0, step=1
        ),
    },
)

st.markdown("### 3. Choose an allocation strategy")

strategy_label = st.radio(
    "How should resources be allocated?",
    options=["Need-based", "Equal distribution"],
    horizontal=True,
    help=(
        "Need-based considers priority first. Equal distribution shares "
        "available units in rounds among eligible recipients."
    ),
)

strategy = (
    "need-based"
    if strategy_label == "Need-based"
    else "equal-distribution"
)

if st.button("Generate allocation plan", type="primary", use_container_width=True):
    try:
        results = allocate_resources(stock, needs, strategy=strategy)

        st.session_state["allocation_results"] = results
        st.session_state["allocation_strategy"] = strategy_label

    except (ValueError, KeyError, TypeError) as error:
        st.error(f"Please check your entries: {error}")
        st.session_state.pop("allocation_results", None)

if "allocation_results" in st.session_state:
    results = st.session_state["allocation_results"]

    st.markdown("---")
    st.markdown("## Your allocation plan")

    total_allocated = int(results["Allocated"].sum())
    total_unmet = int(results["Unmet need"].sum())
    total_leftover = int(
        results.groupby("Item")["Leftover stock"].first().sum()
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Units allocated", f"{total_allocated:,}")
    col2.metric("Units of unmet need", f"{total_unmet:,}")
    col3.metric("Units left over", f"{total_leftover:,}")

    st.caption(
        f"Strategy used: {st.session_state['allocation_strategy']}"
    )

    st.dataframe(results, use_container_width=True, hide_index=True)

    csv = results.to_csv(index=False).encode("utf-8")

    st.download_button(
        label="Download allocation report (CSV)",
        data=csv,
        file_name="openrelief_allocation.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.markdown("### Unmet needs")
    unmet = results[results["Unmet need"] > 0]

    if unmet.empty:
        st.success("All recorded shortages have been covered within the limits provided.")
    else:
        st.warning(
            "These recorded needs still require resources. "
            "Consider additional donations or review the leftover stock."
        )
        st.dataframe(
            unmet[["Recipient", "Item", "Unmet need", "Priority"]],
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("### Allocation by resource")
    chart_data = results.groupby("Item")["Allocated"].sum()
    st.bar_chart(chart_data)

st.markdown("---")
st.caption(
    "OpenRelief is an open-source planning prototype. "
    "Recommendations depend on the accuracy of the information entered. "
    "Review results before making real-world distribution decisions."
)

