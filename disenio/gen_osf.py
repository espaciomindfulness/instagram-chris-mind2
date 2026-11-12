#!/usr/bin/env python3
"""Carrusel: el curriculum del MBSR es de acceso libre.

Va solo en @chris.mind2 y no en Espacio Mindfulness. El carrusel del
encuentro —que salio como colaborativo entre las dos cuentas— cubre la
noticia; este es el angulo util para colegas, que es lo que funciona en esta
cuenta. Asi las dos no publican lo mismo con distinta cara.

Es el tipo de pieza que se guarda: un recurso concreto, gratis, que el lector
se lleva. En EM medimos que lo que se guarda es lo unico que llega a gente
que no te sigue.

Verificado el 12/11/2026 contra la API de OSF: el proyecto "2026 MBSR
Curriculum and Teaching Guide" existe y es publico.

Cuidados: la credencial de Christian es del GMC, nunca de Brown. No se
argumenta nunca contra el formato de ocho semanas. Nada que sugiera que el
lector puede no estar a la altura. Sin precios.
"""
from marca_chris import *


def c5_osf():
    return [
        ("p5_osf_1.png", portada(
            "Un dato poco conocido",
            "El currículum completo del MBSR es público",
            "Doscientas treinta y dos páginas, gratis y sin registro. Está "
            "en OSF desde octubre.", "verde")),
        ("p5_osf_2.png", punto(
            "01", "Está entero, no es un resumen.",
            "Las ocho clases una por una, la jornada de práctica intensiva y "
            "ocho apéndices: el espíritu de la enseñanza, cómo darlo online, "
            "los materiales para participantes, las lecturas.")),
        ("p5_osf_3.png", punto(
            "02", "Lo revisó quien creó el programa.",
            "La edición 2026 la publicaron Brown University School of "
            "Professional Studies y el Global Mindfulness Collaborative, con "
            "revisiones directas de Jon Kabat-Zinn.")),
        ("p5_osf_4.png", punto(
            "03", "Y te deja chequear.",
            "Si hacés un MBSR, o pensás hacerlo, podés leer el currículum y "
            "ver si lo que te dan es eso. En un campo donde no hay matrícula "
            "que regule, poder verificar vale mucho.")),
        ("p5_osf_5.png", cierre(
            "Está en osf.io/tckb3",
            "Acceso libre, sin registro y sin pago. Lo bajé entero: son 31 "
            "archivos, incluido el currículum original de 1993 para comparar.",
            "Guardátelo para cuando lo necesites", "petroleo")),
    ]


def main():
    guardar(c5_osf(), "preview_osf.jpg", cols=5)


if __name__ == "__main__":
    main()
