#CROSS VALIDATE L1B EQUALIZATED

# PLOT FROM YOUR OUTPUTS THE EQUALISED OUTPUT VERSUS NOT EQUALISED VERSUS THE TRUTH
# TRUTH = EODP-TS-L1B\input\ism_toa_isrf_VNIR-0.nc

from pathlib import Path
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt


# ============================================================
# RUTAS
# ============================================================

output = Path(
    r"C:\Users\ALEJANDRA\Desktop\EODP_TER_2021\EODP-TS-L1B\output"
)

myoutputs = Path(
    r"C:\Users\ALEJANDRA\Desktop\EODP_TER_2021\EODP-TS-L1B\myoutputs"
)

myoutputs_noteq = Path(
    r"C:\Users\ALEJANDRA\Desktop\EODP_TER_2021\EODP-TS-L1B\myoutputs_noteq"
)

# ============================================================
# BUSCAR ARCHIVOS .nc QUE COINCIDEN EN AMBAS CARPETAS
# ============================================================

files_output = {f.name: f for f in output.glob("*.nc")}
files_myoutputs = {f.name: f for f in myoutputs.glob("*.nc")}

common_files = sorted(
    set(files_output.keys()) & set(files_myoutputs.keys())
)

print(f"Archivos comunes encontrados: {len(common_files)}")

for name in common_files:
    print(" -", name)


# ============================================================
# COMPARAR VARIABLE TOA
# ============================================================

for name in common_files:

    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)

    file_ref = files_output[name]
    file_my = files_myoutputs[name]

    # Leer variable toa
    with Dataset(file_ref, "r") as ds_ref:
        toa_ref = ds_ref.variables["toa"][:]

    with Dataset(file_my, "r") as ds_my:
        toa_my = ds_my.variables["toa"][:]

    # Convertir masked arrays a arrays normales
    toa_ref = np.ma.filled(toa_ref, np.nan).astype(float)
    toa_my = np.ma.filled(toa_my, np.nan).astype(float)

    print("Shape output:   ", toa_ref.shape)
    print("Shape myoutputs:", toa_my.shape)

    # Comprobar dimensiones
    if toa_ref.shape != toa_my.shape:
        print("ERROR: las dimensiones son diferentes")
        continue

    # Valores válidos en ambos arrays
    valid = np.isfinite(toa_ref) & np.isfinite(toa_my)

    ref = toa_ref[valid]
    my = toa_my[valid]

    if ref.size == 0:
        print("ERROR: no hay valores válidos para comparar")
        continue

    # Igualdad aproximada
    iguales = np.allclose(
        ref,
        my,
        rtol=1e-6,
        atol=1e-8
    )

    print(f"Valores comparados:          {ref.size}")
    print(f"¿Coinciden numéricamente?:   {iguales}")


# ============================================================
# GRÁFICA EQUALISED VS NOT EQUALISED VS TRUTH
# ============================================================

import matplotlib.pyplot as plt


input_dir = Path(
    r"C:\Users\ALEJANDRA\Desktop\EODP_TER_2021\EODP-TS-L1B\input"
)

band = 0

# TRUTH
truth_file = input_dir / f"ism_toa_isrf_VNIR-{band}.nc"

# Resultado SIN ecualización
no_eq_file = myoutputs_noteq / f"l1b_toa_VNIR-{band}.nc"

# Resultado CON ecualización
eq_file = myoutputs / f"l1b_toa_eq_VNIR-{band}.nc"


def read_toa(filename):
    with Dataset(filename, "r") as ds:
        toa = ds.variables["toa"][:]

    return np.ma.filled(toa, np.nan).astype(float)


truth = read_toa(truth_file)
no_eq = read_toa(no_eq_file)
eq = read_toa(eq_file)


# Promedio de la primera dimensión:
# (100, 150) -> perfil de 150 píxeles ACT
truth_profile = np.nanmean(truth, axis=0)
no_eq_profile = np.nanmean(no_eq, axis=0)
eq_profile = np.nanmean(eq, axis=0)

alt_pixel = 50

truth_profile = truth[alt_pixel, :]
no_eq_profile = no_eq[alt_pixel, :]
eq_profile = eq[alt_pixel, :]

act_pixel = np.arange(truth_profile.size)


# ============================================================
# GRÁFICA
# ============================================================

plt.figure(figsize=(11, 6))

plt.plot(
    act_pixel,
    eq_profile,
    color="black",
    linewidth=1.5,
    label="TOA L1B with eq"
)

plt.plot(
    act_pixel,
    no_eq_profile,
    color="red",
    linewidth=1.5,
    label="TOA L1B no eq"
)

plt.plot(
    act_pixel,
    truth_profile,
    color="blue",
    linewidth=1.5,
    label="TOA after the ISRF"
)

plt.title(f"Effect of the Equalization for VNIR-{band}")
plt.xlabel("ACT pixel [-]")
plt.ylabel("TOA [mW/m²/sr]")

plt.grid(True, alpha=0.4)
plt.legend()
plt.tight_layout()
plt.show()

# Output ecualizado de referencia
eq_ref_file = output / "l1b_toa_eq_VNIR-0.nc"

# Tu output ecualizado
eq_my_file = myoutputs / "l1b_toa_eq_VNIR-0.nc"

with Dataset(eq_ref_file, "r") as ds:
    eq_ref = np.ma.filled(ds.variables["toa"][:], np.nan).astype(float)

with Dataset(eq_my_file, "r") as ds:
    eq_my = np.ma.filled(ds.variables["toa"][:], np.nan).astype(float)

print("REFERENCE EQ:")
print("min =", np.nanmin(eq_ref))
print("max =", np.nanmax(eq_ref))

print("\nMY EQ:")
print("min =", np.nanmin(eq_my))
print("max =", np.nanmax(eq_my))

print("\n¿Coinciden?",
      np.allclose(eq_ref, eq_my, rtol=1e-6, atol=1e-8, equal_nan=True))