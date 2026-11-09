#!/usr/bin/env python3
"""Cuatro carruseles para @chris.mind2, sacados de la charla del 27/10.

Nada de esto es contenido nuevo: son las diapositivas que Christian ya habia
escrito y presentado ante colegas. El trabajo es cosechar, no inventar — el
pidio explicitamente no tener que generar contenido para Instagram.

El orden de publicacion va de lo conceptual a lo practico a proposito. Los
dos ultimos (formular un caso, las tres preguntas) son checklists, que es el
formato que se guarda: en EM las dos unicas publicaciones que se guardaron
duplicaron el alcance de todas las demas.

Los fondos alternan verde y petroleo entre portadas para que la grilla no
quede plana — solo se ve la primera placa de cada publicacion.

NO se menciona la carga horaria del Diplomado: la diapositiva dice 200 horas
y la landing dice 250, y hasta que Christian no resuelva cual es, no se
publica el numero.
"""
from marca_chris import *


# ── 1 · las tres grietas ──────────────────────────────────────────────────
def c1_grietas():
    return [
        ("p1_grietas_1.png", portada(
            "La pregunta incómoda",
            "El diagnóstico describe síntomas. No dice qué los sostiene.",
            "Es una herramienta de comunicación y de clasificación, y en eso "
            "es útil. El problema aparece cuando le pedimos algo que nunca "
            "prometió dar.", "verde")),
        ("p1_grietas_2.png", punto(
            "01", "La comorbilidad es la regla, no la excepción.",
            "Quien llega con ansiedad suele llegar también con ánimo bajo, "
            "insomnio y evitación. Tratamos personas, no capítulos de un "
            "manual.")),
        ("p1_grietas_3.png", punto(
            "02", "Dentro de una misma categoría, nadie se parece.",
            "Dos personas pueden cumplir el mismo criterio diagnóstico sin "
            "compartir casi ningún síntoma. La etiqueta agrupa cuadros que "
            "funcionan distinto.")),
        ("p1_grietas_4.png", punto(
            "03", "Los protocolos que funcionan comparten ingredientes.",
            "Terapias de escuelas distintas obtienen resultados parecidos. "
            "Algo que tienen en común está haciendo el trabajo, y no es el "
            "nombre del modelo.")),
        ("p1_grietas_5.png", punto(
            None, "El giro no es cambiar de técnica.",
            "Es cambiar de unidad de análisis. Donde antes preguntábamos qué "
            "trastorno tiene esta persona, ahora preguntamos qué procesos "
            "sostienen su sufrimiento y cuáles podrían moverlo.", "petroleo")),
        ("p1_grietas_6.png", cierre(
            "No es una escuela más para sumar a la lista",
            "Es una forma de organizar lo que ya sabés hacer. Nada de lo que "
            "aprendiste se tira: cambia el criterio con el que elegís qué "
            "usar y cuándo.",
            "Psicoterapia basada en procesos", "petroleo")),
    ]


# ── 2 · las seis dimensiones ──────────────────────────────────────────────
def c2_dimensiones():
    D = [
        ("Afecto", "Qué siente, cuánto lo tolera, qué hace para no sentirlo."),
        ("Cognición", "Qué se dice, y cuánto se lo cree. La relación con el "
                      "pensamiento, no su contenido."),
        ("Atención", "Dónde se le va, cuánto puede volver, si queda enganchada."),
        ("Self", "Quién cree que es. Qué historia sobre sí mismo defiende."),
        ("Motivación", "Qué lo mueve, qué importa de verdad, qué dejó de hacer."),
        ("Conducta", "Qué hace y qué deja de hacer. Lo observable, que suele "
                     "ser lo último que preguntamos."),
    ]
    placas = [("p2_dim_1.png", portada(
        "Dónde mirar", "Seis dimensiones donde vive un proceso",
        "Cuando la etiqueta no alcanza para decidir qué hacer, estos son los "
        "seis lugares donde buscar.", "petroleo"))]
    for i, (titulo, cuerpo) in enumerate(D, start=1):
        placas.append((f"p2_dim_{i + 1}.png", punto(f"0{i}", titulo, cuerpo)))
    placas.append(("p2_dim_8.png", cierre(
        "Y todo atravesado por dos contextos",
        "El biológico —sueño, dolor, medicación— y el sociocultural: con "
        "quién vive, qué trabajo tiene, quién lo sostiene. Ninguno de los dos "
        "se puede ignorar.",
        "Hayes, Hofmann y Lorscheid (2025)", "verde")))
    return placas


