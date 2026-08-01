"""Milestone 8: Temporal (sequential-substitute) analysis.

Since we lack per-donation event logs, "sequential" analysis here means:
1. Registration trend over time (monthly counts)
2. Seasonal donation pattern (which season sees more last-donations)
3. Rolling averages / trend smoothing
4. Forecasting future monthly volume (ARIMA, with Prophet as an optional extra)

See reports/scope_note.md for why this replaces PrefixSpan/SPADE/GSP.
"""

import pandas as pd
from src.utils.logger import get_logger

log = get_logger(__name__)


def monthly_registration_trend(donors: pd.DataFrame) -> pd.DataFrame:
    s = (
        donors.set_index("Registration_Date")
        .resample("MS")["Donor_ID"]
        .count()
        .rename("registrations")
        .to_frame()
    )
    s["rolling_3mo_avg"] = s["registrations"].rolling(3, min_periods=1).mean()
    return s.reset_index().rename(columns={"Registration_Date": "month"})


def monthly_donation_activity_trend(donors: pd.DataFrame) -> pd.DataFrame:
    """Uses Last_Donation_Date as a proxy for 'a donation happened this
    month' — not a full log, but the best available signal per donor."""
    valid = donors[donors["Last_Donation_Date"].notna()]
    s = (
        valid.set_index("Last_Donation_Date")
        .resample("MS")["Donor_ID"]
        .count()
        .rename("donations_recorded")
        .to_frame()
    )
    s["rolling_3mo_avg"] = s["donations_recorded"].rolling(3, min_periods=1).mean()
    return s.reset_index().rename(columns={"Last_Donation_Date": "month"})


def seasonal_index(donors: pd.DataFrame, date_col: str = "Last_Donation_Date") -> pd.DataFrame:
    """Average donation count by calendar month, normalized so 1.0 = average
    month. Values > 1 mean that month sees above-average activity."""
    valid = donors[donors[date_col].notna()].copy()
    valid["month_num"] = valid[date_col].dt.month
    monthly = valid.groupby("month_num").size().rename("count").to_frame()
    monthly["seasonal_index"] = monthly["count"] / monthly["count"].mean()
    return monthly.reset_index()


def seasonal_decompose_series(monthly_series: pd.Series, period: int = 12):
    """Wraps statsmodels seasonal_decompose. Requires >= 2 full periods
    (24 months) of data — returns None with a warning otherwise."""
    from statsmodels.tsa.seasonal import seasonal_decompose

    if len(monthly_series) < 2 * period:
        log.warning(
            f"Only {len(monthly_series)} months of data — need >= {2*period} "
            f"for reliable seasonal decomposition. Returning None."
        )
        return None
    return seasonal_decompose(monthly_series, model="additive", period=period)


def forecast_arima(monthly_series: pd.Series, steps: int = 6, order=(1, 1, 1)):
    """Simple ARIMA forecast on a monthly-indexed series. Returns a DataFrame
    with forecasted mean and confidence interval."""
    from statsmodels.tsa.arima.model import ARIMA

    model = ARIMA(monthly_series, order=order)
    fit = model.fit()
    forecast = fit.get_forecast(steps=steps)
    result = forecast.summary_frame()
    log.info(f"forecast_arima: forecasted {steps} steps ahead with order={order}")
    return result


def forecast_prophet(monthly_df: pd.DataFrame, date_col: str, value_col: str, periods: int = 6):
    """Optional Prophet forecast. monthly_df needs columns [date_col, value_col].
    Falls back gracefully (returns None) if prophet isn't installed —
    ARIMA above is the required baseline; Prophet is a nice-to-have comparison.
    """
    try:
        from prophet import Prophet
    except ImportError:
        log.warning("prophet not installed — skipping. `pip install prophet` to enable.")
        return None

    df = monthly_df.rename(columns={date_col: "ds", value_col: "y"})[["ds", "y"]]
    m = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
    m.fit(df)
    future = m.make_future_dataframe(periods=periods, freq="MS")
    forecast = m.predict(future)
    return forecast
