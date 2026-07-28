#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Inyecta un .pine en el editor Monaco VISIBLE de TradingView Desktop via CDP.

Diferencias con pine_inject.py (que se queda; este NO lo sustituye hasta validarlo):
  1. Elige el editor por getDomNode().offsetParent !== null, NO por getEditors()[0].
     [S145/S146] Con dos scripts abiertos hay DOS editores en el mismo monacoEnv y el
     indice 0 puede ser el OCULTO -> en S145 se sobrescribio el Visual con el Context
     dos veces. Verificado de nuevo en S146: [0] = plantilla oculta, [1] = Visual visible.
  2. Escribe con executeEdits (marca el buffer DIRTY). setValue NO lo marca => Ctrl+S
     se queda en no-op y el "guardado" es mentira.
  3. Imprime una HUELLA del buffer antes y despues (longitud + cabecera) para que el
     destino real sea auditable, no una suposicion.

Uso: python pine_inject_v2.py <archivo.pine> [--no-click]
"""
import sys, json, asyncio, urllib.request
import websockets

PATH = sys.argv[1]
NO_CLICK = "--no-click" in sys.argv
with open(PATH, "r", encoding="utf-8") as f:
    SOURCE = f.read()

# Localiza el monacoEnv desde el contenedor VISIBLE y devuelve el editor cuyo DOM esta visible.
FIND_BODY = """
var conts=document.querySelectorAll('.monaco-editor.pine-editor-monaco');
var vis=null;
for(var i=0;i<conts.length;i++){if(conts[i].offsetParent!==null){vis=conts[i];break}}
if(!vis)return null;
var el=vis,fk;
for(var i=0;i<20;i++){if(!el)break;fk=Object.keys(el).find(function(k){return k.startsWith('__reactFiber$')});if(fk)break;el=el.parentElement}
if(!fk)return null;
var cur=el[fk];
for(var d=0;d<15;d++){
  if(!cur)break;
  if(cur.memoizedProps&&cur.memoizedProps.value&&cur.memoizedProps.value.monacoEnv){
    var env=cur.memoizedProps.value.monacoEnv;
    if(env.editor&&typeof env.editor.getEditors==='function'){
      var eds=env.editor.getEditors();
      for(var j=0;j<eds.length;j++){
        var dn=eds[j].getDomNode();
        if(dn&&dn.offsetParent!==null)return{editor:eds[j],env:env,idx:j,total:eds.length};
      }
    }
  }
  cur=cur.return;
}
return null;
"""
FIND = "(function(){" + FIND_BODY + "})()"

HUELLA = ("(function(){var m=" + FIND + ";if(!m)return 'NO_EDITOR';var v=m.editor.getValue();"
          "return JSON.stringify({idx:m.idx,total:m.total,len:v.length,head:v.slice(0,70)})})()")

# executeEdits sobre el rango COMPLETO -> el modelo queda dirty (a diferencia de setValue).
INJECT = ("(function(){var m=" + FIND + ";if(!m)return 'NO_EDITOR';var mo=m.editor.getModel();"
          "if(!mo)return 'NO_MODEL';var full=mo.getFullModelRange();"
          "m.editor.executeEdits('probe',[{range:full,text:" + json.dumps(SOURCE) + ",forceMoveMarkers:true}]);"
          "m.editor.pushUndoStop();return 'OK'})()")

CLICK = """(function(){var btns=document.querySelectorAll('button');
for(var i=0;i<btns.length;i++){var t=btns[i].textContent.trim();
if(/^(A.adir al gr.fico|Actualizar en el gr.fico|Add to chart|Update on chart)$/i.test(t)&&btns[i].offsetParent!==null){btns[i].click();return t}}
return null})()"""

MARKERS = ("(function(){var m=" + FIND + ";if(!m)return 'NO_EDITOR';var mo=m.editor.getModel();"
           "if(!mo)return 'NO_MODEL';var mk=m.env.editor.getModelMarkers({resource:mo.uri});"
           "return JSON.stringify(mk.map(function(x){return{line:x.startLineNumber,sev:x.severity,msg:x.message}}))})()")


async def main():
    targets = json.loads(urllib.request.urlopen("http://localhost:9222/json/list").read())
    t = next((x for x in targets if "tradingview.com" in (x.get("url") or "")), None)
    if not t:
        print("NO_TV_TARGET"); return
    _id = [0]
    async with websockets.connect(t["webSocketDebuggerUrl"], max_size=None) as ws:
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

        print("ANTES :", await ev(HUELLA))
        print("INJECT:", await ev(INJECT))
        print("DESPUES:", await ev(HUELLA))
        if not NO_CLICK:
            print("CLICK :", await ev(CLICK))
            await asyncio.sleep(5.0)
            print("MARKERS:", await ev(MARKERS))

asyncio.run(main())
