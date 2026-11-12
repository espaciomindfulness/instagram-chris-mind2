#!/usr/bin/env python3
"""Programa el carrusel de OSF en @chris.mind2 para el 12/11 a las 19:00.

Sale el mismo dia que el colaborativo del encuentro: la noticia y el recurso
juntos pegan mas que separados, y una noticia pierde valor cada dia que pasa.
El carrusel de las seis dimensiones se corrio al 14 para no amontonar.
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RUTA = RAIZ / "contenido" / "calendario.json"

CAPTION = (
 "El currículum completo del MBSR es público y casi nadie lo sabe.\n\n"
 "Doscientas treinta y dos páginas, gratis, sin registro y sin pago. Está "
 "en OSF desde octubre 👉 deslizá.\n\n"
 "No es un resumen ni un índice: están las ocho clases una por una, la "
 "jornada de práctica intensiva y ocho apéndices, incluidos el espíritu de "
 "la enseñanza y cómo darlo online. También el currículum original de 1993, "
 "para comparar.\n\n"
 "La edición 2026 la publicaron Brown University School of Professional "
 "Studies y el Global Mindfulness Collaborative, con revisiones directas de "
 "Jon Kabat-Zinn.\n\n"
 "Lo comparto por una razón concreta: en mindfulness no hay matrícula ni "
 "colegio que regule. Que el currículum sea público significa que cualquiera "
 "—alumno o colega— puede leer qué es el MBSR y compararlo con lo que le "
 "están dando. Eso es raro y es bueno.\n\n"
 "Está en osf.io/tckb3\n\n"
 "—\n"
 "Christian Arpa · Psicólogo (UBA) · MBSR Teacher calificado por el GMC\n\n"
 "#MBSR #mindfulness #psicologia #psicoterapia #formacion #saludmental "
 "#JonKabatZinn #atenciónplena"
)


def main():
    d = json.load(open(RUTA, encoding="utf-8"))
    if any(p["id"] == "c5-osf-curriculum" for p in d["posts"]):
        print("ya estaba programado")
        return
    archivos = [f"p5_osf_{i}.jpg" for i in range(1, 6)]
    faltan = [a for a in archivos
              if not (RAIZ / "contenido" / "publicar" / a).exists()]
    if faltan:
        print(f"! faltan {faltan}: corre preparar_imagenes.py")
        return
    d["posts"].append(dict(
        id="c5-osf-curriculum", tipo="carrusel", estado="pendiente",
        fecha="2026-11-12", hora="19:00", archivos=archivos, caption=CAPTION))
    d["posts"].sort(key=lambda p: (p["fecha"], p["hora"]))
    open(RUTA, "w", encoding="utf-8").write(
        json.dumps(d, ensure_ascii=False, indent=2) + "\n")
    print(f"programado 12/11 19:00 | caption {len(CAPTION)} de 2200")
    for p in d["posts"]:
        if p["estado"] == "pendiente":
            print(f"  {p['fecha']} {p['hora']}  {p['id']}")


if __name__ == "__main__":
    main()
