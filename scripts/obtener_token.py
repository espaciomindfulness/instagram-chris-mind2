#!/usr/bin/env python3
"""
Ayudante para conseguir el token de larga duracion y el IG_USER_ID usando la
Instagram API con Login de Instagram (SIN pagina de Facebook).

Por que existe este script:
  Con el Login de Instagram, el token que genera el panel de Meta puede venir
  de corta duracion (1 hora) o ya de larga (60 dias). Este script:
    1. Si hace falta, cambia el token corto por uno largo de 60 dias.
    2. Averigua el ID numerico de tu cuenta de Instagram.
    3. Te dice exactamente que dos valores cargar como Secrets del repo.

  A diferencia de las paginas de Facebook (cuyo token no expiraba), el token
  de Instagram dura 60 dias. Por eso el repo incluye un refresco automatico
  (scripts/refrescar_token.py + workflow) que lo renueva solo cada semana.

Que necesitas antes de correrlo (ver SETUP.md paso a paso):
  1. App creada en developers.facebook.com con el producto "Instagram"
     configurado con "API setup with Instagram business login".
  2. App Secret de esa app (App settings -> Basic).
  3. Un token generado desde el panel de la app, en la seccion del producto
     Instagram -> "Generate token" para tu cuenta @espaciomindfulness,
     con los permisos:
        instagram_business_basic
        instagram_business_content_publish

Uso:
    python scripts/obtener_token.py
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.parse
import urllib.request

GRAPH = "https://graph.instagram.com"


def get(url: str, **params) -> dict:
    completa = f"{url}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(completa, timeout=60) as respuesta:
            return json.loads(respuesta.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detalle = exc.read().decode("utf-8", "replace")
        return {"__error__": f"HTTP {exc.code}: {detalle}"}
    except urllib.error.URLError as exc:
        sys.exit(f"\nNo se pudo conectar con Instagram: {exc.reason}\n")


def preguntar(texto: str) -> str:
    valor = input(texto).strip()
    if not valor:
        sys.exit("Valor vacio, abortando.")
    return valor


def main() -> None:
    print(__doc__)
    print("=" * 70)
    app_secret = preguntar("App Secret: ")
    token = preguntar("Token generado en el panel (Instagram -> Generate token): ")

    print("\n[1/2] Asegurando un token de larga duracion (60 dias)...")
    # ig_exchange_token cambia un token corto por uno largo. Si el token ya es
    # largo, Meta devuelve un error: en ese caso seguimos con el que tenemos.
    largo = get(
        f"{GRAPH}/access_token",
        grant_type="ig_exchange_token",
        client_secret=app_secret,
        access_token=token,
    )
    if "access_token" in largo:
        token = largo["access_token"]
        dias = int(largo.get("expires_in", 0)) // 86400
        print(f"      ok: token largo obtenido (valido ~{dias} dias)")
    else:
        # Ya era largo, o el corto no admite intercambio. Verificamos que sirva.
        print("      el token ya parece de larga duracion; sigo con ese.")

    print("[2/2] Verificando el token y buscando el ID de tu cuenta...")
    yo = get(
        f"{GRAPH}/me",
        fields="user_id,username",
        access_token=token,
    )
    if "__error__" in yo:
        sys.exit(
            "\nEl token no es valido o le faltan permisos.\n"
            f"Detalle: {yo['__error__']}\n\n"
            "Regenera el token en el panel de la app (producto Instagram),\n"
            "asegurandote de marcar los permisos instagram_business_basic e\n"
            "instagram_business_content_publish, y volve a correr este script."
        )

    user_id = str(yo.get("user_id") or yo.get("id") or "")
    usuario = yo.get("username", "?")
    if not user_id:
        sys.exit(f"\nNo pude leer el ID de la cuenta. Respuesta: {yo}\n")

    print(f"      ok: Instagram @{usuario}  (id {user_id})")

    print("\n" + "=" * 70)
    print("LISTO. Carga estos dos valores como Secrets del repositorio:")
    print("  Settings -> Secrets and variables -> Actions -> New repository secret\n")
    print(f"  IG_USER_ID       {user_id}")
    print(f"  IG_ACCESS_TOKEN  {token}")
    print("\nEl token dura 60 dias, pero el refresco automatico del repo lo")
    print("renueva solo. No compartas ni subas el token a ningun archivo del repo.")
    print("=" * 70)


if __name__ == "__main__":
    main()
