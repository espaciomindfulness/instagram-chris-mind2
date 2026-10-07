#!/usr/bin/env python3
"""Mide si la cuenta suma o resta seguidores.

Dos fuentes, porque ninguna alcanza sola:

  1. El historico propio (contenido/metricas.json). Cada corrida guarda una
     foto del dia: seguidores, seguidos y publicaciones. Con eso se calcula
     la variacion desde la corrida anterior, desde hace 7 dias y desde hace
     30. Es lo unico que funciona en cuentas chicas.

  2. Las Insights de Instagram (metrica `follower_count`), que dan el alta
     neta de cada dia de los ultimos 30. Es mas fino, pero Meta las niega en
     cuentas con menos de 100 seguidores: ahi el script sigue igual con el
     historico y lo dice, en vez de fallar.

La primera corrida no puede decir si subis o bajas — no hay contra que
comparar. Deja la primera marca y a partir de la segunda ya hay respuesta.

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
HISTORICO = RAIZ / "contenido" / "metricas.json"
GRAPH = "https://graph.instagram.com/v23.0"
IG_USER_ID = os.environ.get("IG_USER_ID", "")
TOKEN = os.environ.get("IG_ACCESS_TOKEN", "")

# Buenos Aires. Sin libreria extra: el offset es fijo todo el anio.
ARG = timezone(timedelta(hours=-3))


def resumen(lineas: list[str]) -> None:
    texto = "\n".join(lineas)
    print(texto)
    destino = os.environ.get("GITHUB_STEP_SUMMARY")
    if destino:
        with open(destino, "a", encoding="utf-8") as archivo:
            archivo.write(texto + "\n")


def get(ruta: str, intentos: int = 3, **params) -> dict:
    """Consulta la API. Reintenta: la API se cae de a ratos por unos minutos
    y no tiene sentido dar por perdida la medicion de la semana por eso."""
    params["access_token"] = TOKEN
    url = f"{GRAPH}/{ruta}?{urllib.parse.urlencode(params)}"
    ultimo = ""
    for intento in range(intentos):
        try:
            with urllib.request.urlopen(url, timeout=60) as respuesta:
                return json.loads(respuesta.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            ultimo = f"HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')}"
            # 4xx que no sea 429 es un problema del pedido: reintentar no cambia nada.
            if 400 <= exc.code < 500 and exc.code != 429:
                break
        except (urllib.error.URLError, TimeoutError) as exc:
            ultimo = f"No se pudo conectar: {exc}"
        except json.JSONDecodeError as exc:
            ultimo = f"Respuesta ilegible: {exc}"
        if intento < intentos - 1:
            time.sleep(5 * (intento + 1))
    return {"__error__": ultimo}


def signo(n: int) -> str:
    return f"+{n}" if n > 0 else str(n)


def fecha(texto: str) -> datetime:
    """Una fecha guardada, ya con la zona de Buenos Aires puesta."""
    return datetime.fromisoformat(texto).replace(tzinfo=ARG)


def leer_historico() -> list[dict]:
    if not HISTORICO.exists():
        return []
    try:
        return json.loads(HISTORICO.read_text(encoding="utf-8")).get("mediciones", [])
    except (json.JSONDecodeError, OSError):
        # Un historico roto no puede tumbar la medicion de hoy.
        return []


def mas_cercana(mediciones: list[dict], dias: int, hoy: datetime) -> dict | None:
    """La medicion mas cercana a hace `dias` dias, con 3 dias de tolerancia."""
    objetivo = hoy - timedelta(days=dias)
    # Las fechas guardadas son "2026-09-04" pelado, o sea sin zona horaria, y
    # restar una naive de una con zona explota. Se les pone la de Buenos Aires.
    candidatas = [
        (abs((fecha(m["fecha"]) - objetivo).days), m)
        for m in mediciones
    ]
    candidatas = [(d, m) for d, m in candidatas if d <= 3]
    return min(candidatas, key=lambda par: par[0])[1] if candidatas else None


def main() -> int:
    if not (IG_USER_ID and TOKEN):
        resumen(["Faltan IG_USER_ID o IG_ACCESS_TOKEN."])
        return 1

    perfil = get(IG_USER_ID, fields="username,followers_count,follows_count,media_count")
    if "__error__" in perfil:
        # Sale en verde a proposito. Que no se pueda leer una metrica no es una
        # falla del sistema: publicar sigue andando. Pintar Actions de rojo por
        # esto hace que despues nadie mire cuando el rojo importa de verdad.
        resumen([
            "### No pude leer la cuenta esta vez",
            "",
            "La API no contesto despues de tres intentos. No se perdio nada: "
            "la proxima corrida vuelve a medir.",
            "",
            f"```\n{perfil['__error__'][:500]}\n```",
        ])
        return 0

    ahora = datetime.now(ARG)
    hoy = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
    actual = {
        "fecha": ahora.date().isoformat(),
        "seguidores": perfil.get("followers_count", 0),
        "seguidos": perfil.get("follows_count", 0),
        "publicaciones": perfil.get("media_count", 0),
    }

    mediciones = [m for m in leer_historico() if m["fecha"] != actual["fecha"]]
    previas = sorted(mediciones, key=lambda m: m["fecha"])

    lineas = [
        f"### @{perfil.get('username', '?')} — {ahora:%d/%m/%Y %H:%M}",
        "",
        f"**{actual['seguidores']} seguidores** · {actual['seguidos']} seguidos "
        f"· {actual['publicaciones']} publicaciones",
        "",
    ]

    if not previas:
        lineas += [
            "Primera medicion: todavia no hay contra que comparar. La proxima "
            "corrida ya va a mostrar la variacion.",
            "",
        ]
    else:
        lineas += ["| Desde | Fecha | Seguidores | Variacion | Seguidos | Variacion |",
                   "|---|---|---|---|---|---|"]
        anterior = previas[-1]
        filas = [("la medicion anterior", anterior)]
        for dias, etiqueta in ((7, "hace 7 dias"), (30, "hace 30 dias")):
            ref = mas_cercana(previas, dias, hoy)
            if ref and ref["fecha"] != anterior["fecha"]:
                filas.append((etiqueta, ref))
        for etiqueta, ref in filas:
            d_seg = actual["seguidores"] - ref["seguidores"]
            d_sig = actual["seguidos"] - ref.get("seguidos", actual["seguidos"])
            lineas.append(
                f"| {etiqueta} | {ref['fecha']} | {ref['seguidores']} | "
                f"**{signo(d_seg)}** | {ref.get('seguidos', '?')} | {signo(d_sig)} |")
        lineas.append("")

        delta = actual["seguidores"] - anterior["seguidores"]
        dias = (hoy - fecha(anterior["fecha"])).days
        veredicto = "sumando" if delta > 0 else ("restando" if delta < 0 else "planchada")
        lineas += [f"En los ultimos {dias} dias la cuenta viene **{veredicto}** "
                   f"({signo(delta)}).", ""]

        # Seguimiento de la depuracion de seguidos. La proporcion importa:
        # una cuenta que sigue casi tanto como la siguen pierde alcance.
        # Lo que se vigila no es solo que baje, sino que al bajar NO se lleve
        # seguidores puestos — si al dejar de seguir se van, es que seguian
        # por reciprocidad y conviene ir mas despacio.
        bajada = anterior.get("seguidos", actual["seguidos"]) - actual["seguidos"]
        if bajada > 0:
            costo = ("sin costo: no se fue nadie" if delta >= 0 else
                     f"y en el mismo periodo se fueron {abs(delta)} seguidores")
            lineas += [
                f"**Depuracion:** dejaste de seguir {bajada} cuentas, {costo}.", ""]

    ratio = actual["seguidores"] / actual["seguidos"] if actual["seguidos"] else 0
    lineas += [f"_Proporcion: {ratio:.2f} seguidores por cada cuenta que seguis "
               f"(sano a partir de 3)._", ""]

    # Insights: el alta neta dia por dia. Solo desde 100 seguidores.
    desde = int((ahora - timedelta(days=30)).timestamp())
    hasta = int(ahora.timestamp())
    ins = get(f"{IG_USER_ID}/insights", metric="follower_count", period="day",
              since=desde, until=hasta)
    if "__error__" in ins:
        if actual["seguidores"] < 100:
            lineas += ["_Instagram no da las metricas diarias hasta los 100 "
                       "seguidores. Mientras tanto vale el historico de arriba._", ""]
        else:
            lineas += [f"_No pude leer las metricas diarias: {ins['__error__'][:180]}_", ""]
    else:
        valores = [v for d in ins.get("data", []) for v in d.get("values", [])]
        netos = [v.get("value", 0) for v in valores]
        if netos:
            mejor = max(valores, key=lambda v: v.get("value", 0))
            lineas += [
                f"**Ultimos 30 dias segun Instagram:** {signo(sum(netos))} seguidores "
                f"netos, {sum(1 for n in netos if n > 0)} dias en alza y "
                f"{sum(1 for n in netos if n < 0)} en baja.",
                f"Mejor dia: {mejor.get('end_time', '')[:10]} con "
                f"{signo(mejor.get('value', 0))}.",
                "",
            ]

    previas.append(actual)
    HISTORICO.parent.mkdir(parents=True, exist_ok=True)
    HISTORICO.write_text(
        json.dumps({"mediciones": previas}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")

    resumen(lineas)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
