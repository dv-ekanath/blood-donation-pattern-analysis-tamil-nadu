import streamlit as st
import pandas as pd
import plotly.express as px


def render(district_summary: pd.DataFrame):
    st.title("Spatial Analysis")

    st.subheader("Donor density by district")
    fig = px.bar(
        district_summary.sort_values("donor_density_per_100k", ascending=True),
        x="donor_density_per_100k", y="District", orientation="h", height=800,
        title="Donors per 100k Population",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Blood bank coverage")
    fig = px.bar(
        district_summary.sort_values("population_per_blood_bank", ascending=False),
        x="District", y="population_per_blood_bank",
        title="Population per Blood Bank (higher = worse coverage)",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Interactive maps")
    st.info(
        "Blood bank cluster map and donor density heatmap render here via "
        "`src/spatial/maps.py` + `streamlit_folium.st_folium`. Requires "
        "district-level lat/lon centroids or per-donor coordinates — see "
        "`data/external/` in the README for the TN district GeoJSON to add."
    )
    # Example wiring once you have donor/blood-bank coordinates ready:
    #
    # from streamlit_folium import st_folium
    # from src.spatial.maps import blood_bank_map
    # st_folium(blood_bank_map(blood_banks_clustered), width=1200, height=600)

    st.subheader("District comparison table")
    st.dataframe(
        district_summary[[
            "District", "Population", "n_donors", "n_blood_banks",
            "donor_density_per_100k", "population_per_blood_bank", "eligible_pct",
        ]].sort_values("donor_density_per_100k"),
        use_container_width=True, hide_index=True,
    )
