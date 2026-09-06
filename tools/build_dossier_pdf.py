#!/usr/bin/env python3
"""
build_dossier_pdf.py — Impagina il dossier di consultazione in un PDF brandizzato.

Unisce dossier + capitolo coesistenza + allegato accessi civici, converte Markdown
in HTML, applica il template del brand e stampa in PDF via Chrome headless.

Output: docs/consultazione/Dossier-Terzo-Scalo-Lazio.pdf
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
CONS = ROOT / "docs" / "consultazione"
OUT_HTML = CONS / "_dossier_print.html"
OUT_PDF = CONS / "Dossier-Terzo-Scalo-Lazio.pdf"

CHROME = [r"C:\Program Files\Google\Chrome\Application\chrome.exe",
          r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"]

BLU = "#0b3d67"
GOLD = "#f0b429"

CSS = """
@page{size:A4;margin:20mm 17mm}
*{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{font-family:'Segoe UI','Helvetica Neue',Arial,sans-serif;color:#1a2230;font-size:10.5pt;line-height:1.5;margin:0}
a{color:#12557f;text-decoration:none;word-break:break-word}
h1{color:#0b3d67;font-size:18pt;margin:0 0 .4em;padding-bottom:.2em;border-bottom:2px solid #f0b429;page-break-after:avoid}
h2{color:#0b3d67;font-size:14pt;margin:1.1em 0 .3em;page-break-after:avoid}
h3{color:#12557f;font-size:11.5pt;margin:.9em 0 .3em;page-break-after:avoid}
p{margin:.4em 0}
table{border-collapse:collapse;width:100%;margin:.7em 0;font-size:9pt}
th,td{border:1px solid #cdd8e2;padding:5px 7px;text-align:left;vertical-align:top}
th{background:#0b3d67;color:#fff;font-weight:600}
tr:nth-child(even) td{background:#f4f7fa}
blockquote{background:#eef4f9;border-left:4px solid #12557f;margin:.7em 0;padding:.5em .9em;color:#22303c}
code{background:#eef2f6;padding:1px 4px;border-radius:3px;font-size:9pt}
hr{border:0;border-top:1px solid #dfe6ee;margin:1.2em 0}
ul,ol{margin:.4em 0 .4em 1.1em;padding:0}
li{margin:.2em 0}
.pagebreak{page-break-before:always}
.cover{page-break-after:always;height:247mm;display:flex;flex-direction:column;
justify-content:center;background:#0b3d67;color:#fff;text-align:center;padding:0 22mm;margin:-20mm -17mm 0}
.cover .logo{margin:0 auto 26px}
.cover .kick{color:#f0b429;font-weight:600;letter-spacing:2px;text-transform:uppercase;font-size:11pt;margin-bottom:14px}
.cover h1{color:#fff;border:0;font-size:25pt;line-height:1.2;margin:0 0 16px}
.cover .sub{font-size:12.5pt;color:#cfe0ee;margin:0 auto;max-width:150mm;line-height:1.5}
.cover .meta{margin-top:34px;font-size:10.5pt;color:#aecbe4}
.cover .org{margin-top:8px;font-weight:600;color:#fff;font-size:12pt}
"""

LOGO = (f'<svg class="logo" width="96" height="96" viewBox="0 0 120 120">'
        f'<rect width="120" height="120" rx="24" fill="#12557f"/>'
        f'<rect x="30" y="30" width="14" height="52" fill="#f4f6f8"/>'
        f'<rect x="30" y="68" width="44" height="14" fill="#f4f6f8"/>'
        f'<line x1="37" y1="75" x2="70" y2="75" stroke="#12557f" stroke-width="2.4" stroke-dasharray="5 4"/>'
        f'<path d="M72 65 L97 49 L81 63 Z" fill="{GOLD}"/><path d="M81 63 L84 70 L89 62 Z" fill="#e0a300"/></svg>')

COVER = (f'<div class="cover">{LOGO}'
         f'<div class="kick">Osservazione alla consultazione pubblica</div>'
         f'<h1>Il terzo aeroporto del Lazio</h1>'
         f'<div class="sub">Dossier conoscitivo e osservazione alla Valutazione Ambientale '
         f'Strategica (VAS n. 8657) del Piano Nazionale degli Aeroporti 2026-2035</div>'
         f'<div class="meta">Documento presentato nell\'ambito della consultazione pubblica MASE-ENAC '
         f'(4 agosto – 18 settembre 2026)</div>'
         f'<div class="org">Comitato per l\'Aeroporto di Latina</div>'
         f'<div class="meta">iniziativa civica e non partitica · aeroportolatina.it</div></div>')

EXT = ["tables", "toc", "fenced_code", "attr_list", "sane_lists"]


def render(name: str, strip_first_h1: bool = False) -> str:
    p = CONS / name
    if not p.exists():
        return ""
    text = p.read_text(encoding="utf-8")
    return markdown.markdown(text, extensions=EXT)


def main():
    chrome = next((c for c in CHROME if Path(c).exists()), None)
    if not chrome:
        sys.exit("Chrome non trovato")

    body = render("dossier-terzo-scalo-lazio.md")
    coex = render("cap-coesistenza-civile-militare.md")
    acc = render("accessi-civici-da-fare.md")
    parts = [COVER, body]
    if coex:
        parts.append('<div class="pagebreak"></div>' + coex)
    if acc:
        parts.append('<div class="pagebreak"></div><h1>Allegato — Documentazione da reperire (accessi civici)</h1>' + acc)
    html = (f'<!doctype html><html lang="it"><head><meta charset="utf-8">'
            f'<style>{CSS}</style></head><body>{"".join(parts)}</body></html>')
    OUT_HTML.write_text(html, encoding="utf-8")

    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                    "--run-all-compositor-stages-before-draw", "--virtual-time-budget=20000",
                    f"--print-to-pdf={OUT_PDF}", str(OUT_HTML)], timeout=120, capture_output=True)
    if OUT_PDF.exists():
        kb = OUT_PDF.stat().st_size // 1024
        print(f"PDF generato: {OUT_PDF} ({kb} KB)")
    else:
        print("ERRORE: PDF non generato")


if __name__ == "__main__":
    main()
