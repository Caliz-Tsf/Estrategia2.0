#!/usr/bin/env python
# Compila un archivo Pine via el endpoint server-side de TradingView (pine-facade
# translate_light), el MISMO que usa el MCP (pine_check). Lee el archivo desde DISCO
# (no pasa por el contexto del LLM). Imprime error_count / warning_count + mensajes.
# Uso: python pine_check.py <archivo.pine>
import sys, json, urllib.request, urllib.parse

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as f:
    source = f.read()

data = urllib.parse.urlencode({"source": source}).encode("utf-8")
url = ("https://pine-facade.tradingview.com/pine-facade/translate_light"
       "?user_name=Guest&pine_id=00000000-0000-0000-0000-000000000000")
req = urllib.request.Request(url, data=data, headers={
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://www.tradingview.com/",
})
with urllib.request.urlopen(req, timeout=60) as resp:
    result = json.loads(resp.read().decode("utf-8"))

inner = result.get("result") or {}
errors = inner.get("errors2") or []
warnings = inner.get("warnings2") or []
if result.get("error"):
    errors = errors + [{"message": result["error"]}]

print(f"FILE: {path}")
print(f"ERRORS: {len(errors)} | WARNINGS: {len(warnings)}")
for e in errors:
    s = e.get("start") or {}
    print(f"  [E] L{s.get('line','?')}:{s.get('column','?')} {e.get('message','')}")
for w in warnings:
    s = w.get("start") or {}
    print(f"  [W] L{s.get('line','?')}:{s.get('column','?')} {w.get('message','')}")
print("RESULT:", "CLEAN_0_0" if (not errors and not warnings) else "HAS_ISSUES")
