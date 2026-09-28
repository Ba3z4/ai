#!/usr/bin/env python3
"""Genera shotlist-kling.md, keyframes.md y storyboard.html a partir de plan.json.

Uso:
    python3 herramientas/generar.py
    python3 herramientas/generar.py --artefacto salida.html   # versión sin <head>, para publicarla como Artifact
"""

import argparse
import json
from html import escape
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
AVISO = "<!-- Archivo generado por herramientas/generar.py a partir de plan.json. Edita plan.json y vuelve a generar. -->"
LUCES = {
    "calida": "Tungsteno cálido",
    "luna": "Luna fría",
    "dorada": "Hora dorada",
    "dia": "Luz de día",
}


def cargar():
    return json.loads((RAIZ / "plan.json").read_text(encoding="utf-8"))


def mmss(segundos):
    return f"{segundos // 60}:{segundos % 60:02d}"


def todos_los_planos(plan):
    return [p for esc in plan["escenas"] for p in esc["planos"]]


def secuencia(plan):
    """Planos y extras (negro, título) en orden de montaje, con su segundo de entrada."""
    extras = {}
    for extra in plan["montaje_extras"]:
        extras.setdefault(extra["despues_de"], []).append(extra)
    t, filas = 0, []
    for esc in plan["escenas"]:
        for p in esc["planos"]:
            filas.append({"id": p["id"], "titulo": p["titulo"], "uso": p["uso"], "entra": t,
                          "escena": esc["num"], "luz": esc["luz"], "extra": False})
            t += p["uso"]
            for e in extras.get(p["id"], []):
                filas.append({"id": e["id"], "titulo": e["titulo"], "uso": e["uso"], "entra": t,
                              "escena": esc["num"], "luz": "extra", "extra": True})
                t += e["uso"]
    return filas, t


class Indice:
    """Resuelve los IDs de imagen del plan (ref01, K4, el-alex, 4A-ultimo) a archivo y etiqueta."""

    def __init__(self, plan):
        self.refs = {r["id"]: r for r in plan["referencias"]}
        self.kfs = {k["id"]: k for k in plan["keyframes"]}
        self.elements = {"el-" + e["id"].lower(): e for e in plan["elements"]}

    def etiqueta(self, ident):
        if ident in self.refs:
            return f"Ref. {ident[3:]}"
        if ident in self.kfs:
            return f"{ident} · {self.kfs[ident]['titulo']}"
        if ident in self.elements:
            return f"Recorte «{self.elements[ident]['id']}»"
        if ident.endswith("-ultimo"):
            return f"Último cuadro de {ident.split('-')[0]}"
        raise KeyError(ident)

    def corta(self, ident):
        return ident if ident in self.kfs else self.etiqueta(ident)

    def archivo(self, ident):
        if ident in self.refs:
            return self.refs[ident]["archivo"]
        if ident in self.elements:
            return self.elements[ident]["imagen"]
        return None


# ---------------------------------------------------------------- Markdown

def md_bloque(texto):
    return f"```text\n{texto}\n```"


def md_imagen(indice, ident, ancho):
    archivo = indice.archivo(ident)
    return f'<img src="{archivo}" width="{ancho}" alt="{indice.etiqueta(ident)}">' if archivo else ""


def md_cuadro(indice, ident):
    if ident in indice.kfs:
        return f"[{indice.etiqueta(ident)}](keyframes.md#{ident.lower()})"
    return indice.etiqueta(ident)


