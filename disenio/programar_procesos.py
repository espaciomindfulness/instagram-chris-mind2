#!/usr/bin/env python3
"""Programa los cuatro carruseles de procesos en @chris.mind2.

Dos por semana, no dia por medio. En EM medimos que publicar mas seguido casi
no mueve las altas (0,67 contra 0,50 por dia); lo que las mueve es que valga
la pena guardarlo. Y esta cuenta le habla a colegas, que no estan en
Instagram todo el dia.

Las captions van en primera persona y sin llamada a la accion de venta. Es
material clinico para colegas: un «inscribite» al pie le baja el registro y
le saca lo que lo hace funcionar.
"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RUTA = RAIZ / "contenido" / "calendario.json"

FIRMA = ("—\n"
         "Christian Arpa · Psicólogo (UBA) · MBSR Teacher (GMC)\n"
         "De la charla «Del diagnóstico al proceso», octubre de 2026.\n\n"
         "#psicologia #act #psicoterapia #clinica #mindfulness "
         "#saludmental #procesos")

P = [
 ("2026-11-09", "19:00", "c1-tres-grietas",
  [f"p1_grietas_{i}.jpg" for i in range(1, 7)],
  "El diagnóstico describe un conjunto de síntomas. No dice qué los "
  "sostiene, ni por dónde intervenir.\n\n"
  "Y está bien: es una herramienta de comunicación y de clasificación. El "
  "problema aparece cuando le pedimos algo que nunca prometió dar — una guía "
  "para decidir qué hacer con esta persona, un martes a las seis de la "
  "tarde.\n\n"
  "Tres grietas conocidas del modelo de categorías 👉 deslizá.\n\n"
  "La tercera es la que más me hizo ruido cuando la entendí: terapias de "
  "escuelas distintas obtienen resultados parecidos. Algo que tienen en "
  "común está haciendo el trabajo, y no es el nombre del modelo.\n\n"),

 ("2026-11-12", "19:00", "c2-seis-dimensiones",
  [f"p2_dim_{i}.jpg" for i in range(1, 9)],
  "Si la etiqueta no alcanza para decidir qué hacer, ¿dónde se mira?\n\n"
  "Seis dimensiones donde vive un proceso: afecto, cognición, atención, "
  "self, motivación y conducta 👉 deslizá.\n\n"
  "La que más se saltea es la última. Preguntamos mucho por lo que siente y "
  "lo que piensa, y dejamos para el final lo que efectivamente hace y dejó "
  "de hacer — que es lo único observable.\n\n"
  "Y todo atravesado por dos contextos que no se pueden ignorar: el "
  "biológico y el sociocultural.\n\n"
  "Guardátelo para tenerlo a mano en la próxima formulación.\n\n"),

 ("2026-11-16", "19:00", "c3-formular-caso",
  [f"p3_caso_{i}.jpg" for i in range(1, 8)],
  "Cómo se formula un caso desde procesos, en cinco pasos.\n\n"
  "Esto se puede usar el martes que viene sin cambiar de modelo ni "
  "abandonar nada de lo que ya sabés hacer 👉 deslizá.\n\n"
  "El segundo paso es el que más rinde: casi siempre hay un alivio a corto "
  "plazo que paga el costo a largo plazo. Ese alivio es el que hay que "
  "tocar, y casi nunca es el síntoma que trae la persona.\n\n"
  "Y el quinto es el más incómodo. Si en cuatro o seis sesiones no se movió "
  "nada, la primera hipótesis no debería ser que el paciente no colabora.\n\n"),

 ("2026-11-19", "19:00", "c4-tres-preguntas",
  [f"p4_preg_{i}.jpg" for i in range(1, 6)],
  "Tres preguntas para la próxima primera entrevista. Una por cada "
  "proceso 👉 deslizá.\n\n"
  "No reemplazan una evaluación ni hace falta cambiar de modelo para "
  "usarlas. Pero cambian lo que escuchás en los primeros veinte minutos, "
  "que es cuando se decide casi todo.\n\n"
  "La tercera es la que más me sorprende en sesión: la distancia entre cómo "
  "alguien se trata a sí mismo y cómo trataría a un amigo con el mismo "
  "problema suele ser enorme, y verla es la puerta de entrada a la "
  "compasión.\n\n"
  "¿Vos cuál agregarías? Me interesa leerlo 👇\n\n"),
]


def main():
    d = json.load(open(RUTA, encoding="utf-8"))
    existentes = {p["id"] for p in d["posts"]}
    nuevos = 0
    for fecha, hora, pid, archivos, cuerpo in P:
        if pid in existentes:
            continue
        faltan = [a for a in archivos
                  if not (RAIZ / "contenido" / "publicar" / a).exists()]
        if faltan:
            print(f"  ! {pid}: faltan {faltan[:2]}... corre preparar_imagenes.py")
            continue
        d["posts"].append(dict(id=pid, tipo="carrusel", estado="pendiente",
                               fecha=fecha, hora=hora, archivos=archivos,
                               caption=cuerpo + FIRMA))
        nuevos += 1
    d["posts"].sort(key=lambda p: (p["fecha"], p["hora"]))
    open(RUTA, "w", encoding="utf-8").write(
        json.dumps(d, ensure_ascii=False, indent=2) + "\n")

    largo = max(len(p["caption"]) for p in d["posts"])
    print(f"\n{nuevos} carruseles programados | caption mas larga: {largo} de 2200")
    for p in d["posts"]:
        if p["estado"] == "pendiente":
            print(f"  {p['fecha']} {p['hora']}  {len(p.get('archivos',[]))} placas  {p['id']}")


if __name__ == "__main__":
    main()
