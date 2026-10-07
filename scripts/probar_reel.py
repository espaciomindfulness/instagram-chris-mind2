#!/usr/bin/env python3
"""Prueba que Meta pueda descargar y procesar un reel, SIN publicarlo.

Publicar un video son dos pasos: primero se crea un contenedor (ahi Meta baja
el archivo y lo procesa) y despues se publica. Este script hace solo el primero
y reporta el resultado. El contenedor queda sin publicar y Meta lo descarta
solo a las 24 horas.

Sirve para saber de antemano si un video le sirve a Instagram, en vez de
enterarse el dia que sale al feed.

Variables de entorno: las mismas que publicar.py.
"""

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from publicar import (  # noqa: E402
    CALENDARIO, ErrorAPI, IG_USER_ID, api, crear_contenedor, url_publica,
)

REEL_ID = os.environ.get("IG_REEL_ID", "")


def resumen(lineas: list[str]) -> None:
    texto = "\n".join(lineas)
    print(texto)
    destino = os.environ.get("GITHUB_STEP_SUMMARY")
    if destino:
        with open(destino, "a", encoding="utf-8") as archivo:
            archivo.write(texto + "\n")


def main() -> int:
    calendario = json.loads(CALENDARIO.read_text(encoding="utf-8"))
    # Solo reels activos: los que quedaron en borrador no tienen archivo y
    # probarlos da un falso negativo (Meta no puede bajar lo que no existe).
    reels = [p for p in calendario["posts"]
             if p.get("tipo") == "reel" and p.get("estado") == "pendiente"]
    if REEL_ID:
        reels = [p for p in calendario["posts"]
                 if p.get("tipo") == "reel" and p["id"] == REEL_ID]
    if not reels:
        resumen(["No encontre ningun reel pendiente para probar."])
        return 1

    post = reels[0]
    url = url_publica(post["archivo"])
    lineas = [f"### Prueba del reel `{post['id']}`", "", f"Archivo: {url}", ""]

    try:
        contenedor = crear_contenedor({
            "media_type": "REELS",
            "video_url": url,
            "caption": "PRUEBA - este contenedor no se publica",
        })
    except ErrorAPI as exc:
        lineas += ["**Meta rechazo el video al crear el contenedor.**", "",
                   f"```\n{exc}\n```", "",
                   "Si el error habla del formato o de la descarga, hay que",
                   "servir los videos desde otro lado o reencodearlos."]
        resumen(lineas)
        return 1

    lineas.append(f"Contenedor creado: `{contenedor}`. Esperando a que Meta lo procese...")
    inicio = time.monotonic()
    while time.monotonic() - inicio < 420:
        estado = api("GET", contenedor, {"fields": "status_code,status"})
        codigo = estado.get("status_code")
        if codigo == "FINISHED":
            lineas += ["", "**El video sirve.** Meta lo bajo y lo proceso bien.", "",
                       "El contenedor NO se publico: Meta lo descarta solo en 24 h.",
                       "Los reels del calendario van a salir sin problema."]
            resumen(lineas)
            return 0
        if codigo == "ERROR":
            lineas += ["", "**Meta no pudo procesar el video.**", "",
                       f"```\n{estado.get('status')}\n```"]
            resumen(lineas)
            return 1
        time.sleep(15)

    lineas += ["", "Timeout: sigue procesando despues de 7 minutos.",
               "No es concluyente; probablemente el video sea muy pesado."]
    resumen(lineas)
    return 1


if __name__ == "__main__":
    sys.exit(main())