def shotlist_md(plan, indice):
    planos = todos_los_planos(plan)
    filas, total = secuencia(plan)
    opcionales = sum(1 for p in planos if p.get("opcional"))
    L = [AVISO, "", f"# {plan['titulo']} · Shotlist para Kling AI", "", plan["logline"], "",
         f"**Formato:** {plan['formato']}  ",
         f"**Planos:** {len(planos)} ({opcionales} opcional) · **Montaje:** {mmss(total)} · "
         f"**Generación:** {sum(p['genera'] for p in planos)} s por pasada completa", "",
         "Los prompts de las imágenes que faltan están en [keyframes.md](keyframes.md). "
         "La versión visual, con botones para copiar, es [storyboard.html](storyboard.html) (ábrela en el navegador).", "",
         "## Antes de empezar", "", "### Flujo", ""]
    L += [f"{i}. {paso}" for i, paso in enumerate(plan["flujo"], 1)]
    L += ["", "### Ajustes en Kling", "", "| Ajuste | Valor |", "|---|---|"]
    L += [f"| {clave} | {valor} |" for clave, valor in plan["ajustes"]]
    L += ["", "### Elements", "", "| Element | Imagen | Cómo se arma | Úsalo en |", "|---|---|---|---|"]
    L += [f"| **{e['id']}** | <img src=\"{e['imagen']}\" width=\"110\" alt=\"{e['id']}\"> | {e['fuente']} | {e['usar_en']} |"
          for e in plan["elements"]]
    L += ["", "### Referencias", "", "| Ref. | Imagen | Qué es | Se usa en |", "|---|---|---|---|"]
    L += [f"| {r['id'][3:]} | <img src=\"{r['archivo']}\" width=\"200\" alt=\"{r['titulo']}\"> | "
          f"**{r['titulo']}.** {r['descripcion']} | {r['usa_en']} |" for r in plan["referencias"]]
    L += ["", "### Continuidad: revisa esto antes de generar", ""]
    L += [f"- **{c['nivel']} · {c['titulo']}.** {c['detalle']}" for c in plan["continuidad"]]
    L += ["", '<a id="linea-de-tiempo"></a>', "", "## Línea de tiempo del montaje", "",
          "| Entra | Sale | Dura | Plano | Escena |", "|---|---|---|---|---|"]
    for f in filas:
        nombre = f"_{f['id']}: {f['titulo']}_" if f["extra"] else f"[**{f['id']}** · {f['titulo']}](#{f['id'].lower()})"
        L.append(f"| {mmss(f['entra'])} | {mmss(f['entra'] + f['uso'])} | {f['uso']} s | {nombre} | {f['escena']} |")
    L.append("")
    for esc in plan["escenas"]:
        L += [f"## Escena {esc['num']} · {esc['titulo']}", "", f"`{esc['slug']}`", "", esc["resumen"], "",
              f"- **Luz:** {LUCES[esc['luz']]}. {esc['color']}",
              "- **Paleta:** " + " · ".join(f"{nombre} `{hexa}`" for nombre, hexa in esc["paleta"]),
              f"- **Sonido:** {esc['sonido']}", ""]
        for p in esc["planos"]:
            L += [f'<a id="{p["id"].lower()}"></a>', "",
                  f"### {p['id']} · {p['titulo']}" + (" (opcional)" if p.get("opcional") else ""), ""]
            imagenes = [md_imagen(indice, i, 360) for i in (p["inicio"], p.get("fin")) if i]
            imagenes = [i for i in imagenes if i]
            if imagenes:
                L += [" ".join(imagenes), ""]
            inicio = md_cuadro(indice, p["inicio"])
            if p.get("inicio_alt"):
                inicio += f" (o {md_cuadro(indice, p['inicio_alt'])})"
            fin = md_cuadro(indice, p["fin"]) if p.get("fin") else "—"
            L += ["| Genera | Usa | Fotograma inicial | Fotograma final | Elements |", "|---|---|---|---|---|",
                  f"| {p['genera']} s | {p['uso']} s | {inicio} | {fin} | {', '.join(p['elements']) or '—'} |", "",
                  f"**Cámara:** {p['camara']}  ", f"**Qué pasa:** {p['accion']}", "",
                  "**Prompt**", "", md_bloque(p["prompt"]), "",
                  "**Negative prompt**", "", md_bloque(plan["negativos"][p["negativo"]]), ""]
            if p.get("audio"):
                L += ["**Audio nativo** (opcional: pégalo al final del prompt si activas el audio)", "", md_bloque(p["audio"]), ""]
            if p.get("notas"):
                L += [f"> {p['notas']}", ""]
    return "\n".join(L).rstrip() + "\n"


def keyframes_md(plan, indice):
    L = [AVISO, "", f"# {plan['titulo']} · Keyframes", "",
         "Son las imágenes que faltan para animar los planos. Genéralas **antes** que los videos, en 16:9 y a la mayor resolución que permita tu plan.", "",
         "- En Kling usa **Imágenes** con referencia (o edición con varias referencias, según tu versión). Cualquier generador con referencias sirve.",
         "- «The reference image» o «the first/second reference image» son las imágenes que subes, en ese orden. "
         "Si tu herramienta usa etiquetas (por ejemplo @imagen1), cámbialas en el prompt.",
         "- Genera 3 o 4 variantes y quédate con la que mejor respete la continuidad (ver [shotlist-kling.md](shotlist-kling.md)).", "",
         "| Keyframe | Se usa en |", "|---|---|"]
    L += [f"| [{k['id']} · {k['titulo']}](#{k['id'].lower()}){' (opcional)' if k.get('opcional') else ''} | {k['usa_en']} |"
          for k in plan["keyframes"]]
    L.append("")
    for k in plan["keyframes"]:
        L += [f'<a id="{k["id"].lower()}"></a>', "",
              f"## {k['id']} · {k['titulo']}" + (" (opcional)" if k.get("opcional") else ""), ""]
        imagenes = [i for i in (md_imagen(indice, b, 220) for b in k["base"]) if i]
        if imagenes:
            L += [" ".join(imagenes), ""]
        L += [f"**Referencias:** {', '.join(indice.etiqueta(b) for b in k['base'])}  ",
              f"**Se usa en:** {k['usa_en']}  ", f"**Cómo:** {k['como']}", "", md_bloque(k["prompt"]), ""]
        if k.get("notas"):
            L += [f"> {k['notas']}", ""]
    return "\n".join(L).rstrip() + "\n"


# ---------------------------------------------------------------- HTML

TITULO_PAGINA = "Storyboard de La Incisión"

FUENTES = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:wght@500;700&family=Courier+Prime:wght@400;700&family=IBM+Plex+Sans:wght@400;500;600&display=swap">"""

