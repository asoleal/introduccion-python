"""
Generador del dataset oficial del libro: ventas_cadena.parquet
Cadena agroindustrial ficticia "AgroAndina" - 12 meses de ventas.

El dataset contiene problemas REALES a propósito (para el ejercicio 6
del capítulo 11):
  - valores faltantes en cantidad y precio (~2 %)
  - nombres de producto inconsistentes ("Café", "café ", "CAFE"...)
  - precios absurdos (errores de digitación: negativos y enormes)

Uso:  python generar_dataset.py
Salida: data/ventas_cadena.parquet  (~20-30 MB, 3.000.000 de filas)
"""

import numpy as np
import pandas as pd
import os

rng = np.random.default_rng(2026)
N = 3_000_000

# --- productos con escritura inconsistente (dato sucio a propósito) ---
variantes = {
    "cafe":     ["café", "Café", "CAFE", "café ", " cafe"],
    "cacao":    ["cacao", "Cacao", "CACAO"],
    "banano":   ["banano", "Banano", "banano ", "BANANO"],
    "panela":   ["panela", "Panela", "PANELA"],
    "aguacate": ["aguacate", "Aguacate", "AGUACATE"],
}
base_productos = list(variantes.keys())
todas_variantes = [v for vs in variantes.values() for v in vs]

print("Generando datos...")
df = pd.DataFrame({
    "fecha":    pd.date_range("2025-01-01", periods=N, freq="min"),
    "tienda":   rng.integers(1, 121, N),                     # 120 tiendas
    "producto": rng.choice(todas_variantes, N),
    "cantidad": rng.integers(1, 60, N).astype(float),        # float para poder meter NaN
    "precio":   rng.normal(8000, 1200, N).round(0),
})

# --- suciedad 1: valores faltantes (~2 %) ---
faltantes_c = rng.choice(N, size=int(N * 0.02), replace=False)
df.loc[faltantes_c, "cantidad"] = np.nan
faltantes_p = rng.choice(N, size=int(N * 0.02), replace=False)
df.loc[faltantes_p, "precio"] = np.nan

# --- suciedad 2: errores de digitación en precio (~0.5 %) ---
errores = rng.choice(N, size=int(N * 0.005), replace=False)
df.loc[errores[:len(errores)//2], "precio"] = -df.loc[errores[:len(errores)//2], "precio"].abs()
df.loc[errores[len(errores)//2:], "precio"] = df.loc[errores[len(errores)//2:], "precio"] * 100

os.makedirs("data", exist_ok=True)
ruta = "data/ventas_cadena.parquet"
df.to_parquet(ruta, compression="snappy", index=False)

mb = os.path.getsize(ruta) / 1e6
print(f"Listo: {ruta}  ({len(df):,} filas, {mb:.1f} MB)")
print("Suciedad incluida: ~2% faltantes, ~0.5% precios absurdos, nombres inconsistentes.")
