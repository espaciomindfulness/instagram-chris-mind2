#!/usr/bin/env python3
"""Sistema de diseno de @chris.mind2.

Deliberadamente distinto del de Espacio Mindfulness. Si la cuenta personal se
ve como un segundo feed institucional, pierde lo unico que la hace funcionar:
que del otro lado hay una persona. Por eso aca NO va el isotipo en cada placa,
los fondos son mas oscuros y sobrios, y el pie es el usuario, no la marca.

La paleta no se invento: se muestreo de las diapositivas que Christian uso en
su charla del 27/10, asi que el feed queda coherente con el material con el
que se presenta ante colegas.

  verde profundo  #1F2F2F   fondo principal
  petroleo        #2F4A4B   fondo secundario, para alternar en la grilla
  crema           #F8F8F3   fondo claro y texto sobre oscuro
  dorado          #BDA058   acento, numeros y reglas

Tipografia: Cambria (serif) + Segoe UI (sans). EM usa Georgia + Calibri; el
cambio de familia es parte de que se note que son dos cuentas distintas.

Formato 1080x1350 (4:5), el que mas pantalla ocupa en el feed.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1350
MARGEN = 96

VERDE = (31, 47, 47)
PETROLEO = (47, 74, 75)
CREMA = (248, 248, 243)
DORADO = (189, 160, 88)
TINTA = (26, 38, 38)          # texto sobre crema
GRIS = (92, 106, 106)         # cuerpo sobre crema
CREMA_SUAVE = (214, 219, 215)  # cuerpo sobre oscuro

F = "C:/Windows/Fonts/"
SERIF_B, SERIF_I = "cambriab.ttf", "cambriai.ttf"
SANS, SANS_B, SANS_L = "segoeui.ttf", "segoeuib.ttf", "segoeuil.ttf"

RAIZ = Path(__file__).resolve().parent.parent
DESTINO = RAIZ / "contenido" / "originales"

TONOS = {
    "verde":    dict(fondo=VERDE,    titulo=CREMA, cuerpo=CREMA_SUAVE,
                     acento=DORADO, pie=(140, 156, 152)),
    "petroleo": dict(fondo=PETROLEO, titulo=CREMA, cuerpo=CREMA_SUAVE,
                     acento=DORADO, pie=(160, 180, 176)),
    "crema":    dict(fondo=CREMA,    titulo=TINTA, cuerpo=GRIS,
                     acento=DORADO, pie=(150, 158, 154)),
}


def fuente(nombre, tam):
    return ImageFont.truetype(F + nombre, tam)


def ancho(d, texto, fnt):
    return d.textbbox((0, 0), texto, font=fnt)[2]


def envolver(d, texto, fnt, max_ancho):
    lineas, actual = [], ""
    for p in texto.split():
        prueba = f"{actual} {p}".strip()
        if ancho(d, prueba, fnt) <= max_ancho:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = p
    if actual:
        lineas.append(actual)
    return lineas


def alto_parrafo(d, texto, fnt, max_ancho, interlinea=1.42):
    return int(len(envolver(d, texto, fnt, max_ancho)) * fnt.size * interlinea)


def parrafo(d, texto, fnt, x, y, max_ancho, color, interlinea=1.42, centrado=False):
    salto = int(fnt.size * interlinea)
    for i, linea in enumerate(envolver(d, texto, fnt, max_ancho)):
        px = x + (max_ancho - ancho(d, linea, fnt)) // 2 if centrado else x
        d.text((px, y + i * salto), linea, font=fnt, fill=color)
    return y + len(envolver(d, texto, fnt, max_ancho)) * salto


def espaciado(d, texto, fnt, x, y, color, sep=6, centrado_en=None):
    total = sum(ancho(d, c, fnt) + sep for c in texto) - sep
    px = x if centrado_en is None else (centrado_en - total) // 2
    for c in texto:
        d.text((px, y), c, font=fnt, fill=color)
        px += ancho(d, c, fnt) + sep
    return total


def pie(d, color, texto="@chris.mind2"):
    espaciado(d, texto, fuente(SANS, 28), 0, H - 76, color, sep=3, centrado_en=W)


def lienzo(fondo):
    return Image.new("RGB", (W, H), fondo)


def flecha(d, x, y, color, s=18):
    d.polygon([(x, y - s / 2), (x + s * 0.85, y), (x, y + s / 2)], fill=color)


# --- piezas ---------------------------------------------------------------

def portada(etiqueta, titulo, bajada, tono="verde"):
    t = TONOS[tono]
    img = lienzo(t["fondo"])
    d = ImageDraw.Draw(img)
    util = W - 2 * MARGEN

    espaciado(d, etiqueta.upper(), fuente(SANS_B, 28), MARGEN, 190, t["acento"], sep=7)
    d.line([(MARGEN, 252), (MARGEN + 64, 252)], fill=t["acento"], width=3)

    f_t = fuente(SERIF_B, 88 if len(titulo) < 48 else 72)
    y = parrafo(d, titulo, f_t, MARGEN, 330, util, t["titulo"], interlinea=1.18)
    parrafo(d, bajada, fuente(SANS_L, 42), MARGEN, y + 56, util - 40, t["cuerpo"],
            interlinea=1.48)

    total = espaciado(d, "DESLIZÁ", fuente(SANS_B, 30), MARGEN, H - 210,
                      t["acento"], sep=6)
    flecha(d, MARGEN + total + 18, H - 197, t["acento"])
    pie(d, t["pie"])
    return img


def punto(numero, titulo, cuerpo, tono="crema"):
    t = TONOS[tono]
    img = lienzo(t["fondo"])
    d = ImageDraw.Draw(img)
    util = W - 2 * MARGEN

    if numero:
        d.text((MARGEN, 170), str(numero), font=fuente(SERIF_B, 150), fill=t["acento"])
        arranque = 380
    else:
        arranque = 230

    f_t, f_c = fuente(SERIF_B, 62), fuente(SANS, 44)
    alto = (alto_parrafo(d, titulo, f_t, util, 1.22) + 46
            + alto_parrafo(d, cuerpo, f_c, util, 1.50))
    y = arranque + max(0, (H - 200 - arranque - alto) // 2)
    y = parrafo(d, titulo, f_t, MARGEN, y, util, t["titulo"], interlinea=1.22)
    parrafo(d, cuerpo, f_c, MARGEN, y + 46, util, t["cuerpo"], interlinea=1.50)
    pie(d, t["pie"])
    return img


def cierre(titulo, cuerpo, remate=None, tono="petroleo"):
    t = TONOS[tono]
    img = lienzo(t["fondo"])
    d = ImageDraw.Draw(img)
    util = W - 2 * MARGEN

    f_t = fuente(SERIF_B, 76 if len(titulo) < 40 else 64)
    alto = (alto_parrafo(d, titulo, f_t, util, 1.20) + 60
            + alto_parrafo(d, cuerpo, fuente(SANS, 44), util, 1.50))
    y = max(300, (H - 260 - alto) // 2)
    y = parrafo(d, titulo, f_t, MARGEN, y, util, t["titulo"], interlinea=1.20)
    d.line([(MARGEN, y + 34), (MARGEN + 64, y + 34)], fill=t["acento"], width=3)
    y = parrafo(d, cuerpo, fuente(SANS, 44), MARGEN, y + 78, util, t["cuerpo"],
                interlinea=1.50)
    if remate:
        espaciado(d, remate.upper(), fuente(SANS_B, 28), MARGEN, y + 56,
                  t["acento"], sep=5)
    pie(d, t["pie"])
    return img


def suelta(etiqueta, titulo, cuerpo, tono="verde"):
    """Placa de un solo golpe, para posteos que no son carrusel."""
    t = TONOS[tono]
    img = lienzo(t["fondo"])
    d = ImageDraw.Draw(img)
    util = W - 2 * MARGEN

    espaciado(d, etiqueta.upper(), fuente(SANS_B, 28), MARGEN, 200, t["acento"], sep=7)
    f_t = fuente(SERIF_B, 84 if len(titulo) < 44 else 68)
    alto = (alto_parrafo(d, titulo, f_t, util, 1.20) + 56
            + alto_parrafo(d, cuerpo, fuente(SANS_L, 44), util, 1.50))
    y = 300 + max(0, (H - 240 - 300 - alto) // 2)
    y = parrafo(d, titulo, f_t, MARGEN, y, util, t["titulo"], interlinea=1.20)
    d.line([(MARGEN, y + 32), (MARGEN + 64, y + 32)], fill=t["acento"], width=3)
    parrafo(d, cuerpo, fuente(SANS_L, 44), MARGEN, y + 76, util, t["cuerpo"],
            interlinea=1.50)
    pie(d, t["pie"])
    return img


def guardar(placas, nombre_preview=None, cols=6):
    DESTINO.mkdir(parents=True, exist_ok=True)
    for nombre, img in placas:
        img.save(DESTINO / nombre)
        print("  +", nombre, img.size)
    if not nombre_preview:
        return
    tw, th = 300, 375
    filas = (len(placas) + cols - 1) // cols
    hoja = Image.new("RGB", (cols * tw, filas * th), "white")
    for i, (_, img) in enumerate(placas):
        mini = img.copy()
        mini.thumbnail((tw - 8, th - 8))
        hoja.paste(mini, ((i % cols) * tw + 4, (i // cols) * th + 4))
    salida = Path(__file__).resolve().parent / nombre_preview
    hoja.save(salida, quality=90)
    print("preview:", salida)