ESTILOS = """
:root{
  color-scheme:light;
  --bg:#ECEEF1; --surface:#F9FAFB; --sunken:#E3E7EB; --ink:#15191E; --muted:#58626D; --rule:#CCD2D8;
  --accent:#A3182C; --focus:#2B6CB0; --ok:#2C7A4B; --on-seg:#FFFFFF;
  --calida:#9A5413; --luna:#34536F; --dorada:#86650F; --dia:#56676D;
  --serif:"Bodoni Moda", Didot, "Bodoni 72", "Times New Roman", serif;
  --sans:"IBM Plex Sans", system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  --mono:"Courier Prime", "Courier New", Courier, monospace;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    color-scheme:dark;
    --bg:#0B0E12; --surface:#131820; --sunken:#0E1217; --ink:#E4E8EC; --muted:#8F9AA6; --rule:#28313B;
    --accent:#E5495E; --focus:#8AB8E6; --ok:#5BC48A; --on-seg:#0B0E12;
    --calida:#E09A58; --luna:#8AB0D4; --dorada:#E2BD5E; --dia:#AFBEC3;
  }
}
:root[data-theme="dark"]{
  color-scheme:dark;
  --bg:#0B0E12; --surface:#131820; --sunken:#0E1217; --ink:#E4E8EC; --muted:#8F9AA6; --rule:#28313B;
  --accent:#E5495E; --focus:#8AB8E6; --ok:#5BC48A; --on-seg:#0B0E12;
  --calida:#E09A58; --luna:#8AB0D4; --dorada:#E2BD5E; --dia:#AFBEC3;
}
*,*::before,*::after{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 var(--sans);-webkit-font-smoothing:antialiased}
img{max-width:100%;display:block}
a{color:inherit;text-underline-offset:3px}
:focus-visible{outline:2px solid var(--focus);outline-offset:2px;border-radius:2px}
.page{max-width:1120px;margin:0 auto;padding-inline:20px;padding-block:40px 72px}
@media (max-width:520px){.page{padding-inline:16px;padding-block:28px 56px}}
[id]{scroll-margin-top:72px}

.eyebrow{margin:0 0 18px;font:600 12px/1.3 var(--sans);letter-spacing:.16em;text-transform:uppercase;color:var(--muted)}
.title{position:relative;display:inline-block;margin:0 0 24px;font:700 clamp(40px,11vw,120px)/.92 var(--serif);letter-spacing:.03em;text-transform:uppercase;text-wrap:balance}
.title::after{content:"";position:absolute;left:-3%;right:-3%;top:52%;height:18px;transform:translateY(-50%) rotate(-1.5deg);pointer-events:none;
  background:linear-gradient(var(--accent),var(--accent)) center/100% 2px no-repeat,
    repeating-linear-gradient(90deg,transparent 0 11px,var(--accent) 11px 13px,transparent 13px 24px) center/100% 16px no-repeat}
.logline{max-width:62ch;margin:0 0 28px;font-size:17px}
.meta{display:flex;flex-wrap:wrap;gap:14px 32px;margin:0;padding-top:18px;border-top:1px solid var(--rule)}
.meta div{display:grid;gap:2px}
.meta dt{font:600 11px/1.2 var(--sans);letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.meta dd{margin:0;font:500 18px/1.3 var(--sans);font-variant-numeric:tabular-nums}

.jump{position:sticky;top:env(safe-area-inset-top,0px);z-index:10;display:flex;gap:6px;overflow-x:auto;scrollbar-width:none;
  margin-top:32px;padding-block:10px;background:var(--bg);border-bottom:1px solid var(--rule);
  box-shadow:0 0 0 100vmax var(--bg);clip-path:inset(0 -100vmax)}
.jump::-webkit-scrollbar{display:none}
.jump a{flex:0 0 auto;display:inline-flex;align-items:center;gap:7px;padding:7px 12px;border:1px solid var(--rule);border-radius:999px;
  background:var(--surface);font:500 13px/1 var(--sans);text-decoration:none}
.jump a:hover{border-color:var(--ink)}
.jump i{width:8px;height:8px;border-radius:50%;background:var(--luz)}

.block{padding-block:48px 8px}
.sec{margin:0 0 6px;font:700 clamp(28px,5vw,40px)/1.1 var(--serif);text-wrap:balance}
.lede{margin:0 0 22px;max-width:65ch;color:var(--muted)}
.sub{margin:32px 0 12px;font:600 12px/1.3 var(--sans);letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}

.tl{display:grid;gap:6px;margin-top:6px}
.tl-escenas{display:flex;font:600 11px/1 var(--sans);letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}
.tl-escenas span{min-width:0;overflow:hidden;white-space:nowrap;padding:0 0 5px 6px;border-left:1px solid var(--muted)}
.tl-escenas em{font-style:normal}
@media (max-width:620px){.tl-escenas em{display:none}}
.tl-barra{display:flex;height:42px;border-radius:3px;overflow:hidden;background:var(--sunken)}
.seg{display:flex;align-items:center;justify-content:center;min-width:0;text-decoration:none;color:var(--on-seg);
  font:600 11px/1 var(--sans);box-shadow:inset -1px 0 0 var(--bg)}
.seg span{white-space:nowrap}
.seg.estrecho span{visibility:hidden}
.seg:hover{filter:brightness(1.12)}
.seg-calida{background:var(--calida)} .seg-luna{background:var(--luna)} .seg-dorada{background:var(--dorada)} .seg-dia{background:var(--dia)}
.seg-extra{background:repeating-linear-gradient(135deg,var(--ink) 0 2px,transparent 2px 6px)}
.tl-eje{position:relative;height:24px;font:12px/1 var(--sans);color:var(--muted);font-variant-numeric:tabular-nums}
.tl-eje span{position:absolute;top:8px;transform:translateX(-50%)}
.tl-eje span::before{content:"";position:absolute;left:50%;top:-8px;width:1px;height:5px;background:var(--muted)}
.tl-eje .primero{transform:none}
.tl-eje .primero::before{left:0}
.tl-eje .ultimo{transform:none;left:auto;right:0}
.tl-eje .ultimo::before{left:auto;right:0}
.leyenda{display:flex;flex-wrap:wrap;gap:8px 18px;margin:8px 0 0;padding:0;list-style:none;font-size:13px;color:var(--muted)}
.leyenda i{display:inline-block;width:12px;height:12px;border-radius:2px;margin-right:6px;vertical-align:-1px}
details.tiempos{margin-top:16px}
summary{cursor:pointer;font:500 14px/1.4 var(--sans)}
.tabla{overflow-x:auto;margin-top:10px}
table{border-collapse:collapse;width:100%;font-size:14px;font-variant-numeric:tabular-nums}
th,td{text-align:left;padding:6px 12px 6px 0;border-bottom:1px solid var(--rule);white-space:nowrap}
th{font:600 11px/1.2 var(--sans);letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}

.prep{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1.4fr);gap:36px}
@media (max-width:820px){.prep{grid-template-columns:minmax(0,1fr);gap:8px}}
.flujo{margin:0;padding-left:1.4em;display:grid;gap:8px}
.ajustes{margin:0}
.ajustes div{display:grid;grid-template-columns:9em minmax(0,1fr);gap:14px;padding:9px 0;border-bottom:1px solid var(--rule)}
.ajustes dt{font-weight:600}
.ajustes dd{margin:0}
@media (max-width:520px){.ajustes div{grid-template-columns:minmax(0,1fr);gap:2px}}
.elements{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,330px),1fr));gap:16px}
.element{margin:0;display:grid;grid-template-columns:104px minmax(0,1fr);gap:14px;align-items:start;padding:14px;
  border:1px solid var(--rule);border-radius:6px;background:var(--surface)}
.element img{width:104px;height:120px;object-fit:cover;object-position:50% 20%;border-radius:4px;background:#000}
.element b{font:700 22px/1.1 var(--serif)}
.element p{margin:6px 0 0;font-size:14px}
.element .usa{color:var(--muted)}
.refs{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,190px),1fr));gap:18px 16px}
.ref{margin:0}
.ref img{width:100%;aspect-ratio:2000/1091;object-fit:cover;border-radius:4px;background:#000}
.ref figcaption{padding-top:8px;font-size:13px;line-height:1.45}
.ref b{display:block;font-size:14px}
.ref p{margin:4px 0 0}
.ref .usa{color:var(--muted)}

.cont{list-style:none;margin:0;padding:0}
.cont li{display:grid;grid-template-columns:6.5em minmax(0,1fr);gap:14px;padding:12px 0;border-bottom:1px solid var(--rule)}
.cont li p{margin:0;max-width:75ch}
.chip{justify-self:start;align-self:start;font:600 11px/1 var(--sans);letter-spacing:.1em;text-transform:uppercase;
  padding:5px 8px;border-radius:3px;border:1px solid currentColor}
.nivel-corrige .chip{color:var(--accent)}
.nivel-decide .chip{color:var(--dorada)}
.nivel-revisa .chip{color:var(--luna)}
.nivel-nota .chip{color:var(--muted)}
@media (max-width:520px){.cont li{grid-template-columns:minmax(0,1fr);gap:6px}}

.lista{display:grid;gap:16px}
.card{display:grid;grid-template-columns:minmax(0,5fr) minmax(0,7fr);gap:22px;padding:18px;border:1px solid var(--rule);
  border-radius:6px;background:var(--surface)}
@media (max-width:820px){.card{grid-template-columns:minmax(0,1fr);gap:16px}}
.card.hecho{border-color:var(--ok)}
.media,.cuerpo{display:grid;grid-template-columns:minmax(0,1fr);gap:12px;align-content:start;min-width:0}
.frame{margin:0;display:grid;grid-template-columns:minmax(0,1fr);gap:6px}
.frame img,.frame .falta{width:100%;aspect-ratio:2000/1091;border-radius:4px;object-fit:cover;background:#000}
.frame .falta{display:grid;place-content:center;justify-items:center;gap:4px;padding:12px;text-align:center;
  border:1.5px dashed var(--muted);background:var(--sunken);color:var(--muted);text-decoration:none}
.falta b{font:700 30px/1 var(--serif);color:var(--ink)}
.falta span{font-size:14px;color:var(--ink)}
.falta small{font-size:12px}
.frame figcaption{font-size:12px;color:var(--muted)}
.rol{font-weight:600;letter-spacing:.1em;text-transform:uppercase;margin-right:4px}
.alt{margin:0;font-size:13px;color:var(--muted)}
.base{display:flex;flex-wrap:wrap;gap:10px}
.base figure{margin:0;display:grid;gap:4px;font-size:12px;color:var(--muted)}
.base img{height:72px;width:auto;border-radius:3px;background:#000}
.base .kchip{display:grid;place-items:center;height:72px;min-width:72px;padding:0 14px;border:1.5px dashed var(--muted);border-radius:3px;
  font:700 20px/1 var(--serif);text-decoration:none;color:var(--ink)}
.cab{display:flex;align-items:baseline;flex-wrap:wrap;gap:6px 12px}
.sid{font:700 32px/1 var(--serif);color:var(--luz,var(--ink))}
.cab h3{margin:0;flex:1 1 11em;font:600 18px/1.3 var(--sans)}
.tag{font:600 11px/1 var(--sans);letter-spacing:.1em;text-transform:uppercase;padding:4px 7px;border:1px solid var(--rule);border-radius:3px;color:var(--muted)}
.listo{display:inline-flex;align-items:center;gap:7px;font:500 13px/1 var(--sans);color:var(--muted);cursor:pointer;user-select:none}
.listo input{width:18px;height:18px;margin:0;accent-color:var(--ok);cursor:pointer}
.hecho .listo{color:var(--ok)}
.accion{margin:0;font-size:15.5px}
.specs{display:flex;flex-wrap:wrap;gap:10px 26px;margin:0}
.specs div{display:grid;gap:2px;min-width:0}
.specs .ancho{flex-basis:100%}
.specs dt{font:600 11px/1.2 var(--sans);letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.specs dd{margin:0;font-size:14px;font-variant-numeric:tabular-nums}
.prompt{border:1px solid var(--rule);border-radius:4px;background:var(--bg);overflow:hidden}
.prompt-cab{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:6px 6px 6px 12px;border-bottom:1px solid var(--rule);
  font:600 11px/1 var(--sans);letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.prompt pre{margin:0;padding:12px 14px;font:15px/1.55 var(--mono);white-space:pre-wrap;overflow-wrap:anywhere;color:var(--ink)}
.copiar{min-width:7.5em;padding:8px 12px;border:1px solid var(--ink);border-radius:3px;background:var(--ink);color:var(--bg);
  font:600 12px/1 var(--sans);cursor:pointer}
.copiar:hover{background:transparent;color:var(--ink)}
.copiar.ok{background:var(--ok);border-color:var(--ok);color:var(--on-seg)}
.copiar.sel{background:transparent;color:var(--ink)}
details.mas{border-top:1px dashed var(--rule);padding-top:10px}
details.mas summary{color:var(--muted)}
details.mas[open] summary{margin-bottom:10px}
.pista{margin:0 0 8px;font-size:13px;color:var(--muted)}
.nota{margin:0;font-size:14px;color:var(--muted)}
.nota b{color:var(--ink)}

.escena{padding-block:64px 8px}
.luz-calida{--luz:var(--calida)} .luz-luna{--luz:var(--luna)} .luz-dorada{--luz:var(--dorada)} .luz-dia{--luz:var(--dia)}
.esc-cab{display:grid;grid-template-columns:auto minmax(0,1fr);gap:4px 22px;align-items:start;margin-bottom:20px}
.esc-num{font:700 clamp(64px,12vw,124px)/.78 var(--serif);color:var(--luz)}
.slug{margin:2px 0 6px;font:700 14px/1.4 var(--mono);letter-spacing:.02em;color:var(--muted)}
.esc-cab h2{margin:0 0 8px;font:700 clamp(26px,4.4vw,38px)/1.1 var(--serif);text-wrap:balance}
.resumen{margin:0;max-width:62ch}
.esc-notas{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:24px;margin:0 0 20px;padding-block:16px;
  border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)}
@media (max-width:720px){.esc-notas{grid-template-columns:minmax(0,1fr);gap:16px}}
.esc-notas h4{margin:0 0 6px;font:600 11px/1.2 var(--sans);letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.esc-notas p{margin:0;font-size:14px}
.paleta{list-style:none;margin:12px 0 0;padding:0;display:flex;flex-wrap:wrap;gap:8px 16px;font-size:12px;color:var(--muted)}
.paleta li{display:inline-flex;align-items:center;gap:6px}
.sw{width:16px;height:16px;border-radius:2px;box-shadow:inset 0 0 0 1px rgba(127,127,127,.4)}
.paleta code{font:12px/1 var(--mono);color:var(--ink)}

.pie{margin-top:72px;padding-top:18px;border-top:1px solid var(--rule);font-size:13px;color:var(--muted)}
.pie p{margin:0 0 6px;max-width:75ch}
@media (prefers-reduced-motion: reduce){html{scroll-behavior:auto}*{transition:none!important}}
"""

