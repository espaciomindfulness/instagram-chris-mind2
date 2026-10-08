#!/usr/bin/env python3
"""Separa altas de bajas y las cruza con los dias en que se publico.

Existe para contestar una pregunta concreta del usuario: "¿cómo puede ser que
pierdo seguidores subiendo contenido, y sin subir no perdía?".

El contador de seguidores no alcanza para contestarla, porque muestra el neto.
Y `follower_count`, que es lo que veniamos usando, cuenta SOLO las altas. Para
saber si publicar dispara bajas hace falta la metrica `follows_and_unfollows`,
que las desglosa.

La prueba: si las bajas se amontonan los dias que se publico, la intuicion es
correcta y hay que repensar la frecuencia. Si estan parejas entre dias con y
sin publicacion, son rotacion de fondo y publicar no tiene la culpa.

Ojo con la trampa de interpretacion: aunque las bajas se concentren en los
dias de publicacion, eso NO significa que publicar sea malo. Significa que
publicar hace visible una decision que la persona ya habia tomado. Una cuenta
dormida no pierde seguidores porque nadie se acuerda de que existe.

La API es inconsistente con esta metrica segun el tipo de cuenta, asi que se
prueban varias formas y se informa cual anduvo, en vez de fallar en silencio.

Variables de entorno:
  IG_USER_ID       (obligatoria)
  IG_ACCESS_TOKEN  (obligatoria)
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CALENDARIO = RAIZ / "contenido" / "calendario.json"
INFORME = RAIZ / "contenido" / "altas_bajas.md"
GRAPH = "https://graph.instagram.com/v23.0"
IG_USER_ID = os.environ.get("IG_USER_ID", "").strip()
TOKEN = os.environ.get("IG_ACCESS_TOKEN", "").strip()
ARG = timezone(timedelta(hours=-3))


def get(ruta: str, intentos: int = 3, **params) -> dict:
    params["access_token"] = TOKEN
    url = f"{GRAPH}/{ruta}?{urllib.parse.urlencode(params)}"
    ultimo = ""
    for intento in range(intentos):
        try:
            with urllib.request.urlopen(url, timeout=60) as respuesta:
                return json.loads(respuesta.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            ultimo = f"HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')}"
            if 400 <= exc.code < 500 and exc.code != 429:
                break
        except (urllib.error.URLError, TimeoutError) as exc:
            ultimo = f"No se pudo conectar: {exc}"
        except json.JSONDecodeError as exc:
            ultimo = f"Respuesta ilegible: {exc}"
        if intento < intentos - 1:
            time.sleep(5 * (intento + 1))
    return {"__error__": ultimo}


def dias_con_publicacion() -> set[str]:
    """Fechas en que salio algo, segun el propio calendario."""
    try:
        cal = json.loads(CALENDARIO.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return set()
    return {p["fecha"] for p in cal["posts"] if p["estado"] == "publicado"}


def main() -> int:
    if not (IG_USER_ID and TOKEN):
        print("Faltan IG_USER_ID o IG_ACCESS_TOKEN.")
        return 1

    ahora = datetime.now(ARG)
    desde = int((ahora - timedelta(days=29)).timestamp())
    hasta = int(ahora.timestamp())

    # Sin el nombre de la cuenta: este script se copia a los otros repos y
    # un titulo con el usuario cableado termina mintiendo en el repo de al lado.
    lineas = [f"# Altas y bajas de la cuenta",
              "", f"Medido el {ahora:%d/%m/%Y %H:%M}.", ""]

    # 1) Altas y bajas desglosadas. Se prueban las formas que acepta la API
    #    segun el tipo de cuenta; la primera que ande, gana.
    formas = [
        ("total del periodo, desglosado",
         dict(metric="follows_and_unfollows", metric_type="total_value",
              breakdown="follow_type", since=desde, until=hasta)),
        ("total del periodo, sin desglosar",
         dict(metric="follows_and_unfollows", metric_type="total_value",
              since=desde, until=hasta)),
        ("dia por dia",
         dict(metric="follows_and_unfollows", period="day",
              since=desde, until=hasta)),
    ]
    desglose = None
    for nombre, params in formas:
        datos = get(f"{IG_USER_ID}/insights", intentos=1, **params)
        if "__error__" not in datos and datos.get("data"):
            desglose = (nombre, datos)
            break

    lineas += ["## Altas y bajas de los ultimos 30 dias", ""]
    if desglose:
        nombre, datos = desglose
        lineas += [f"_Forma que acepto la API: {nombre}._", "", "```json",
                   json.dumps(datos, ensure_ascii=False, indent=2)[:2500], "```", ""]
    else:
        lineas += ["Instagram no entrego esta metrica para esta cuenta. "
                   "Abajo queda lo que si se pudo medir.", ""]

    # 2) Altas dia por dia cruzadas con los dias que se publico. Aunque no
    #    haya bajas, ver si las altas se concentran en dias de publicacion ya
    #    dice si publicar mueve la aguja.
    publico = dias_con_publicacion()
    ins = get(f"{IG_USER_ID}/insights", metric="follower_count", period="day",
              since=desde, until=hasta)
    lineas += ["## Altas por dia, segun si ese dia se publico", ""]
    if "__error__" in ins:
        lineas.append(f"_No disponible: {ins['__error__'][:300]}_")
    else:
        valores = [v for d in ins.get("data", []) for v in d.get("values", [])]
        con, sin = [], []
        filas = []
        for v in valores:
            dia = v.get("end_time", "")[:10]
            alta = v.get("value", 0)
            hubo = dia in publico
            (con if hubo else sin).append(alta)
            filas.append((dia, alta, "sí" if hubo else "—"))

        def media(xs):
            return sum(xs) / len(xs) if xs else 0

        lineas += [
            f"- Dias **con** publicacion: {len(con)} · {sum(con)} altas · "
            f"promedio **{media(con):.2f}** por dia",
            f"- Dias **sin** publicacion: {len(sin)} · {sum(sin)} altas · "
            f"promedio **{media(sin):.2f}** por dia",
            "",
        ]
        if con and sin:
            if media(sin) == 0:
                lineas.append("Los dias sin publicar no sumaron **ningun** seguidor.")
            else:
                lineas.append(f"Publicar multiplica las altas por "
                              f"**{media(con) / media(sin):.1f}**.")
            lineas.append("")
        lineas += ["| Dia | Altas | ¿Se publicó? |", "|---|---:|---|"]
        for dia, alta, hubo in filas:
            lineas.append(f"| {dia} | {alta:+d} | {hubo} |")

    INFORME.parent.mkdir(parents=True, exist_ok=True)
    INFORME.write_text("\n".join(lineas) + "\n", encoding="utf-8")
    print("\n".join(lineas))
    destino = os.environ.get("GITHUB_STEP_SUMMARY")
    if destino:
        with open(destino, "a", encoding="utf-8") as archivo:
            archivo.write("\n".join(lineas) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
