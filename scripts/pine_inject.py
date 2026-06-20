#!/usr/bin/env python
# Inyecta un archivo Pine en el editor Monaco de TradingView Desktop via CDP y lo aplica
# al chart (Update/Add to chart), luego lee los markers de error. Replica el mecanismo del
# MCP (src/core/pine.js: FIND_MONACO via .pine-editor-monaco + React fiber). Lee el archivo
# desde DISCO (no pasa por el contexto del LLM).
# Uso: python pine_inject.py <archivo.pine>
import sys, json, asyncio, urllib.request
import websockets

PATH = sys.argv[1]
with open(PATH, "r", encoding="utf-8") as f:
    SOURCE = f.read()

FIND = """(function findMonacoEditor(){var container=document.querySelector('.monaco-editor.pine-editor-monaco');if(!container)return null;var el=container;var fiberKey;for(var i=0;i<20;i++){if(!el)break;fiberKey=Object.keys(el).find(function(k){return k.startsWith('__reactFiber$')});if(fiberKey)break;el=el.parentElement}if(!fiberKey)return null;var current=el[fiberKey];for(var d=0;d<15;d++){if(!current)break;if(current.memoizedProps&&current.memoizedProps.value&&current.memoizedProps.value.monacoEnv){var env=current.memoizedProps.value.monacoEnv;if(env.editor&&typeof env.editor.getEditors==='function'){var editors=env.editor.getEditors();if(editors.length>0)return{editor:editors[0],env:env}}}current=current.return}return null})()"""

OPEN_EDITOR = """(function(){var btn=document.querySelector('[aria-label="Pine"]')||document.querySelector('[data-name="pine-dialog-button"]');if(btn){btn.click();return 'clicked'}var bwb=window.TradingView&&window.TradingView.bottomWidgetBar;if(bwb&&typeof bwb.activateScriptEditorTab==='function'){bwb.activateScriptEditorTab();return 'bwb'}return 'none'})()"""

SETVALUE = "(function(){var m=" + FIND + ";if(!m)return false;m.editor.setValue(" + json.dumps(SOURCE) + ");return true})()"

CLICK = """(function(){var btns=document.querySelectorAll('button');for(var i=0;i<btns.length;i++){var t=btns[i].textContent.trim();if(/save and add to chart/i.test(t)){btns[i].click();return 'Save and add to chart'}}for(var i=0;i<btns.length;i++){var t=btns[i].textContent.trim();if(/^(Add to chart|Update on chart)$/i.test(t)){btns[i].click();return t}}for(var i=0;i<btns.length;i++){if(btns[i].className.indexOf('saveButton')!==-1&&btns[i].offsetParent!==null){btns[i].click();return 'Pine Save'}}return null})()"""

MARKERS = "(function(){var m=" + FIND + ";if(!m)return 'NO_EDITOR';var model=m.editor.getModel();if(!model)return 'NO_MODEL';var mk=m.env.editor.getModelMarkers({resource:model.uri});return JSON.stringify(mk.map(function(x){return{line:x.startLineNumber,sev:x.severity,msg:x.message}}))})()"

async def main():
    targets = json.loads(urllib.request.urlopen("http://localhost:9222/json/list").read())
    t = next((x for x in targets if "tradingview.com" in (x.get("url") or "")), None)
    if not t:
        print("NO_TV_TARGET"); return
    ws_url = t["webSocketDebuggerUrl"]
    _id = [0]
    async with websockets.connect(ws_url, max_size=None) as ws:
        await ws.send(json.dumps({"id": 1, "method": "Runtime.enable"}))
        async def ev(expr):
            _id[0] += 1
            mid = 100 + _id[0]
            await ws.send(json.dumps({"id": mid, "method": "Runtime.evaluate",
                "params": {"expression": expr, "returnByValue": True, "awaitPromise": True}}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == mid:
                    if "error" in msg:
                        return "CDP_ERR " + json.dumps(msg["error"])
                    return msg["result"]["result"].get("value")
        # ensure editor open
        m = await ev("(function(){return " + FIND + "!==null})()")
        if not m:
            await ev(OPEN_EDITOR)
            for _ in range(40):
                await asyncio.sleep(0.25)
                if await ev("(function(){return " + FIND + "!==null})()"):
                    break
        ok = await ev(SETVALUE)
        print("SETVALUE:", ok)
        if ok is not True:
            print("INJECT_FAILED"); return
        clicked = await ev(CLICK)
        print("CLICK:", clicked)
        await asyncio.sleep(4.0)
        mk = await ev(MARKERS)
        print("MARKERS:", mk)

asyncio.run(main())
