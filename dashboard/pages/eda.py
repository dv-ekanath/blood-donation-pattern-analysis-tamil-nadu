import streamlit as st
import pandas as pd
import plotly.express as px


def render(donors: pd.DataFrame):
    st.title("Exploratory Data Analysis")

    st.subheader("Demographics")
    c1, c2, c3 = st.columns(3)
    with c1:
        fig = px.histogram(donors, x="Age", nbins=30, title="Age Distribution")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.pie(donors, names="Gender", title="Gender Distribution")
        st.plotly_chart(fig, use_container_width=True)
    with c3:
        bg_counts = donors["Blood_Group"].value_counts().reset_index()
        bg_counts.columns = ["Blood_Group", "count"]
        fig = px.bar(bg_counts, x="Blood_Group", y="count", title="Blood Group Distribution")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Donor status")
    c1, c2 = st.columns(2)
    with c1:
        fig = px.pie(donors, names="Eligible_for_Donation", title="Eligibility Split")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.pie(donors, names="Repeat_Donor", title="Repeat vs First-time Donors")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("District-wise donor counts")
    dist_counts = donors["District"].value_counts().reset_index()
    dist_counts.columns = ["District", "count"]
    fig = px.bar(dist_counts.sort_values("count", ascending=True), x="count", y="District",
                 orientation="h", height=800, title="Donors per District")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Health indicators")
    c1, c2 = st.columns(2)
    with c1:
        fig = px.histogram(donors, x="Hemoglobin_g_dL", nbins=30, title="Hemoglobin Distribution")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.pie(donors, names="Has_Medical_Condition", title="Medical Condition Present")
        st.plotly_chart(fig, use_container_width=True)