SCRIPT = """
(function () {
  function seleccionar(el) {
    try {
      var r = document.createRange(); r.selectNodeContents(el);
      var s = window.getSelection(); s.removeAllRanges(); s.addRange(r);
    } catch (e) {}
  }
  document.addEventListener('click', function (ev) {
    var b = ev.target.closest('button.copiar');
    if (!b) return;
    var el = document.getElementById(b.getAttribute('data-copiar'));
    if (!el) return;
    function volver() { b.textContent = 'Copiar'; b.classList.remove('ok', 'sel'); }
    function ok() { b.textContent = 'Copiado'; b.classList.add('ok'); setTimeout(volver, 1600); }
    function fallo() { seleccionar(el); b.textContent = 'Seleccionado'; b.classList.add('sel'); setTimeout(volver, 2400); }
    try { navigator.clipboard.writeText(el.textContent).then(ok, fallo); } catch (e) { fallo(); }
  });

  var CLAVE = 'la-incision:listo', estado = {};
  try { estado = JSON.parse(localStorage.getItem(CLAVE) || '{}') || {}; } catch (e) { estado = {}; }
  var casillas = Array.prototype.slice.call(document.querySelectorAll('input[data-listo]'));
  function pintar() {
    var p = 0, pt = 0, k = 0, kt = 0;
    casillas.forEach(function (c) {
      var card = c.closest('.card');
      if (card) card.classList.toggle('hecho', c.checked);
      if (c.getAttribute('data-tipo') === 'plano') { pt++; if (c.checked) p++; } else { kt++; if (c.checked) k++; }
    });
    var out = document.getElementById('avance');
    if (out) out.textContent = p + '/' + pt + ' planos · ' + k + '/' + kt + ' keyframes';
  }
  casillas.forEach(function (c) {
    c.checked = !!estado[c.getAttribute('data-listo')];
    c.addEventListener('change', function () {
      estado[c.getAttribute('data-listo')] = c.checked;
      try { localStorage.setItem(CLAVE, JSON.stringify(estado)); } catch (e) {}
      pintar();
    });
  });
  pintar();

  function ajustarEtiquetas() {
    document.querySelectorAll('.seg').forEach(function (s) {
      var l = s.querySelector('span');
      if (l) s.classList.toggle('estrecho', s.clientWidth < l.scrollWidth + 8);
    });
  }
  ajustarEtiquetas();
  window.addEventListener('resize', ajustarEtiquetas);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(ajustarEtiquetas);
})();
"""


