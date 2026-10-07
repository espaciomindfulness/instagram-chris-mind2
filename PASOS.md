# Lo que falta para que @chris.mind2 publique solo

El pipeline ya está armado y validado (`python scripts/validar.py` dice
"Todo en orden"). Faltan los pasos que solo puede hacer una persona con la
sesión de Meta y de GitHub abiertas.

Es más corto que las dos cuentas anteriores porque **se reusa la misma app de
Meta** ("Publicador EM"): una app admite varias cuentas de Instagram y así no
hay que repetir la verificación de desarrollador.

**Requisito:** @chris.mind2 tiene que ser cuenta profesional (Empresa o
Creador). Si ves "Panel profesional" en la app, ya lo es.

## 1 · Rol en la app de Meta

developers.facebook.com/apps → "Publicador EM" → **Roles de la aplicación →
Roles** → agregar **Evaluador de Instagram** → `chris.mind2`.

> Si rebota con *"You don't have access"*, no es un bloqueo: es la sesión
> equivocada en el navegador. Abrir en incógnito con el perfil personal.

## 2 · Aceptar la invitación

Logueado como @chris.mind2:
instagram.com/accounts/manage_access/ → aceptar la invitación pendiente.

## 3 · Conectar y generar el token

En la app → **Instagram → API setup with Instagram business login** →
**Add account** → login de Instagram (no de Facebook) → autorizar →
**Generate token**.

## 4 · Token de 60 días

```bash
python scripts/obtener_token.py
```

Pide el App Secret (el de siempre) y el token recién generado. Devuelve
`IG_USER_ID` y `IG_ACCESS_TOKEN`. **No van a ningún archivo del repo**: van a
los Secrets de GitHub, que están cifrados.

## 5 · Repo en GitHub

Crear `instagram-chris-mind2`, **público** (Instagram necesita bajar los
videos desde raw.githubusercontent.com).

Después, desde esta carpeta:

```bash
git remote add origin https://github.com/espaciomindfulness/instagram-chris-mind2.git
git push -u origin main
```

## 6 · Secrets y permisos

En el repo → **Settings → Secrets and variables → Actions**:

- `IG_USER_ID` y `IG_ACCESS_TOKEN` — los del paso 4.
- `GH_PAT` — **no generar uno nuevo**: entrar al que ya existe en
  github.com/settings/personal-access-tokens y agregarle este repo a la lista
  de repositorios permitidos.

Y en **Settings → Actions → General → Workflow permissions**: **Read and
write permissions**.

## 7 · Probar sin publicar

- **Actions → Probar un reel sin publicarlo → Run workflow**: verifica que
  Meta pueda bajar y procesar el video.
- **Actions → Publicar en Instagram → Run workflow** con **Simulacro**
  activado: dice qué publicaría, sin publicar.

Cuando el simulacro se vea bien, el cron de cada 30 minutos se encarga del
resto.

---

## Qué hay cargado

Tres reels de la charla del Diplomado, del 20 al 28 de octubre:

| Fecha | Reel |
|---|---|
| 20/10 19:00 | No es la técnica, falta el mapa |
| 24/10 19:00 | Nadie viene con una sola etiqueta |
| 28/10 19:00 | El caso concreto |

Los otros dos recortes de la misma charla van en @espaciomindfulness (23 y 27
de octubre), para que las dos cuentas empujen el mismo tema sin publicar lo
mismo. El carrusel del Diplomado en EM cierra la secuencia el 29/10.

Si el alta en Meta se demora más allá del 20, correr las fechas en
`disenio/programar_charla.py` y volver a correrlo.
