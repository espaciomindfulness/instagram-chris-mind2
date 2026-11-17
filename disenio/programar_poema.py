#!/usr/bin/env python3
"""Publica el reel del poema «Lo que queda cuando callo» en @chris.mind2.

Sale desde la cuenta personal con @espaciomindfulness como colaborador, al
reves del carrusel del encuentro: el poema lo escribio Christian, asi que la
autoria queda en su cuenta y Espacio presta el alcance. Un colaborativo se
distribuye a los seguidores de las dos cuentas.

Sin llamada a la accion, a proposito: es un texto, no una pieza de venta, y
un «inscribite» al pie le baja el registro.

El video se arma en Escritorio/ACBS - meditacion y poema (generador del
reel.py + retimar.py). La voz es la regrabacion del 16/11/2026, pasada por la
cadena SM58 sin denoise — Christian comparo las dos y el denoise le apagaba
la voz.
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RUTA = RAIZ / "contenido" / "calendario.json"

CAPTION = (
 "Lo escribí una mañana, pensando en una práctica que iba a guiar un rato "
 "después.\n\n"
 "No habla de meditar. Habla de lo que aparece cuando uno deja de corregir "
 "lo que escucha: el ruido de afuera, el cuerpo que se acomoda, y más "
 "adentro algo que no hace ruido y que no es vacío.\n\n"
 "Un lugar donde lo que duele entra sin pelear, como un huésped que llegó "
 "cansado.\n\n"
 "Gracias a @acbs_argentina por el espacio donde se leyó por primera vez.\n\n"
 "🌿 Christian D. Arpa · Psicólogo (UBA) · MBSR Teacher (GMC)\n\n"
 "#mindfulness #poesia #atencionplena #silencio #meditacion"
)


def main():
    fecha, hora = sys.argv[1], sys.argv[2]
    d = json.load(open(RUTA, encoding="utf-8"))
    if any(p["id"] == "reel-poema-callo" for p in d["posts"]):
        print("ya estaba programado")
        return
    if not (RAIZ / "contenido" / "publicar" / "reel_poema.mp4").exists():
        print("! falta contenido/publicar/reel_poema.mp4")
        return
    d["posts"].append(dict(
        id="reel-poema-callo", tipo="reel", estado="pendiente",
        fecha=fecha, hora=hora, archivo="reel_poema.mp4",
        compartir_en_feed=True, colaboradores=["espaciomindfulness"],
        caption=CAPTION))
    d["posts"].sort(key=lambda p: (p["fecha"], p["hora"]))
    open(RUTA, "w", encoding="utf-8").write(
        json.dumps(d, ensure_ascii=False, indent=2) + "\n")
    print(f"programado {fecha} {hora} | colaborador @espaciomindfulness")


if __name__ == "__main__":
    main()