def h(texto):
    return escape(str(texto), quote=True)


def bloque_html(ident, etiqueta, texto):
    return (f'<div class="prompt"><div class="prompt-cab"><span>{h(etiqueta)}</span>'
            f'<button type="button" class="copiar" data-copiar="{h(ident)}">Copiar</button></div>'
            f'<pre id="{h(ident)}">{h(texto)}</pre></div>')


def casilla(tipo, ident):
    return (f'<label class="listo"><input type="checkbox" id="listo-{h(ident)}" data-listo="{tipo}-{h(ident)}" '
            f'data-tipo="{tipo}"> Listo</label>')


def cuadro_html(indice, ident, rol):
    archivo = indice.archivo(ident)
    if archivo:
        media = f'<img src="{h(archivo)}" alt="{h(indice.etiqueta(ident))}" decoding="async">'
    elif ident in indice.kfs:
        media = (f'<a class="falta" href="#k-{h(ident)}"><b>{h(ident)}</b><span>{h(indice.kfs[ident]["titulo"])}</span>'
                 f'<small>Genera este keyframe primero</small></a>')
    else:
        media = (f'<div class="falta"><b>{h(ident.split("-")[0])}</b><span>{h(indice.etiqueta(ident))}</span>'
                 f'<small>Expórtalo del clip ya generado</small></div>')
    return f'<figure class="frame">{media}<figcaption><span class="rol">{h(rol)}</span>{h(indice.corta(ident))}</figcaption></figure>'


