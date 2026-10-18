from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from common.io.readGeodetic import readGeodetic
from config.globalConfig import globalConfig


#Rutas
auxdir = r'C:\Users\ALEJANDRA\Documents\GitHub\EODP\auxiliary'

indir = (
    r"C:\Users\ALEJANDRA\Desktop\EODP_TER_2021\EODP-TS-L1C\input\gm_alt100_act_150"
    r",C:\Users\ALEJANDRA\Desktop\EODP_TER_2021\EODP-TS-L1C\input\l1b_output"
)

outdir = r"C:\Users\ALEJANDRA\Desktop\EODP_TER_2021\EODP-TS-L1C\myoutput"
RESULTS = Path(r"C:\Users\ALEJANDRA\Desktop\EODP_TER_2021\EODP-TS-L1C\l1c_report_figures")

#Separar las dos carpetas de entrada
gmdir, l1bdir = indir.split(",")

#Configuración global
config = globalConfig()

BAND = "VNIR-0"  # Grid geometry is represented using this L1C product.
EARTH_RADIUS_M = 6_371_000.0  # Spherical Earth approximation.


def read_l1c_geometry(path):
    with Dataset(path) as ds:
        lat = np.ma.filled(ds.variables["lat"][:], np.nan).astype(float)
        lon = np.ma.filled(ds.variables["lon"][:], np.nan).astype(float)
    return lat, lon

def haversine(lat1, lon1, lat2, lon2):
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = phi2 - phi1
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_M * np.arcsin(np.sqrt(np.clip(a, 0, 1)))

def save_plot(filename):
    plt.tight_layout()
    plt.savefig(RESULTS / filename, dpi=200)
    plt.close()

def main():
    RESULTS.mkdir(parents=True, exist_ok=True)
    cfg = globalConfig()

    #L1B geometry comes from the GM geolocation file
    lat_l1b, lon_l1b = readGeodetic(str(gmdir), cfg.gm_geoloc)
    lat_l1b = np.ma.filled(np.ma.asarray(lat_l1b), np.nan).astype(float)
    lon_l1b = np.ma.filled(np.ma.asarray(lon_l1b), np.nan).astype(float)

    #L1C coordinates from one output band
    l1c_file = Path(outdir) / f"{cfg.l1c_toa}{BAND}.nc"
    lat_l1c, lon_l1c = read_l1c_geometry(l1c_file)
    if lat_l1b.shape != lon_l1b.shape or lat_l1c.shape != lon_l1c.shape:
        raise ValueError("Latitude and longitude arrays have incompatible shapes")

    #Figure 1
    plt.figure(figsize=(10, 7))
    plt.scatter(lon_l1b.ravel(), lat_l1b.ravel(), s=4, color="red", label="L1B grid")
    plt.scatter(lon_l1c.ravel(), lat_l1c.ravel(), s=8, color="blue", label="L1C grid")
    plt.title("L1B and L1C spatial grids")
    plt.xlabel("Longitude [deg]")
    plt.ylabel("Latitude [deg]")
    plt.grid(alpha=0.3)
    plt.legend()
    save_plot("l1b_vs_l1c_grid.png")

    #Consecutive ACT pixel pairs on the central ALT row of L1B
    row = lat_l1b.shape[0] // 2
    lat = lat_l1b[row, :]
    lon = lon_l1b[row, :]
    ssd = haversine(lat[:-1], lon[:-1], lat[1:], lon[1:])
    lat_mid = (lat[:-1] + lat[1:]) / 2
    valid = np.isfinite(ssd) & np.isfinite(lat_mid)
    if not valid.any():
        raise ValueError("No valid consecutive pixels in the central L1B row")
    indices = np.arange(ssd.size)[valid]
    values = ssd[valid]
    mean_ssd = values.mean()

    #Figure 2
    plt.figure(figsize=(10, 6))
    plt.plot(indices, values, label="SSD", linewidth=1.5)
    plt.axhline(mean_ssd, color="red", linestyle="--", label=f"Mean = {mean_ssd:.2f} m")
    plt.title(f"Spatial Sampling Distance — central L1B row (ALT {row})")
    plt.xlabel("ACT pixel pair (starting index) [-]")
    plt.ylabel("SSD [m]")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.ticklabel_format(axis="y", style="plain", useOffset=False)
    save_plot("l1b_ssd_central_row.png")

    #Figure 3
    plt.figure(figsize=(10, 6))
    plt.plot(lat_mid[valid], values, marker=".", markersize=3, linewidth=1)
    plt.title(f"Spatial Sampling Distance versus latitude — L1B ALT {row}")
    plt.xlabel("Latitude [deg]")
    plt.ylabel("SSD [m]")
    plt.grid(alpha=0.3)
    plt.ticklabel_format(axis="y", style="plain", useOffset=False)
    save_plot("l1b_ssd_vs_latitude.png")

    print(f"Central L1B ALT row: {row}")
    print(f"SSD minimum: {values.min():.3f} m")
    print(f"SSD maximum: {values.max():.3f} m")
    print(f"SSD mean:    {mean_ssd:.3f} m")
    print(f"Figures saved in: {RESULTS}")


if __name__ == "__main__":
    main()