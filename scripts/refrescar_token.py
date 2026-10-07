#!/usr/bin/env python3
"""
Refresca el token de larga duracion de la Instagram API con Login de Instagram.

El token de Instagram dura 60 dias. Este script lo renueva por otros 60 dias
llamando al endpoint ig_refresh_token. Lo corre un workflow semanal
(.github/workflows/refrescar_token.yml), asi que el token nunca llega a vencer
y no tenes que rehacer nada a mano.

Requisitos:
  - El token actual tiene que tener al menos 24 horas de vida y no estar vencido.
    Como el workflow corre cada semana, esto siempre se cumple.

Variables de entorno:
  IG_ACCESS_TOKEN  (obligatoria) token actual de larga duracion.
  IG_TOKEN_OUT     opcional, archivo donde escribir el token nuevo.
                   Default: nuevo_token.txt (lo lee el workflow y lo borra).

Codigo de salida:
  0  se refresco bien (el token nuevo quedo en el archivo de salida)
  1  fallo el refresco (el workflow avisa; el token viejo sigue valido hasta
     su vencimiento)
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

GRAPH = "https://graph.instagram.com"
TOKEN = os.environ.get("IG_ACCESS_TOKEN", "")
SALIDA = os.environ.get("IG_TOKEN_OUT", "nuevo_token.txt")


def resumen(texto: str) -> None:
    print(texto)
    destino = os.environ.get("GITHUB_STEP_SUMMARY")
    if destino:
        with open(destino, "a", encoding="utf-8") as archivo:
            archivo.write(texto + "\n")


def main() -> int:
    if not TOKEN:
        resumen("Falta IG_ACCESS_TOKEN. Revisa el Secret del repositorio.")
        return 1

    url = f"{GRAPH}/refresh_access_token?" + urllib.parse.urlencode({
        "grant_type": "ig_refresh_token",
        "access_token": TOKEN,
    })

    try:
        with urllib.request.urlopen(url, timeout=60) as respuesta:
            datos = json.loads(respuesta.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detalle = exc.read().decode("utf-8", "replace")
        resumen(f"No se pudo refrescar el token (HTTP {exc.code}): {detalle}")
        return 1
    except urllib.error.URLError as exc:
        resumen(f"No se pudo conectar con Instagram: {exc.reason}")
        return 1

    nuevo = datos.get("access_token")
    if not nuevo:
        resumen(f"Respuesta inesperada al refrescar: {datos}")
        return 1

    dias = int(datos.get("expires_in", 0)) // 86400
    with open(SALIDA, "w", encoding="utf-8") as archivo:
        archivo.write(nuevo)

    resumen(f"Token refrescado: ahora vale ~{dias} dias mas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
