#!/usr/bin/env python
# Helper CDP minimo: evalua una expresion JS en un target de pagina (TradingView Desktop).
# Uso: python cdp_eval.py <ws_url> <archivo_js>   (lee la expresion JS desde archivo, UTF-8)
#   o: python cdp_eval.py <ws_url> --expr "<js>"
# Imprime el resultado JSON de Runtime.evaluate (returnByValue). No carga nada en el contexto del LLM.
import sys, json, asyncio
import websockets

async def main():
    ws_url = sys.argv[1]
    if sys.argv[2] == "--expr":
        expr = sys.argv[3]
    else:
        with open(sys.argv[2], "r", encoding="utf-8") as f:
            expr = f.read()
    async with websockets.connect(ws_url, max_size=None) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
        await ws.send(json.dumps({
            "id": 2, "method": "Runtime.evaluate",
            "params": {"expression": expr, "returnByValue": True, "awaitPromise": True, "allowUnsafeEvalBlocklistedCalls": True}
        }))
        while True:
            msg = json.loads(await ws.recv())
            if msg.get("id") == 2:
                if "error" in msg:
                    print("CDP_ERROR", json.dumps(msg["error"]))
                else:
                    r = msg["result"].get("result", {})
                    print(r.get("value", json.dumps(r)))
                return

asyncio.run(main())
