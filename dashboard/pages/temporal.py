import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def render(reg_trend: pd.DataFrame, donation_trend: pd.DataFrame, season_idx: pd.DataFrame):
    st.title("Temporal Analysis")
    st.caption(
        "Sequential-mining substitute: since the dataset lacks per-donation "
        "event logs, this page mines time as the primary axis instead "
        "(trend, seasonality, forecast). See reports/scope_note.md."
    )

    st.subheader("Registration trend")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=reg_trend["month"], y=reg_trend["registrations"], name="Monthly registrations"))
    fig.add_trace(go.Scatter(x=reg_trend["month"], y=reg_trend["rolling_3mo_avg"], name="3-month rolling avg"))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Donation activity trend (proxy via Last_Donation_Date)")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=donation_trend["month"], y=donation_trend["donations_recorded"], name="Monthly donations"))
    fig.add_trace(go.Scatter(x=donation_trend["month"], y=donation_trend["rolling_3mo_avg"], name="3-month rolling avg"))
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Seasonal index")
    st.caption("Values > 1.0 indicate an above-average donation month.")
    month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    season_idx = season_idx.copy()
    season_idx["month_name"] = season_idx["month_num"].apply(lambda m: month_names[m - 1])
    fig = px.bar(season_idx.sort_values("month_num"), x="month_name", y="seasonal_index",
                 title="Seasonal Donation Index by Month")
    fig.add_hline(y=1.0, line_dash="dash", annotation_text="Average")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Forecast")
    st.info(
        "Run `src.temporal.trend_analysis.forecast_arima` / `forecast_prophet` "
        "in a notebook and export the forecast to data/processed/forecast.csv "
        "to wire it into this page. Left out of the default pipeline run "
        "since ARIMA order should be tuned per-series (check ACF/PACF first)."
    )
