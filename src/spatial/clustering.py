"""Milestone 9: Spatial analysis — DBSCAN clustering + KDE density.

DBSCAN here uses haversine distance so `eps` can be specified in real
kilometers (config.yaml -> spatial.dbscan_eps_km) instead of raw
degrees, which is what most tutorials get wrong for geo data.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from src.utils.config import CONFIG
from src.utils.logger import get_logger

log = get_logger(__name__)
SPATIAL_CFG = CONFIG["spatial"]

EARTH_RADIUS_KM = 6371.0


def dbscan_cluster(df: pd.DataFrame, lat_col: str = "latitude", lon_col: str = "longitude") -> pd.DataFrame:
    """Cluster points (e.g. blood banks) using DBSCAN with haversine distance.
    Adds a `cluster` column; -1 means "noise" (not part of any cluster)."""
    df = df.copy()
    coords = df[[lat_col, lon_col]].dropna()

    coords_rad = np.radians(coords.values)
    eps_rad = SPATIAL_CFG["dbscan_eps_km"] / EARTH_RADIUS_KM

    db = DBSCAN(
        eps=eps_rad,
        min_samples=SPATIAL_CFG["dbscan_min_samples"],
        metric="haversine",
    ).fit(coords_rad)

    df.loc[coords.index, "cluster"] = db.labels_
    n_clusters = len(set(db.labels_)) - (1 if -1 in db.labels_ else 0)
    n_noise = int((db.labels_ == -1).sum())
    log.info(f"dbscan_cluster: found {n_clusters} clusters, {n_noise} noise points "
             f"(eps={SPATIAL_CFG['dbscan_eps_km']}km, min_samples={SPATIAL_CFG['dbscan_min_samples']})")
    return df


def cluster_summary(clustered_df: pd.DataFrame, lat_col="latitude", lon_col="longitude") -> pd.DataFrame:
    """One row per cluster: size + centroid. Excludes noise (cluster == -1)."""
    valid = clustered_df[clustered_df["cluster"] != -1]
    summary = (
        valid.groupby("cluster")
        .agg(size=(lat_col, "count"), centroid_lat=(lat_col, "mean"), centroid_lon=(lon_col, "mean"))
        .reset_index()
        .sort_values("size", ascending=False)
    )
    return summary


def kde_density_grid(
    df: pd.DataFrame,
    lat_col: str = "latitude",
    lon_col: str = "longitude",
    grid_size: int = 100,
):
    """Compute a KDE density surface over a lat/lon grid — feeds the heatmap
    in the dashboard. Returns (grid_lat, grid_lon, density) meshgrid arrays."""
    from sklearn.neighbors import KernelDensity

    coords = df[[lat_col, lon_col]].dropna().values
    kde = KernelDensity(bandwidth=SPATIAL_CFG["kde_bandwidth"], metric="haversine",
                         kernel="gaussian")
    kde.fit(np.radians(coords))

    lat_min, lat_max = coords[:, 0].min() - 0.3, coords[:, 0].max() + 0.3
    lon_min, lon_max = coords[:, 1].min() - 0.3, coords[:, 1].max() + 0.3
    grid_lat, grid_lon = np.meshgrid(
        np.linspace(lat_min, lat_max, grid_size),
        np.linspace(lon_min, lon_max, grid_size),
    )
    grid_coords = np.radians(np.column_stack([grid_lat.ravel(), grid_lon.ravel()]))
    log_density = kde.score_samples(grid_coords)
    density = np.exp(log_density).reshape(grid_lat.shape)

    return grid_lat, grid_lon, density
