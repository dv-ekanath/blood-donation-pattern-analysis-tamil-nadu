import streamlit as st
import pandas as pd
import plotly.express as px


def render(recommendations: pd.DataFrame, district_summary: pd.DataFrame):
    st.title("Blood Donation Priority Index (BDPI) & Recommendations")

    st.subheader("District ranking")
    fig = px.bar(
        recommendations.sort_values("BDPI", ascending=True),
        x="BDPI", y="District", orientation="h", height=800, color="Priority_Band",
        title="BDPI Score by District",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Filter by priority")
    bands = st.multiselect(
        "Priority band", options=recommendations["Priority_Band"].unique(),
        default=list(recommendations["Priority_Band"].unique()),
    )
    filtered = recommendations[recommendations["Priority_Band"].isin(bands)]

    for _, row in filtered.sort_values("Rank").iterrows():
        with st.expander(f"#{row['Rank']} — {row['District']} (BDPI: {row['BDPI']})"):
            st.markdown(f"**Priority band:** {row['Priority_Band']}")
            st.markdown(f"**Recommendation:** {row['Recommendation']}")
            st.markdown(f"**Explanation:** {row['Explanation']}")

    st.download_button(
        "Download full recommendations (CSV)",
        data=recommendations.to_csv(index=False).encode("utf-8"),
        file_name="district_recommendations.csv",
        mime="text/csv",
    )
