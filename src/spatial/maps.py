"""Milestone 9: Folium map builders — used by the dashboard and for
exporting standalone HTML maps into reports/figures/."""

import folium
from folium.plugins import HeatMap, MarkerCluster
import pandas as pd

TN_CENTER = [10.9, 78.6]   # rough geographic center of Tamil Nadu


def blood_bank_map(blood_banks: pd.DataFrame, lat_col="latitude", lon_col="longitude") -> folium.Map:
    m = folium.Map(location=TN_CENTER, zoom_start=7, tiles="cartodbpositron")
    cluster = MarkerCluster().add_to(m)

    for _, row in blood_banks.dropna(subset=[lat_col, lon_col]).iterrows():
        popup = f"<b>{row.get('h_name', 'Blood Bank')}</b><br>{row.get('district', '')}"
        folium.Marker(
            location=[row[lat_col], row[lon_col]],
            popup=popup,
            icon=folium.Icon(color="red", icon="tint", prefix="fa"),
        ).add_to(cluster)
    return m


def donor_density_heatmap(donors_with_coords: pd.DataFrame, lat_col="latitude", lon_col="longitude") -> folium.Map:
    """Requires donor rows to have lat/lon — if donors only have City/District,
    join district centroid coordinates first (see district_centroids in
    src/spatial/clustering.py or external/tn_district_centroids.csv)."""
    m = folium.Map(location=TN_CENTER, zoom_start=7, tiles="cartodbpositron")
    points = donors_with_coords.dropna(subset=[lat_col, lon_col])[[lat_col, lon_col]].values.tolist()
    HeatMap(points, radius=15, blur=20).add_to(m)
    return m


def district_choropleth(district_summary: pd.DataFrame, geojson_path: str, value_col: str,
                          key_col: str = "District") -> folium.Map:
    """Choropleth map colored by any district_summary column (e.g. BDPI score,
    donor_density_per_100k). Needs a TN district boundary GeoJSON in
    data/external/ — see README for a source link to add."""
    m = folium.Map(location=TN_CENTER, zoom_start=7, tiles="cartodbpositron")
    folium.Choropleth(
        geo_data=geojson_path,
        data=district_summary,
        columns=[key_col, value_col],
        key_on="feature.properties.district",   # adjust to match your GeoJSON's property name
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.3,
        legend_name=value_col,
    ).add_to(m)
    return m
