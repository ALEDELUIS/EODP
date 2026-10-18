from pathlib import Path
import csv
import matplotlib.pyplot as plt
import numpy as np
from netCDF4 import Dataset

#Rutas
output = Path(r"C:\Users\ALEJANDRA\Desktop\EODP_TER_2021\EODP-TS-L1B\output")
myoutputs = Path(r"C:\Users\ALEJANDRA\Desktop\EODP_TER_2021\EODP-TS-L1B\myoutputs")
myoutputs_noteq = Path(r"C:\Users\ALEJANDRA\Desktop\EODP_TER_2021\EODP-TS-L1B\myoutputs_noteq")
input_dir = Path(r"C:\Users\ALEJANDRA\Desktop\EODP_TER_2021\EODP-TS-L1B\input")
RESULTS = Path(r"C:\Users\ALEJANDRA\Desktop\EODP_TER_2021\EODP-TS-L1B\l1b_validation_figures")

BANDS = [f"VNIR-{i}" for i in range(4)]
ALT_PIXEL = 50       # Fila along-track representada
MAX_REL_ERROR = 1e-3  # Porcentaje: 0,001 %
ZERO_ATOL = 1e-8     # Error absoluto admitido si referencia = 0

#Lee la variable toa
def load_toa(path):
    with Dataset(path) as ds:
        return np.asarray(
            np.ma.filled(ds.variables["toa"][:], np.nan),
            dtype=float
        )

#Cross Validation
def validate(filename):
    reference = load_toa(output / filename)
    generated = load_toa(myoutputs / filename)

    #Comprobación de que los datos se puedan comparar
    if reference.shape != generated.shape:
        raise ValueError(f"Dimensiones distintas en {filename}")
    if not (np.isfinite(reference).all() and np.isfinite(generated).all()):
        raise ValueError(f"Hay valores NaN o infinitos en {filename}")

    #Calcula la diferencia absoluta y relativa máximas
    error = np.abs(generated - reference)
    valid = reference != 0

    max_abs = float(error.max())

    max_rel = (
        float((100 * error[valid] / np.abs(reference[valid])).max())
        if valid.any() else np.nan
    )

    #Umbral relativo y tolerancia
    relative_ok = max_rel < MAX_REL_ERROR if valid.any() else True
    zeros_ok = np.all(error[~valid] <= ZERO_ATOL)

    status = "PASS" if relative_ok and zeros_ok else "FAIL"

    return [filename, max_abs, max_rel, status]

#Gráficas
def plot_equalization(band):
    filename = f"l1b_toa_{band}.nc"

    curves = [
        ("L1B with equalization", myoutputs / filename, "black"),
        ("L1B without equalization", myoutputs_noteq / filename, "red"),
        ("TOA after ISRF", input_dir / f"ism_toa_isrf_{band}.nc", "blue"),
    ]

    fig, ax = plt.subplots(figsize=(11, 6))
    shape = None

    for label, path, color in curves:
        data = load_toa(path)

        if data.ndim != 2 or (shape is not None and data.shape != shape):
            raise ValueError(f"Dimensiones incompatibles en {path.name}")

        shape = data.shape

        if ALT_PIXEL >= shape[0]:
            raise ValueError(f"ALT_PIXEL={ALT_PIXEL} fuera de rango")

        ax.plot(
            data[ALT_PIXEL, :],
            label=label,
            color=color,
            linewidth=1.4
        )

    ax.set(
        title=f"Effect of equalization — {band} (ALT pixel {ALT_PIXEL})",
        xlabel="ACT pixel [-]",
        ylabel="TOA [mW/m²/sr]"
    )

    ax.grid(alpha=0.35)
    ax.legend()
    fig.tight_layout()

    fig.savefig(RESULTS / f"l1b_equalization_{band}.png", dpi=200)
    plt.close(fig)


def main():
    RESULTS.mkdir(parents=True, exist_ok=True)
    filenames = [
        f"{prefix}_{band}.nc"
        for prefix in ("l1b_toa", "l1b_toa_eq")
        for band in BANDS
    ]

    rows = [validate(filename) for filename in filenames]

    #Resultados
    print(
        f"{'File':<24} "
        f"{'Max abs difference':>21} "
        f"{'Max rel difference (%)':>24} "
        f"{'PASS/FAIL':>11}"
    )
    print("-" * 85)

    for name, abs_err, rel_err, status in rows:
        print(
            f"{name:<24} "
            f"{abs_err:>21.8e} "
            f"{rel_err:>24.8e} "
            f"{status:>11}"
        )

    #Tabla a CSV
    with (RESULTS / "l1b_cross_validation.csv").open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.writer(file)
        writer.writerow([
            "file",
            "max_abs_diff",
            "max_rel_diff_percent",
            "status"
        ])
        writer.writerows(rows)

    #Gráfica para cada banda
    for band in BANDS:
        plot_equalization(band)

    overall = "PASS" if all(row[3] == "PASS" for row in rows) else "FAIL"
    print(f"\nOVERALL RESULT: {overall}")
    print(f"Results saved in: {RESULTS}")


if __name__ == "__main__":
    main()
