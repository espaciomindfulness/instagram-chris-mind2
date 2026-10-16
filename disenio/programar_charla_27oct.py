#!/usr/bin/env python3
"""Anuncio de la charla abierta del 27/10 en @chris.mind2.

Va un dia antes que en Espacio Mindfulness a proposito: el publico de esta
charla son colegas, y esta es la cuenta donde estan. Ademas evita que las dos
cuentas publiquen la misma placa el mismo dia.

Mismo evento, texto distinto: aca habla el en primera persona, contando como
se formo el y que lo hizo cambiar. En EM la misma charla se anuncia en voz
institucional.
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RUTA = RAIZ / "contenido" / "calendario.json"

CAPTION = (
 "Doy una charla abierta y gratuita para colegas, y me gustaría que vengas.\n\n"
 "«Del diagnóstico al proceso: qué cambia cuando dejás de tratar trastornos»\n\n"
 "Me formé como casi todos: diagnóstico, y después el protocolo que le "
 "corresponde. Es prolijo. El problema es que el paciente real casi nunca "
 "viene con una sola etiqueta — viene con varias, y se alimentan entre sí.\n\n"
 "Trabajar por procesos cambia la pregunta. En vez de qué trastorno tiene, "
 "qué procesos sostienen su sufrimiento y cuáles puedo activar para que esté "
 "mejor.\n\n"
 "En una hora recorro ese giro y los tres procesos que atraviesan a las "
 "terapias con más evidencia: mindfulness, compasión y flexibilidad "
 "psicológica. Con ejemplos clínicos, no con teoría de manual.\n\n"
 "📅 Martes 27 de octubre · 20:30\n"
 "💻 Por Zoom · 1 hora · gratis\n\n"
 "El link para anotarte está en mi bio. Los cupos son limitados.\n\n"
 "—\n"
 "Christian Arpa · Psicólogo (UBA) · MBSR Teacher (GMC)\n"
 "Dirijo el Diplomado en Psicoterapia Basada en Procesos.\n\n"
 "#psicologia #act #mindfulness #psicoterapia #clinica #saludmental"
)


def main():
    d = json.load(open(RUTA, encoding="utf-8"))
    if any(p["id"] == "charla-27oct" for p in d["posts"]):
        print("ya estaba programada")
        return
    if not (RAIZ / "contenido" / "publicar" / "charla_27oct.jpg").exists():
        print("! falta charla_27oct.jpg: corre antes preparar_imagenes.py")
        return
    d["posts"].append(dict(id="charla-27oct", tipo="imagen", estado="pendiente",
                           fecha="2026-10-17", hora="19:00",
                           archivo="charla_27oct.jpg", caption=CAPTION))
    d["posts"].sort(key=lambda p: (p["fecha"], p["hora"]))
    open(RUTA, "w", encoding="utf-8").write(
        json.dumps(d, ensure_ascii=False, indent=2) + "\n")
    print(f"programada | caption {len(CAPTION)} de 2200")


if __name__ == "__main__":
    main()
