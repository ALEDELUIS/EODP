from pathlib import Path

import numpy as np
from netCDF4 import Dataset


# ============================================================
# RUTAS
# ============================================================

BASE = Path(
    r"C:\Users\ALEJANDRA\Desktop\EODP_TER_2021\EODP-TS-ISM"
)

output = BASE / "output"
myoutput = BASE / "myoutput"


def read_toa(filename):
    """Leer la variable TOA de un archivo NetCDF."""
    with Dataset(filename, "r") as ds:
        return np.ma.filled(
            ds.variables["toa"][:],
            np.nan
        ).astype(float)


# ============================================================
# BUSCAR ARCHIVOS COMUNES
# ============================================================

files_output = {f.name for f in output.glob("*.nc")}
files_myoutput = {f.name for f in myoutput.glob("*.nc")}

common_files = sorted(files_output & files_myoutput)

print(f"Archivos comunes encontrados: {len(common_files)}")


# ============================================================
# COMPARAR RESULTADOS
# ============================================================

for name in common_files:

    toa_ref = read_toa(output / name)
    toa_my = read_toa(myoutput / name)

    if toa_ref.shape != toa_my.shape:
        print(f"{name}: NO COINCIDE - dimensiones diferentes")
        continue

    # Valores válidos en ambos arrays
    valid = np.isfinite(toa_ref) & np.isfinite(toa_my)

    ref = toa_ref[valid]
    my = toa_my[valid]

    # Evitar divisiones entre cero
    nonzero = ref != 0

    relative_error = np.abs(
        (my[nonzero] - ref[nonzero]) / ref[nonzero]
    ) * 100

    max_relative_error = (
        np.max(relative_error)
        if relative_error.size > 0
        else 0
    )

    # Criterio de validación: error relativo menor que 1e-3 %
    coinciden = max_relative_error < 1e-3

    print(
        f"{name}: "
        f"{'COINCIDE' if coinciden else 'NO COINCIDE'} "
        f"(error relativo máx. = {max_relative_error:.3e} %)"
    )