# ── 3 · formular un caso ──────────────────────────────────────────────────
def c3_formular():
    P = [
        ("Describí la secuencia, no el rasgo.",
         "Qué pasa, en qué orden, desde el disparador hasta lo que la persona "
         "hace y lo que obtiene con eso."),
        ("Buscá qué lo mantiene.",
         "Casi siempre hay un alivio a corto plazo que paga el costo a largo "
         "plazo. Ese alivio es el que hay que tocar."),
        ("Elegí un proceso, uno solo, para empezar.",
         "El más modificable y el que más desbloquea a los otros. No el más "
         "interesante."),
        ("Definí cómo vas a saber si se movió.",
         "Un indicador que la persona pueda reportar, observable antes de un "
         "mes."),
        ("Revisá y corregí.",
         "Si en cuatro o seis sesiones no se movió, el problema es la "
         "formulación, no la adherencia del paciente."),
    ]
    placas = [("p3_caso_1.png", portada(
        "Lo concreto", "Cómo se formula un caso desde procesos",
        "Cinco pasos para usar el martes que viene, sin cambiar de modelo.",
        "verde"))]
    for i, (titulo, cuerpo) in enumerate(P, start=1):
        placas.append((f"p3_caso_{i + 1}.png", punto(str(i), titulo, cuerpo)))
    placas.append(("p3_caso_7.png", cierre(
        "El quinto paso es el que más cuesta",
        "Cuando un tratamiento no avanza, la primera hipótesis no debería ser "
        "que el paciente no colabora. Suele ser que la formulación estaba mal.",
        None, "petroleo")))
    return placas


# ── 4 · las tres preguntas ────────────────────────────────────────────────
def c4_preguntas():
    return [
        ("p4_preg_1.png", portada(
            "Para llevarse", "Tres preguntas para la próxima primera entrevista",
            "Una por cada proceso. No hace falta cambiar de modelo para "
            "empezar a escuchar distinto.", "petroleo")),
        ("p4_preg_2.png", punto(
            "01", "«¿Qué dejaste de hacer desde que esto empezó?»",
            "Abre la conducta y la motivación a la vez: qué se achicó, y qué "
            "importaba lo suficiente como para que doliera perderlo.")),
        ("p4_preg_3.png", punto(
            "02", "«Cuando aparece, ¿qué hacés? ¿Y eso cómo te deja un rato después?»",
            "Ahí aparece el alivio a corto plazo que sostiene el problema. "
            "Casi nadie lo nombra solo.")),
        ("p4_preg_4.png", punto(
            "03", "«¿Qué te dirías a vos mismo si un amigo te contara esto?»",
            "Deja a la vista la distancia entre cómo se trata a sí mismo y "
            "cómo trataría a otro. Es la puerta de entrada a la compasión.")),
        ("p4_preg_5.png", cierre(
            "Guardátelas para el martes",
            "No reemplazan una evaluación. Pero cambian lo que escuchás en "
            "los primeros veinte minutos, que es cuando se decide casi todo.",
            None, "verde")),
    ]


def main():
    placas = c1_grietas() + c2_dimensiones() + c3_formular() + c4_preguntas()
    guardar(placas, "preview_procesos.jpg", cols=6)


if __name__ == "__main__":
    main()