def linea_html(plan):
    filas, total = secuencia(plan)
    por_escena = {}
    for f in filas:
        por_escena[f["escena"]] = por_escena.get(f["escena"], 0) + f["uso"]
    escenas = "".join(f'<span style="flex:{seg} 1 0"><em>Esc. </em>{num}</span>' for num, seg in por_escena.items())
    segmentos = []
    for f in filas:
        texto = f"{f['id']} · {f['titulo']} · {f['uso']} s"
        if f["extra"]:
            segmentos.append(f'<span class="seg seg-extra" style="flex:{f["uso"]} 1 0" title="{h(texto)}"></span>')
        else:
            segmentos.append(f'<a class="seg seg-{f["luz"]}" href="#p-{h(f["id"])}" style="flex:{f["uso"]} 1 0" '
                             f'title="{h(texto)}" aria-label="{h(texto)}"><span>{h(f["id"])}</span></a>')
    marcas = list(range(0, total, 30))
    eje = []
    for i, t in enumerate(marcas):
        clase = ' class="primero"' if i == 0 else ""
        eje.append(f'<span{clase} style="left:{t / total * 100:.3f}%">{mmss(t)}</span>')
    eje.append(f'<span class="ultimo">{mmss(total)}</span>')
    leyenda = "".join(f'<li><i class="seg-{clave}"></i>{h(nombre)}</li>' for clave, nombre in LUCES.items())
    leyenda += '<li><i class="seg-extra"></i>Negro y título</li>'
    tabla = "".join(
        f'<tr><td>{mmss(f["entra"])}</td><td>{mmss(f["entra"] + f["uso"])}</td><td>{f["uso"]} s</td>'
        f'<td>{h(f["id"])}</td><td>{h(f["titulo"])}</td></tr>' for f in filas)
    return (f'<div class="tl"><div class="tl-escenas" aria-hidden="true">{escenas}</div>'
            f'<div class="tl-barra">{"".join(segmentos)}</div><div class="tl-eje" aria-hidden="true">{"".join(eje)}</div></div>'
            f'<ul class="leyenda">{leyenda}</ul>'
            f'<details class="tiempos"><summary>Tiempos de entrada y salida de cada plano</summary><div class="tabla"><table>'
            f'<thead><tr><th>Entra</th><th>Sale</th><th>Dura</th><th>Plano</th><th>Qué es</th></tr></thead>'
            f'<tbody>{tabla}</tbody></table></div></details>')


