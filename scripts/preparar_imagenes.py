#!/usr/bin/env python3
"""
Convierte las imagenes originales al formato que exige Instagram.

Instagram Graph API solo acepta JPEG para publicar imagenes. Tus disenios
estan en PNG, asi que este script los pasa a JPEG y valida:

  - formato JPEG, color RGB
  - relacion de aspecto entre 4:5 (vertical) y 1.91:1 (horizontal)
  - ancho entre 320 y 1440 px
  - peso menor a 8 MB

Lee de   contenido/originales/*.png|jpg|jpeg|webp
Escribe  contenido/publicar/*.jpg

Uso:
    python scripts/preparar_imagenes.py
    python scripts/preparar_imagenes.py --forzar   # rehace todo
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Falta Pillow. Instalalo con:  python -m pip install Pillow")

RAIZ = Path(__file__).resolve().parent.parent
ORIGEN = RAIZ / "contenido" / "originales"
DESTINO = RAIZ / "contenido" / "publicar"

ASPECTO_MIN = 0.80   # 4:5  vertical
ASPECTO_MAX = 1.91   # 1.91:1 horizontal
ANCHO_MIN = 320
ANCHO_MAX = 1440
PESO_MAX = 8 * 1024 * 1024
EXTENSIONES = {".png", ".jpg", ".jpeg", ".webp"}


def preparar(ruta: Path, forzar: bool) -> str:
    salida = DESTINO / (ruta.stem + ".jpg")
    if salida.exists() and not forzar and salida.stat().st_mtime >= ruta.stat().st_mtime:
        return f"  = {salida.name} (ya estaba al dia)"

    imagen = Image.open(ruta)
    avisos = []

    # JPEG no soporta transparencia: aplanamos sobre blanco.
    if imagen.mode in ("RGBA", "LA", "P"):
        imagen = imagen.convert("RGBA")
        fondo = Image.new("RGB", imagen.size, (255, 255, 255))
        fondo.paste(imagen, mask=imagen.split()[-1])
        imagen = fondo
    else:
        imagen = imagen.convert("RGB")

    ancho, alto = imagen.size
    aspecto = ancho / alto
    if not ASPECTO_MIN <= aspecto <= ASPECTO_MAX:
        avisos.append(
            f"aspecto {aspecto:.2f} fuera del rango permitido "
            f"({ASPECTO_MIN}-{ASPECTO_MAX}); Instagram va a recortar"
        )

    if ancho > ANCHO_MAX:
        alto = round(alto * ANCHO_MAX / ancho)
        ancho = ANCHO_MAX
        imagen = imagen.resize((ancho, alto), Image.LANCZOS)
        avisos.append(f"redimensionada a {ancho}x{alto}")
    elif ancho < ANCHO_MIN:
        avisos.append(f"ancho {ancho}px es menor al minimo de {ANCHO_MIN}px")

    DESTINO.mkdir(parents=True, exist_ok=True)
    calidad = 92
    while True:
        imagen.save(salida, "JPEG", quality=calidad, optimize=True, subsampling=0)
        if salida.stat().st_size <= PESO_MAX or calidad <= 60:
            break
        calidad -= 8
        avisos.append(f"recomprimida a calidad {calidad}")

    peso_kb = salida.stat().st_size / 1024
    detalle = f"  + {salida.name}  {ancho}x{alto}  {peso_kb:.0f} KB"
    if avisos:
        detalle += "\n      aviso: " + "\n      aviso: ".join(avisos)
    return detalle


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--forzar", action="store_true", help="rehacer todas las imagenes")
    args = parser.parse_args()

    if not ORIGEN.exists():
        sys.exit(f"No existe {ORIGEN}. Poné ahí tus PNG originales.")

    archivos = sorted(p for p in ORIGEN.iterdir() if p.suffix.lower() in EXTENSIONES)
    if not archivos:
        sys.exit(f"No hay imagenes en {ORIGEN}")

    print(f"Preparando {len(archivos)} imagen(es) para Instagram...\n")
    for archivo in archivos:
        print(preparar(archivo, args.forzar))
    print(f"\nListo. JPEG publicables en: {DESTINO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
