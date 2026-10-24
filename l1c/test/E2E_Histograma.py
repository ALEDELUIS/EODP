# HISTOGRAMS OF L1B TOA - ONE HISTOGRAM PER BAND

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset


# ============================================================
# RUTA
# ============================================================

input_dir = Path(
    r"C:\Users\ALEJANDRA\Desktop\EODP-TS-E2E\myoutput_l1b"
)

bands = [
    "VNIR-0",
    "VNIR-1",
    "VNIR-2",
    "VNIR-3"
]


# ============================================================
# HISTOGRAMAS
# ============================================================

for band in bands:

    filename = input_dir / f"l1b_toa_{band}.nc"

    # Leer TOA
    with Dataset(filename, "r") as ds:
        toa = ds.variables["toa"][:]

    # Convertir matriz 2D a vector
    toa = np.ma.filled(toa, np.nan).astype(float)
    toa = toa.flatten()

    # Eliminar posibles NaN
    toa = toa[np.isfinite(toa)]

    # Calcular histograma
    frequency, bin_edges = np.histogram(
        toa,
        bins=1000
    )

    # Centro de cada bin
    bin_centers = (
        bin_edges[:-1] + bin_edges[1:]
    ) / 2

    # Crear figura
    plt.figure(figsize=(10, 6))

    plt.plot(
        bin_centers,
        frequency,
        linewidth=1
    )

    plt.title(f"L1B TOA Histogram - {band}")
    plt.xlabel("Pixel value")
    plt.ylabel("Frequency")

    plt.grid(True, alpha=0.4)
    plt.tight_layout()

    plt.show()

    # Información en terminal
    print(
        band,
        "- Maximum frequency:",
        np.max(frequency)
    )