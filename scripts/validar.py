#!/usr/bin/env python3
"""
Revisa el calendario antes de que se publique nada.

Chequea que:
  - los IDs no esten repetidos
  - fecha y hora se puedan interpretar
  - exista el archivo JPEG correspondiente en contenido/publicar/
  - el caption no pase de 2200 caracteres ni de 30 hashtags
  - no haya dos posts a menos de 30 minutos uno del otro
  - los estados sean valores validos

Uso:
    python scripts/validar.py
Devuelve codigo 1 si encuentra algun problema bloqueante.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

RAIZ = Path(__file__).resolve().parent.parent
CALENDARIO = RAIZ / "contenido" / "calendario.json"
PUBLICAR = RAIZ / "contenido" / "publicar"

MAX_CAPTION = 2200
MAX_HASHTAGS = 30
SEPARACION_MINIMA = timedelta(minutes=30)
ESTADOS = {"pendiente", "publicado", "error", "vencido", "borrador"}
TIPOS = {"imagen", "carrusel", "reel"}


def archivos_de(post: dict) -> list[str]:
    if post.get("tipo") == "carrusel":
        return list(post.get("archivos", []))
    salida = [post["archivo"]] if post.get("archivo") else []
    if post.get("portada"):
        salida.append(post["portada"])
    return salida


def main() -> int:
    calendario = json.loads(CALENDARIO.read_text(encoding="utf-8"))
    tz = ZoneInfo(calendario.get("zona_horaria", "America/Argentina/Buenos_Aires"))
    posts = calendario["posts"]

    errores: list[str] = []
    avisos: list[str] = []
    vistos: set[str] = set()
    momentos: list[tuple[datetime, str]] = []

    for post in posts:
        pid = post.get("id", "<sin id>")

        if pid in vistos:
            errores.append(f"{pid}: ID repetido")
        vistos.add(pid)

        if post.get("estado") not in ESTADOS:
            errores.append(f"{pid}: estado invalido {post.get('estado')!r} (validos: {sorted(ESTADOS)})")

        if post.get("tipo") not in TIPOS:
            errores.append(f"{pid}: tipo invalido {post.get('tipo')!r} (validos: {sorted(TIPOS)})")

        try:
            cuando = datetime.fromisoformat(f"{post['fecha']}T{post['hora']}").replace(tzinfo=tz)
            if post.get("estado") == "pendiente":
                momentos.append((cuando, pid))
        except (KeyError, ValueError) as exc:
            errores.append(f"{pid}: fecha/hora ilegible ({exc}). Usa fecha AAAA-MM-DD y hora HH:MM")

        caption = post.get("caption", "")
        if len(caption) > MAX_CAPTION:
            errores.append(f"{pid}: caption de {len(caption)} caracteres, el maximo es {MAX_CAPTION}")
        hashtags = re.findall(r"#\w+", caption)
        if len(hashtags) > MAX_HASHTAGS:
            errores.append(f"{pid}: {len(hashtags)} hashtags, el maximo es {MAX_HASHTAGS}")
        if not caption.strip():
            avisos.append(f"{pid}: caption vacio")

        if post.get("tipo") == "reel":
            continue  # los videos no se generan con preparar_imagenes.py

        for archivo in archivos_de(post):
            if not (PUBLICAR / archivo).exists():
                errores.append(
                    f"{pid}: falta contenido/publicar/{archivo} "
                    "(corre  python scripts/preparar_imagenes.py)"
                )

    momentos.sort()
    for (a_cuando, a_id), (b_cuando, b_id) in zip(momentos, momentos[1:]):
        if b_cuando - a_cuando < SEPARACION_MINIMA:
            avisos.append(f"{a_id} y {b_id} estan a menos de 30 minutos uno del otro")

    pendientes = sum(1 for p in posts if p.get("estado") == "pendiente")
    print(f"Calendario: {len(posts)} posts, {pendientes} pendientes de publicar.\n")

    for aviso in avisos:
        print(f"  aviso  {aviso}")
    for error in errores:
        print(f"  ERROR  {error}")

    if errores:
        print(f"\n{len(errores)} problema(s) bloqueante(s). Corregilos antes de publicar.")
        return 1
    print("\nTodo en orden." if not avisos else f"\nSin errores bloqueantes ({len(avisos)} aviso/s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
