import streamlit as st
import pandas as pd


def render(donors: pd.DataFrame, district_summary: pd.DataFrame, recommendations: pd.DataFrame):
    st.title("Blood Donation Pattern Analysis — Tamil Nadu")
    st.markdown(
        "M.Tech project: temporal + spatial mining of donor and blood bank "
        "data to recommend districts and timing for future donation drives."
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Donors", f"{len(donors):,}")
    c2.metric("Districts Covered", district_summary["District"].nunique())
    c3.metric("Total Blood Banks", int(district_summary["n_blood_banks"].sum()))
    c4.metric("Critical-Priority Districts",
              int((recommendations["Priority_Band"] == "Critical Priority").sum()))

    st.subheader("Top 5 priority districts")
    st.dataframe(
        recommendations.head(5)[["Rank", "District", "BDPI", "Priority_Band", "Recommendation"]],
        use_container_width=True, hide_index=True,
    )

    st.subheader("Project pipeline")
    st.markdown(
        "Raw Datasets → Cleaning → Integration → Feature Engineering → EDA → "
        "**Temporal Analysis** + **Spatial Analysis** → Spatio-Temporal Analysis "
        "→ **BDPI** → Recommendation Engine → this Dashboard."
    )
