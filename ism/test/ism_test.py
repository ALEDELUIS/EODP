from pathlib import Path
import csv
import numpy as np
from netCDF4 import Dataset

#Rutas
output = Path(r"C:\Users\ALEJANDRA\Desktop\EODP_TER_2021\EODP-TS-ISM\output")
myoutput = Path(r"C:\Users\ALEJANDRA\Desktop\EODP_TER_2021\EODP-TS-ISM\myoutput")
RESULTS = Path(r"C:\Users\ALEJANDRA\Desktop\EODP_TER_2021\EODP-TS-ISM\ism_validation_results")

BANDS = [f"VNIR-{i}" for i in range(4)]
MAX_REL_ERROR = 1e-3  #0,001 %
ZERO_ATOL = 1e-8  #Tolerancia

#Leer la variable toa
def read_toa(path):
    with Dataset(path) as ds:
        return np.asarray(np.ma.filled(ds.variables["toa"][:], np.nan), dtype=float)

#Devuelve errores máximos y resultado PASS/FAIL
def validate(filename):
    reference = read_toa(output / filename)
    generated = read_toa(myoutput / filename)

    if reference.shape != generated.shape:
        raise ValueError(f"Dimensiones distintas en {filename}")
    if reference.size == 0:
        raise ValueError(f"Archivo vacío: {filename}")
    if not (np.isfinite(reference).all() and np.isfinite(generated).all()):
        raise ValueError(f"Valores no finitos en {filename}")

    abs_error = np.abs(generated - reference)
    nonzero = reference != 0

    max_abs = float(abs_error.max())
    max_rel = (
        float(np.max(100 * abs_error[nonzero] / np.abs(reference[nonzero])))
        if np.any(nonzero) else 0.0
    )
    zeros_ok = bool(np.all(abs_error[~nonzero] <= ZERO_ATOL))
    status = "PASS" if max_rel < MAX_REL_ERROR and zeros_ok else "FAIL"
    return [filename, max_abs, max_rel, status]


def main():
    #Valida las cuatro bandas, presenta la tabla y guarda un CSV
    RESULTS.mkdir(parents=True, exist_ok=True)
    filenames = [f"ism_toa_optical_{band}.nc" for band in BANDS]
    rows = [validate(filename) for filename in filenames]

    print(f"{'File':<29} {'Max abs difference':>21} {'Max rel difference (%)':>24} {'PASS/FAIL':>11}")
    print("-" * 90)
    for name, max_abs, max_rel, status in rows:
        print(f"{name:<29} {max_abs:>21.8e} {max_rel:>24.8e} {status:>11}")

    csv_path = RESULTS / "ism_optical_cross_validation.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["file", "max_abs_diff", "max_rel_diff_percent", "status"])
        writer.writerows(rows)

    overall = "PASS" if all(row[3] == "PASS" for row in rows) else "FAIL"
    print(f"\nOVERALL RESULT: {overall}")
    print(f"[CSV SAVED] {csv_path}")


if __name__ == "__main__":
    main()