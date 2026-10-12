#!/usr/bin/env python3
"""Junta todos los semana-*.json en un único index.html autónomo (funciona sin servidor, en el móvil)."""
import json, glob, os
here = os.path.dirname(os.path.abspath(__file__))
quizzes = [json.load(open(f, encoding="utf-8")) for f in sorted(glob.glob(os.path.join(here, "semana-*.json")))]
for q in quizzes:
    for i, p in enumerate(q["preguntas"]):
        assert 0 <= p["correcta"] < len(p["opciones"]), f'{q["id"]} #{i+1}: índice "correcta" inválido'
html = open(os.path.join(here, "plantilla.html"), encoding="utf-8").read()
data = json.dumps(quizzes, ensure_ascii=False).replace("</", "<\\/")
open(os.path.join(here, "index.html"), "w", encoding="utf-8").write(html.replace("/*DATA*/", data))
print(f"index.html generado con {len(quizzes)} cuestionario(s)")
