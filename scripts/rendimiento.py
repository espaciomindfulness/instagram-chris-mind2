#!/usr/bin/env python3
"""Que hace cada publicacion: alcance, interacciones y seguidores ganados.

Responde la pregunta que el contador de seguidores no puede contestar. El
perfil solo muestra el neto: si una semana bajas 12, no sabes si nadie te
encontro o si te encontraron 40 y se fueron 52. Aca se ve por publicacion.

Las tres columnas que importan, en orden:

  ALCANCE     cuantas cuentas distintas la vieron. Si es parecido a tu
              cantidad de seguidores, Instagram no la esta mostrando afuera.
  NO SEGUIDOS que porcentaje del alcance fue gente que NO te sigue. Es el
              unico numero que predice crecimiento: sin esto no hay seguidores
              nuevos, por bueno que sea el contenido.
  SEGUIDORES  cuantas personas te siguieron desde esa publicacion.

Guardadas y compartidas van despues porque son las dos senales que mas pesan
para que Instagram decida mostrarte a desconocidos: valen mas que los likes.

El informe se escribe en contenido/rendimiento.md y se commitea, asi queda
legible sin entrar a los logs de Actions.

Variables de entorno:
  IG_USER_ID       (obligatoria)
  IG_ACCESS_TOKEN  (obligatoria)
  IG_MEDIOS        cuantas publicaciones mirar (por defecto 20)
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
INFORME = RAIZ / "contenido" / "rendimiento.md"
GRAPH = "https://graph.instagram.com/v23.0"
IG_USER_ID = os.environ.get("IG_USER_ID", "")
TOKEN = os.environ.get("IG_ACCESS_TOKEN", "")
MEDIOS = int(os.environ.get("IG_MEDIOS", "20"))
ARG = timezone(timedelta(hours=-3))

# Se piden juntas y, si Meta rechaza el lote, se reintenta una por una: que
# una metrica no exista para cierto tipo de publicacion no puede dejarnos sin
# las demas.
METRICAS = ["reach", "total_interactions", "saved", "shares", "comments",
            "likes", "follows", "profile_visits"]


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


def insights_de(media_id: str) -> dict[str, int]:
    """Las metricas que ese tipo de publicacion sí admite."""
    datos = get(f"{media_id}/insights", metric=",".join(METRICAS))
    if "__error__" not in datos:
        return {d["name"]: d["values"][0]["value"] for d in datos.get("data", [])
                if d.get("values")}
    salida = {}
    for metrica in METRICAS:
        una = get(f"{media_id}/insights", intentos=1, metric=metrica)
        for d in una.get("data", []):
            if d.get("values"):
                salida[d["name"]] = d["values"][0]["value"]
    return salida


def etiqueta(medio: dict) -> str:
    """La primera linea del texto, que es como uno reconoce el posteo."""
    texto = (medio.get("caption") or "").strip().split("\n")[0]
    return (texto[:46] + "…") if len(texto) > 47 else (texto or "(sin texto)")


def main() -> int:
    if not (IG_USER_ID and TOKEN):
        print("Faltan IG_USER_ID o IG_ACCESS_TOKEN.")
        return 1

    ahora = datetime.now(ARG)
    perfil = get(IG_USER_ID, fields="username,followers_count")
    if "__error__" in perfil:
        print(f"No pude leer la cuenta: {perfil['__error__'][:300]}")
        return 0
    seguidores = perfil.get("followers_count", 0) or 0

    medios = get(f"{IG_USER_ID}/media",
                 fields="id,caption,media_type,timestamp,permalink", limit=MEDIOS)
    if "__error__" in medios:
        print(f"No pude leer las publicaciones: {medios['__error__'][:300]}")
        return 0

    filas = []
    for medio in medios.get("data", []):
        ins = insights_de(medio["id"])
        alcance = ins.get("reach", 0)
        # Meta no da el desglose seguidores/no-seguidores por publicacion en
        # esta API. Lo que si se puede afirmar es cuanto del alcance excede a
        # la base propia, que es la senal de que salio a explorar.
        filas.append({
            "fecha": medio["timestamp"][:10],
            "tipo": {"VIDEO": "reel", "CAROUSEL_ALBUM": "carrusel",
                     "IMAGE": "imagen"}.get(medio.get("media_type"), "?"),
            "texto": etiqueta(medio),
            "alcance": alcance,
            "sobre_base": alcance / seguidores if seguidores else 0,
            "guardadas": ins.get("saved", 0),
            "compartidas": ins.get("shares", 0),
            "interacciones": ins.get("total_interactions", 0),
            "seguidores": ins.get("follows", 0),
            "link": medio.get("permalink", ""),
        })

    lineas = [
        f"# Rendimiento de @{perfil.get('username', '?')}",
        "",
        f"Medido el {ahora:%d/%m/%Y a las %H:%M}. "
        f"{seguidores} seguidores al momento de medir.",
        "",
        "`% base` es el alcance como porcentaje de tus seguidores. Por debajo "
        "de 100% la publicacion ni siquiera llego a toda tu gente; muy por "
        "encima, Instagram la mostro a desconocidos.",
        "",
        "| Fecha | Tipo | Publicacion | Alcance | % base | Guard. | Comp. | Interac. | Segs. |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for f in filas:
        lineas.append(
            f"| {f['fecha']} | {f['tipo']} | {f['texto']} | {f['alcance']} | "
            f"{f['sobre_base']:.0%} | {f['guardadas']} | {f['compartidas']} | "
            f"{f['interacciones']} | {f['seguidores']} |")

    conteo = len(filas)
    if conteo:
        total_seg = sum(f["seguidores"] for f in filas)
        alcance_medio = sum(f["alcance"] for f in filas) / conteo
        por_tipo: dict[str, list[int]] = {}
        for f in filas:
            por_tipo.setdefault(f["tipo"], []).append(f["alcance"])
        lineas += [
            "",
            "## Resumen",
            "",
            f"- Alcance promedio: **{alcance_medio:.0f}** cuentas "
            f"({alcance_medio / seguidores:.0%} de tu base).",
            f"- Seguidores ganados en estas {conteo} publicaciones: **{total_seg}**.",
            "",
            "Alcance promedio por formato:",
            "",
        ]
        for tipo, valores in sorted(por_tipo.items(),
                                    key=lambda par: -sum(par[1]) / len(par[1])):
            lineas.append(f"- **{tipo}**: {sum(valores) / len(valores):.0f} "
                          f"({len(valores)} publicaciones)")
        mejor = max(filas, key=lambda f: f["alcance"])
        lineas += ["", f"La que mas lejos llego: «{mejor['texto']}» "
                       f"({mejor['tipo']}, {mejor['alcance']} cuentas)."]

    # Seguidores dia por dia: separa las altas de las bajas, que es lo que el
    # neto esconde.
    desde = int((ahora - timedelta(days=29)).timestamp())
    ins = get(f"{IG_USER_ID}/insights", metric="follower_count", period="day",
              since=desde, until=int(ahora.timestamp()))
    lineas += ["", "## Seguidores dia por dia", ""]
    if "__error__" in ins:
        lineas.append(f"_No disponible: {ins['__error__'][:200]}_")
    else:
        valores = [v for d in ins.get("data", []) for v in d.get("values", [])]
        netos = [v.get("value", 0) for v in valores]
        if not netos:
            lineas.append("_Instagram no devolvio datos para este periodo._")
        else:
            lineas += [
                f"Ultimos {len(netos)} dias: **{sum(netos):+d}** neto, "
                f"{sum(1 for n in netos if n > 0)} dias en alza y "
                f"{sum(1 for n in netos if n < 0)} en baja.",
                "",
                "| Dia | Neto |", "|---|---:|",
            ]
            for v in valores:
                lineas.append(f"| {v.get('end_time', '')[:10]} | "
                              f"{v.get('value', 0):+d} |")

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
