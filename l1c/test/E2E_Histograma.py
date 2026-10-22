from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset

#RUTA
input_dir = Path(r"C:\Users\ALEJANDRA\Desktop\EODP-TS-E2E\myoutput_l1b")

bands = [
    "VNIR-0",
    "VNIR-1",
    "VNIR-2",
    "VNIR-3"
]


#HISTOGRAMAS

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

    # Crear histograma
    plt.figure(figsize=(10, 6))

    plt.hist(
        toa,
        bins=100,
        edgecolor="black"
    )

    plt.title(f"Histogram of L1B TOA - {band}")
    plt.xlabel("TOA")
    plt.ylabel("Number of pixels")

    plt.grid(True, alpha=0.3)
    plt.tight_layout()

    plt.show()