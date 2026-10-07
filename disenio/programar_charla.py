#!/usr/bin/env python3
"""Primera tanda de @chris.mind2: tres recortes de la charla del Diplomado.

Los otros dos recortes van en @espaciomindfulness (23 y 27 de octubre), asi
que las dos cuentas empujan el mismo tema sin publicar lo mismo.

Tono distinto al de EM a proposito: esta es la cuenta de la persona, no la de
la institucion. Primera persona, sin bloque institucional al pie y sin el
WhatsApp de ventas. Le habla a colegas.

Cadencia baja — tres posteos en nueve dias. En EM medimos que publicar mas
seguido casi no mueve las altas (0,67 contra 0,50 por dia); lo que las mueve
es que el contenido valga la pena guardarlo. Con tres piezas buenas alcanza
para arrancar.

Las fechas arrancan el 20/10 para dar margen al alta de la cuenta en Meta.
Si la conexion se demora, se corren y listo.
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RUTA = RAIZ / "contenido" / "calendario.json"

FIRMA = ("—\n"
         "Christian Arpa · Psicólogo (UBA) · MBSR Teacher (GMC)\n"
         "Dirijo el Diplomado en Psicoterapia Basada en Procesos.\n\n"
         "#psicologia #act #mindfulness #psicoterapia #clinica "
         "#saludmental #formacion")

P = [
 ("2026-10-20", "19:00", "reel1-falta-el-mapa", "01_falta_el_mapa.mp4",
  "Creo que el problema no son las técnicas. Es que nos faltó el mapa.\n\n"
  "Llega una persona con ansiedad, pero también con evitación, autocrítica y "
  "sueño roto. No entra en una sola casilla del manual.\n\n"
  "Y uno tiene con qué trabajar: algo de mindfulness, técnicas juntadas en "
  "talleres y cursos a lo largo de los años. Pero sin un criterio que las "
  "ordene, elegís por intuición o por lo último que leíste.\n\n"
  "Saber qué hacer primero, y por qué. Eso es lo que falta.\n\n"),

 ("2026-10-24", "19:00", "reel2-una-sola-etiqueta", "02_una_sola_etiqueta.mp4",
  "Diagnóstico y después el protocolo que le corresponde.\n\n"
  "Así me formé, y es prolijo. El problema es que el paciente real casi nunca "
  "viene con una sola etiqueta: viene con varias, y se alimentan entre sí.\n\n"
  "Por eso la disciplina se está moviendo hacia los procesos. En vez de "
  "preguntarte qué trastorno tiene, preguntás qué procesos sostienen su "
  "sufrimiento y cuáles podés activar para que esté mejor.\n\n"
  "Dejás de tratar etiquetas y trabajás los mecanismos de cambio que están "
  "debajo de todos los cuadros.\n\n"
  "¿Cómo lo ves vos en tu clínica? Me interesa leerlo 👇\n\n"),

 ("2026-10-28", "19:00", "reel3-el-caso", "03_el_caso.mp4",
  "Un caso concreto, para que no quede en teoría.\n\n"
  "Consultante de cuarenta años, llega por ansiedad. Si te quedás en la "
  "etiqueta, le das técnicas de relajación y listo.\n\n"
  "Pero escuchando aparece otra cosa: la ansiedad se le dispara cada vez que "
  "comete el error más mínimo, y ahí asoma una autocrítica brutal.\n\n"
  "Entonces no arrancás por la respiración. Vas por la compasión, a aflojar "
  "esa voz. Cuando esa voz baja, recién ahí la atención plena tiene dónde "
  "apoyarse. Y más adelante trabajás para que pueda avanzar hacia lo que le "
  "importa a pesar de la ansiedad.\n\n"
  "Eso es integrar.\n\n"),
]


def main():
    if RUTA.exists():
        d = json.load(open(RUTA, encoding="utf-8"))
    else:
        d = {"zona_horaria": "America/Argentina/Buenos_Aires", "posts": []}

    existentes = {p["id"] for p in d["posts"]}
    nuevos = 0
    for fecha, hora, pid, archivo, cuerpo in P:
        if pid in existentes:
            continue
        if not (RAIZ / "contenido" / "publicar" / archivo).exists():
            print(f"  ! falta el video {archivo}, no lo programo")
            continue
        d["posts"].append(dict(id=pid, tipo="reel", estado="pendiente",
                               fecha=fecha, hora=hora, archivo=archivo,
                               compartir_en_feed=True,
                               caption=cuerpo + FIRMA))
        nuevos += 1
    d["posts"].sort(key=lambda p: (p["fecha"], p["hora"]))
    RUTA.parent.mkdir(parents=True, exist_ok=True)
    open(RUTA, "w", encoding="utf-8").write(
        json.dumps(d, ensure_ascii=False, indent=2) + "\n")

    largo = max((len(p["caption"]) for p in d["posts"]), default=0)
    print(f"{nuevos} nuevos | {len(d['posts'])} en total | "
          f"caption mas larga: {largo} de 2200\n")
    for p in d["posts"]:
        print(f"  {p['fecha']} {p['hora']}  {p['tipo']:<6} {p['id']}")


if __name__ == "__main__":
    main()