def plano_html(plan, indice, p):
    pid = p["id"]
    cuadros = cuadro_html(indice, p["inicio"], "Inicio")
    if p.get("fin"):
        cuadros += cuadro_html(indice, p["fin"], "Fin")
    if p.get("inicio_alt"):
        alt = p["inicio_alt"]
        destino = f"#k-{h(alt)}" if alt in indice.kfs else "#referencias"
        cuadros += f'<p class="alt">Otro inicio posible: <a href="{destino}">{h(indice.etiqueta(alt))}</a></p>'
    opcional = '<span class="tag">Opcional</span>' if p.get("opcional") else ""
    specs = (f'<div><dt>Genera</dt><dd>{p["genera"]} s</dd></div><div><dt>Usa</dt><dd>{p["uso"]} s</dd></div>'
             f'<div><dt>Elements</dt><dd>{h(", ".join(p["elements"]) or "—")}</dd></div>'
             f'<div class="ancho"><dt>Cámara</dt><dd>{h(p["camara"])}</dd></div>')
    partes = [f'<p class="accion">{h(p["accion"])}</p>', f'<dl class="specs">{specs}</dl>',
              bloque_html(f"pr-{pid}", "Prompt", p["prompt"]),
              f'<details class="mas"><summary>Negative prompt</summary>'
              f'{bloque_html(f"ng-{pid}", "Negative prompt", plan["negativos"][p["negativo"]])}</details>']
    if p.get("audio"):
        partes.append(f'<details class="mas"><summary>Audio nativo (opcional)</summary>'
                      f'<p class="pista">Pégalo al final del prompt solo si activas el audio de Kling.</p>'
                      f'{bloque_html(f"au-{pid}", "Audio nativo", p["audio"])}</details>')
    if p.get("notas"):
        partes.append(f'<p class="nota"><b>Nota.</b> {h(p["notas"])}</p>')
    return (f'<article class="card" id="p-{h(pid)}"><div class="media">{cuadros}</div><div class="cuerpo">'
            f'<div class="cab"><span class="sid">{h(pid)}</span><h3>{h(p["titulo"])}</h3>{opcional}{casilla("plano", pid)}</div>'
            f'{"".join(partes)}</div></article>')


def keyframe_html(indice, k):
    kid = k["id"]
    base = []
    for b in k["base"]:
        archivo = indice.archivo(b)
        if archivo:
            base.append(f'<figure><img src="{h(archivo)}" alt="{h(indice.etiqueta(b))}" decoding="async">'
                        f'<figcaption>{h(indice.etiqueta(b))}</figcaption></figure>')
        else:
            base.append(f'<figure><a class="kchip" href="#k-{h(b)}">{h(b)}</a><figcaption>{h(indice.kfs[b]["titulo"])}</figcaption></figure>')
    opcional = '<span class="tag">Opcional</span>' if k.get("opcional") else ""
    nota = f'<p class="nota"><b>Nota.</b> {h(k["notas"])}</p>' if k.get("notas") else ""
    return (f'<article class="card" id="k-{h(kid)}"><div class="media">'
            f'<div class="cab"><span class="sid">{h(kid)}</span><h3>{h(k["titulo"])}</h3>{opcional}{casilla("keyframe", kid)}</div>'
            f'<div class="base">{"".join(base)}</div>'
            f'<dl class="specs"><div class="ancho"><dt>Se usa en</dt><dd>{h(k["usa_en"])}</dd></div>'
            f'<div class="ancho"><dt>Cómo</dt><dd>{h(k["como"])}</dd></div></dl></div>'
            f'<div class="cuerpo">{bloque_html(f"kp-{kid}", "Prompt de imagen", k["prompt"])}{nota}</div></article>')


def escena_html(plan, indice, esc):
    paleta = "".join(f'<li><span class="sw" style="background:{h(hexa)}"></span>{h(nombre)} <code>{h(hexa)}</code></li>'
                     for nombre, hexa in esc["paleta"])
    planos = "".join(plano_html(plan, indice, p) for p in esc["planos"])
    return (f'<section class="escena luz-{esc["luz"]}" id="esc-{esc["num"]}">'
            f'<div class="esc-cab"><div class="esc-num">{esc["num"]}</div><div>'
            f'<p class="slug">{h(esc["slug"])}</p><h2>{h(esc["titulo"])}</h2><p class="resumen">{h(esc["resumen"])}</p></div></div>'
            f'<div class="esc-notas"><div><h4>Luz · {h(LUCES[esc["luz"]])}</h4><p>{h(esc["color"])}</p><ul class="paleta">{paleta}</ul></div>'
            f'<div><h4>Sonido</h4><p>{h(esc["sonido"])}</p></div></div>'
            f'<div class="lista">{planos}</div></section>')


