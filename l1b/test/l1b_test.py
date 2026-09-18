from pathlib import Path
import numpy as np
from netCDF4 import Dataset
import matplotlib.pyplot as plt

#Rutas
output = Path(r"C:\Users\ALEJANDRA\Desktop\EODP_TER_2021\EODP-TS-L1B\output")
myoutputs = Path(r"C:\Users\ALEJANDRA\Desktop\EODP_TER_2021\EODP-TS-L1B\myoutputs")
myoutputs_noteq = Path(r"C:\Users\ALEJANDRA\Desktop\EODP_TER_2021\EODP-TS-L1B\myoutputs_noteq")
input = Path(r"C:\Users\ALEJANDRA\Desktop\EODP_TER_2021\EODP-TS-L1B\input")

#Función para leer el valor de toa

def read_toa(filename):
    with Dataset(filename, "r") as ds:
        return np.ma.filled(ds.variables["toa"][:], np.nan).astype(float)

#CROSS VALIDATE L1B EQUALIZATED
files_output = {f.name for f in output.glob("*.nc")}
files_myoutputs = {f.name for f in myoutputs.glob("*.nc")}

common_files = sorted(files_output & files_myoutputs)

print(f"Archivos comunes: {len(common_files)}")

for name in common_files: #Comparamos variable toa
    toa_output = read_toa(output / name)
    toa_myoutput = read_toa(myoutputs / name)

    coincide = (
        toa_output.shape == toa_myoutput.shape and np.allclose(
            toa_output,
            toa_myoutput,
            rtol=1e-6,
            atol=1e-8,
            equal_nan=True
        )
    )

    print(f"{name}: {'COINCIDE' if coincide else 'NO COINCIDE'}")

# PLOT FROM YOUR OUTPUTS THE EQUALISED OUTPUT VERSUS NOT EQUALISED VERSUS THE TRUTH
# TRUTH = EODP-TS-L1B\input\ism_toa_isrf_VNIR-0.nc

alt_pixel = 50

truth_file = input / f"ism_toa_isrf_VNIR-0.nc"
no_eq_file = myoutputs_noteq / f"l1b_toa_VNIR-0.nc"
eq_file = myoutputs / f"l1b_toa_VNIR-0.nc"

#leemos la variable toa de cada archivo
truth = read_toa(truth_file)
no_eq = read_toa(no_eq_file)
eq = read_toa(eq_file)

#Gráfica
act_pixel = np.arange(eq.shape[1])
plt.figure(figsize=(11, 6))

plt.plot(
    act_pixel,
    eq[alt_pixel, :],
    color="black",
    linewidth=1.5,
    label="TOA L1B with eq"
)

plt.plot(
    act_pixel,
    no_eq[alt_pixel, :],
    color="red",
    linewidth=1.5,
    label="TOA L1B no eq"
)

plt.plot(
    act_pixel,
    truth[alt_pixel, :],
    color="blue",
    linewidth=1.5,
    label="TOA after the ISRF"
)

plt.title(f"Effect of the Equalization for VNIR-0")
plt.xlabel("ACT pixel [-]")
plt.ylabel("TOA [mW/m²/sr]")

plt.grid(True, alpha=0.4)
plt.legend()
plt.tight_layout()
plt.show()