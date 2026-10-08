# LEVEL-1C TEST
# 1. Plot L1B grid (red) versus L1C grid (blue)
# 2. Plot Spatial Sampling Distance for the central row of the L1B geometry

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from geopy.distance import great_circle

from common.io.readGeodetic import readGeodetic
from config.globalConfig import globalConfig


# ============================================================
# RUTAS - MISMA ESTRUCTURA QUE mainL1c.py
# ============================================================

auxdir = r'C:\Users\ALEJANDRA\Documents\GitHub\EODP\auxiliary'

indir = (
    r"C:\Users\ALEJANDRA\Desktop\EODP_TER_2021\EODP-TS-L1C\input\gm_alt100_act_150"
    r",C:\Users\ALEJANDRA\Desktop\EODP_TER_2021\EODP-TS-L1C\input\l1b_output"
)

outdir = r"C:\Users\ALEJANDRA\Desktop\EODP_TER_2021\EODP-TS-L1C\myoutput"


# Separar las dos carpetas de entrada
gmdir, l1bdir = indir.split(",")

# Configuración global
config = globalConfig()


# ============================================================
# LEER GEOMETRÍA L1B
# ============================================================

lat_l1b, lon_l1b = readGeodetic(
    gmdir,
    config.gm_geoloc
)


# ============================================================
# LEER GEOMETRÍA L1C
# ============================================================

# Usamos VNIR-0 para representar la geometría L1C
band = "VNIR-0"

l1c_file = Path(outdir) / f"{config.l1c_toa}{band}.nc"


def read_l1c(filename):
    """
    Lee latitud y longitud del producto L1C.
    """

    with Dataset(filename, "r") as ds:

        print("Variables L1C:", list(ds.variables.keys()))

        lat = ds.variables["lat"][:]
        lon = ds.variables["lon"][:]

    lat = np.ma.filled(lat, np.nan).astype(float)
    lon = np.ma.filled(lon, np.nan).astype(float)

    return lat, lon


lat_l1c, lon_l1c = read_l1c(l1c_file)


# ============================================================
# 1. L1B GRID VS L1C GRID
# ============================================================

plt.figure(figsize=(10, 7))

# L1B grid
plt.scatter(
    lon_l1b.flatten(),
    lat_l1b.flatten(),
    s=4,
    color="red",
    label="L1B grid"
)

# L1C grid
plt.scatter(
    lon_l1c.flatten(),
    lat_l1c.flatten(),
    s=8,
    color="blue",
    label="L1C grid"
)

plt.title("L1B grid versus L1C grid")
plt.xlabel("Longitude [deg]")
plt.ylabel("Latitude [deg]")

plt.grid(True, alpha=0.4)
plt.legend()
plt.tight_layout()
plt.show()


# ============================================================
# 2. SPATIAL SAMPLING DISTANCE - CENTRAL L1B ROW
# ============================================================

# Seleccionar fila ALT central
central_row = lat_l1b.shape[0] // 2

lat_row = lat_l1b[central_row, :]
lon_row = lon_l1b[central_row, :]

# Distancias entre píxeles ACT consecutivos
ssd = np.zeros(len(lat_row) - 1)

for ii in range(len(lat_row) - 1):

    point1 = (lat_row[ii], lon_row[ii])
    point2 = (lat_row[ii + 1], lon_row[ii + 1])

    # Distancia sobre la superficie terrestre
    ssd[ii] = great_circle(
        point1,
        point2
    ).meters


# Eje ACT
act_pixel = np.arange(len(ssd))

# Media del Spatial Sampling Distance
mean_ssd = np.mean(ssd)


# ============================================================
# PLOT SPATIAL SAMPLING DISTANCE
# ============================================================

plt.figure(figsize=(10, 6))

# Spatial Sampling Distance
plt.plot(
    act_pixel,
    ssd,
    linewidth=1.5,
    label="SSD"
)

# Media
plt.axhline(
    y=mean_ssd,
    color="red",
    linestyle="--",
    linewidth=1.5,
    label=f"Mean SSD = {mean_ssd:.2f} m"
)

plt.title(
    f"Spatial Sampling Distance - L1B central row (ALT = {central_row})"
)

plt.xlabel("ACT pixel [-]")
plt.ylabel("Spatial Sampling Distance [m]")

plt.grid(True, alpha=0.4)
plt.legend()
plt.tight_layout()
plt.show()


# ============================================================
# RESULTADOS EN TERMINAL
# ============================================================

print("\nSpatial Sampling Distance")
print("-------------------------")
print("Central ALT row:", central_row)
print("Mean SSD:", mean_ssd, "m")
print("Minimum SSD:", np.min(ssd), "m")
print("Maximum SSD:", np.max(ssd), "m")