def contenido_html(plan):
    indice = Indice(plan)
    planos = todos_los_planos(plan)
    _, total = secuencia(plan)
    nav = ['<a href="#montaje">Montaje</a>', '<a href="#preparacion">Preparación</a>',
           '<a href="#continuidad">Continuidad</a>', '<a href="#keyframes">Keyframes</a>']
    nav += [f'<a class="luz-{e["luz"]}" href="#esc-{e["num"]}"><i></i>Esc. {e["num"]}</a>' for e in plan["escenas"]]
    flujo = "".join(f"<li>{h(paso)}</li>" for paso in plan["flujo"])
    ajustes = "".join(f"<div><dt>{h(k)}</dt><dd>{h(v)}</dd></div>" for k, v in plan["ajustes"])
    elements = "".join(
        f'<figure class="element"><img src="{h(e["imagen"])}" alt="Element {h(e["id"])}" decoding="async">'
        f'<figcaption><b>{h(e["id"])}</b><p>{h(e["fuente"])}</p><p class="usa">Úsalo en {h(e["usar_en"])}</p></figcaption></figure>'
        for e in plan["elements"])
    refs = "".join(
        f'<figure class="ref"><img src="{h(r["archivo"])}" alt="{h(r["titulo"])}" decoding="async">'
        f'<figcaption><b>{h(r["id"][3:])} · {h(r["titulo"])}</b><p>{h(r["descripcion"])}</p><p class="usa">{h(r["usa_en"])}</p></figcaption></figure>'
        for r in plan["referencias"])
    continuidad = "".join(
        f'<li class="nivel-{h(c["nivel"].lower())}"><span class="chip">{h(c["nivel"])}</span>'
        f'<p><b>{h(c["titulo"])}.</b> {h(c["detalle"])}</p></li>' for c in plan["continuidad"])
    keyframes = "".join(keyframe_html(indice, k) for k in plan["keyframes"])
    escenas = "".join(escena_html(plan, indice, esc) for esc in plan["escenas"])
    return f"""<div class="page" lang="es">
<header>
<p class="eyebrow">Plan de producción para Kling AI</p>
<h1 class="title">{h(plan["titulo"])}</h1>
<p class="logline">{h(plan["logline"])}</p>
<dl class="meta">
<div><dt>Planos</dt><dd>{len(planos)}</dd></div>
<div><dt>Keyframes</dt><dd>{len(plan["keyframes"])}</dd></div>
<div><dt>Montaje</dt><dd>{mmss(total)}</dd></div>
<div><dt>Generación</dt><dd>{sum(p["genera"] for p in planos)} s por pasada</dd></div>
<div><dt>Formato</dt><dd>16:9</dd></div>
<div><dt>Avance</dt><dd id="avance">0/{len(planos)} planos · 0/{len(plan["keyframes"])} keyframes</dd></div>
</dl>
</header>
<nav class="jump" aria-label="Secciones">{"".join(nav)}</nav>
<main>
<section class="block" id="montaje">
<h2 class="sec">Montaje</h2>
<p class="lede">Cada bloque es un plano, a escala de lo que dura en el corte final y con el color de su luz. Toca uno para ir a su prompt.</p>
{linea_html(plan)}
</section>
<section class="block" id="preparacion">
<h2 class="sec">Preparación</h2>
<div class="prep">
<div><h3 class="sub">Flujo</h3><ol class="flujo">{flujo}</ol></div>
<div><h3 class="sub">Ajustes en Kling</h3><dl class="ajustes">{ajustes}</dl></div>
</div>
<h3 class="sub">Elements</h3>
<div class="elements">{elements}</div>
<h3 class="sub" id="referencias">Tus referencias</h3>
<div class="refs">{refs}</div>
</section>
<section class="block" id="continuidad">
<h2 class="sec">Continuidad</h2>
<p class="lede">Lo que no cuadra entre tus referencias y el guion, y cómo resolverlo antes de gastar créditos.</p>
<ul class="cont">{continuidad}</ul>
</section>
<section class="block" id="keyframes">
<h2 class="sec">Keyframes</h2>
<p class="lede">Las imágenes que faltan para animar los planos. Genéralas antes que los videos, en 16:9. «The first/second reference image» son las imágenes que subes, en ese orden.</p>
<div class="lista">{keyframes}</div>
</section>
{escenas}
</main>
<footer class="pie">
<p>Generado desde plan.json con herramientas/generar.py. En el repositorio también están el guion, la biblia visual y la guía de postproducción.</p>
<p><a href="{h(plan["repo"])}">{h(plan["repo"])}</a></p>
</footer>
</div>"""


def pagina(plan, completa):
    cabeza = f"<title>{TITULO_PAGINA}</title>\n{FUENTES}\n<style>{ESTILOS}</style>"
    cuerpo = f"{contenido_html(plan)}\n<script>{SCRIPT}</script>"
    if not completa:
        return f"{cabeza}\n{cuerpo}\n"
    return (f'<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
            f'<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            f"{cabeza}\n</head>\n<body>\n{cuerpo}\n</body>\n</html>\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--artefacto", type=Path, help="escribe también la versión sin <head> en esta ruta")
    args = parser.parse_args()
    plan = cargar()
    indice = Indice(plan)
    (RAIZ / "shotlist-kling.md").write_text(shotlist_md(plan, indice), encoding="utf-8")
    (RAIZ / "keyframes.md").write_text(keyframes_md(plan, indice), encoding="utf-8")
    (RAIZ / "storyboard.html").write_text(pagina(plan, completa=True), encoding="utf-8")
    if args.artefacto:
        args.artefacto.write_text(pagina(plan, completa=False), encoding="utf-8")
    print("Listo: shotlist-kling.md, keyframes.md y storyboard.html")


if __name__ == "__main__":
    main()
