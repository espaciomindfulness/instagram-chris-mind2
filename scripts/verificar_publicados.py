#!/usr/bin/env python3
"""Pregunta a Instagram que hay publicado de verdad en la cuenta.

Sirve para contrastar lo que dice contenido/calendario.json con la realidad:
si el script marco un post como "publicado" pero en el feed no esta, aca se ve.

Variables de entorno:
  IG_USER_ID       (obligatoria)
  IG_ACCESS_TOKEN  (obligatoria)
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CALENDARIO = RAIZ / "contenido" / "calendario.json"
GRAPH = "https://graph.instagram.com/v23.0"
IG_USER_ID = os.environ.get("IG_USER_ID", "")
TOKEN = os.environ.get("IG_ACCESS_TOKEN", "")


def resumen(texto: str) -> None:
    print(texto)
    destino = os.environ.get("GITHUB_STEP_SUMMARY")
    if destino:
        with open(destino, "a", encoding="utf-8") as archivo:
            archivo.write(texto + "\n")


def get(ruta: str, **params) -> dict:
    params["access_token"] = TOKEN
    url = f"{GRAPH}/{ruta}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=60) as respuesta:
            return json.loads(respuesta.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return {"__error__": f"HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')}"}
    except urllib.error.URLError as exc:
        return {"__error__": f"No se pudo conectar: {exc.reason}"}


def main() -> int:
    if not (IG_USER_ID and TOKEN):
        resumen("Faltan IG_USER_ID o IG_ACCESS_TOKEN.")
        return 1

    datos = get(f"{IG_USER_ID}/media",
                fields="id,media_type,timestamp,permalink,caption",
                limit=25)
    if "__error__" in datos:
        resumen(f"### No pude consultar Instagram\n\n```\n{datos['__error__']}\n```")
        return 1

    publicados = datos.get("data", [])
    ids_reales = {m["id"] for m in publicados}

    lineas = [f"### Instagram dice que hay {len(publicados)} publicaciones", ""]
    lineas.append("| Fecha (UTC) | Tipo | media_id | Primeras palabras |")
    lineas.append("|---|---|---|---|")
    for m in publicados:
        texto = (m.get("caption") or "").replace("\n", " ")[:45]
        lineas.append(f"| {m.get('timestamp','?')[:16]} | {m.get('media_type','?')} "
                      f"| `{m['id']}` | {texto} |")

    # Contraste con nuestro calendario
    calendario = json.loads(CALENDARIO.read_text(encoding="utf-8"))
    marcados = [p for p in calendario["posts"] if p.get("estado") == "publicado"]
    fantasmas = [p for p in marcados if p.get("media_id") not in ids_reales]

    lineas += ["", f"### Contraste con el calendario ({len(marcados)} marcados como publicados)", ""]
    if fantasmas:
        lineas.append("**Marcados como publicados pero NO estan en Instagram:**")
        lineas.append("")
        for p in fantasmas:
            lineas.append(f"- `{p['id']}` — programado {p['fecha']} {p['hora']} "
                          f"— media_id `{p.get('media_id')}`")
    else:
        lineas.append("Todos los posts marcados como publicados existen en Instagram.")

    resumen("\n".join(lineas))
    return 0


if __name__ == "__main__":
    sys.exit(main())
