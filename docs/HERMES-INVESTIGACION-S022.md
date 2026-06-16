# Investigación Hermes — Velocidad y Configuración Local
> Sesión S022 — pendiente de resolver

---

## Resumen de lo hecho en S021 (sesión actual)

### Problema inicial
El swap de modelos locales quedó incompleto en la sesión anterior. 4 bugs pendientes:
1. Workspace mostraba modelo viejo (gateway en caché)
2. Terminal daba "Response truncated after 3 attempts"
3. Selector de modelo no reiniciaba el gateway
4. Falta comparación local vs cloud

### Lo que hicimos y cómo

**Fix 1 — Gateway no recarga config al cambiar modelo** (`start-hermes.ps1`)
- Agregamos `$modelChanged` para detectar si el modelo cambió antes de escribir config.yaml
- Si cambió y el gateway corría → `Stop-Process -Id $gPid -Force` + reinicio automático
- Resultado: ✅ funciona — el gateway ahora se reinicia cuando el usuario cambia modelo

**Fix 2 — max_tokens muy bajo** (`config.yaml`)
- Subimos `max_tokens: 4096` → `max_tokens: 16384`
- Resultado: ✅ aplicado, pero no era el problema real

**Diagnóstico real del error "Response truncated"**
- Ollama cargaba gemma4:12b con `n_ctx = 4096` (default del sistema)
- Hermes pedía 16384 tokens → crash HTTP 500 porque el modelo no tenía esa ventana
- Adicionalmente: gemma4:12b y qwen3.6:35b-a3b son **thinking models** que generan cadenas de razonamiento largas (`<think>...</think>`) que consumen todos los tokens antes de responder
- Intentos fallidos:
  - `extra_body: options: think: false` → Hermes no pasa esto al endpoint /v1 de Ollama
  - `extra_body: think: false` → Timeout en `/v1/chat/completions`
  - `PARAMETER think false` en Modelfile → Rechazado por Ollama 0.30.8 ("unknown parameter")

**Fix final — Modelfiles con num_ctx 65536**
- Hermes requiere mínimo 64,000 tokens para tool use de agentes
- Creamos alias `gemma4-chat` y `qwen3-chat` con `PARAMETER num_ctx 65536`
- Agregamos a config.yaml: `ollama_num_ctx: 65536` y `context_length: 65536`
- Resultado: ✅ Hermes Agent responde con gemma4-chat sin error de truncado
- Problema nuevo: latencia de ~3 minutos por respuesta

---

## Investigación para S022

### Pregunta central
¿Por qué gemma4-chat tarda ~3 minutos en responder una pregunta simple, y se puede mejorar?

---

### Hipótesis 1 — El modelo corre en CPU, no en GPU (más probable)
Con `num_ctx = 65536`, el KV cache de gemma4:12b ocupa ~4-8 GB de VRAM.
Si la GPU no tiene suficiente VRAM libre, Ollama hace "offload" parcial o total a CPU RAM → lentitud extrema.

**Investigar:**
```powershell
# Ver si Ollama usa GPU y cuántas capas está offloadeando
ollama ps
# Ver VRAM disponible mientras corre gemma4-chat
nvidia-smi
# Ver en el log de Ollama cuántas capas van a GPU vs CPU
Get-Content "$env:LOCALAPPDATA\Ollama\server.log" -Tail 50 | Select-String "gpu|layers|offload|cuda" -CaseSensitive:$false
```

**Si el problema es VRAM insuficiente para 65536 ctx:**
- Probar `num_ctx 32768` (mitad del KV cache)
- Probar `num_ctx 16384` (mínimo para funcionamiento básico con Hermes, sin tool use completo)
- Ver si hay un balance entre velocidad y capacidad de tool use

---

### Hipótesis 2 — El thinking chain sigue consumiendo todos los tokens
Aunque ahora tiene 65536 tokens de espacio, el modelo puede estar generando miles de tokens de razonamiento interno antes de responder, lo que se traduce en minutos de CPU/GPU.

**Investigar:**
```powershell
# Probar con /no_think prefix en qwen3 (truco oficial de Qwen para desactivar thinking)
$body = @{
    model = "qwen3-chat"
    messages = @(@{ role = "user"; content = "/no_think hola" })
    stream = $false
} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:11434/api/chat" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 120

# Ver tokens generados y tiempo real
# Si eval_count es muy alto (>2000) y tardó mucho → es thinking
# Si eval_count es bajo (<200) y tardó mucho → es otro problema
```

**Para gemma4:12b** — verificar si genera thinking:
```powershell
# Llamar con stream=true y ver si hay <think> en la respuesta
```

---

### Hipótesis 3 — ¿Había una forma mejor de instalarlo sin crear alias?
La ruta que tomamos (crear modelos alias con Modelfile) fue necesaria porque:
1. Ollama carga modelos con `n_ctx = 4096` por default
2. Hermes no tiene una forma documentada de pasar `num_ctx` per-request vía config.yaml

**Investigar si existía opción más simple:**
```powershell
# Opción A: Variable de entorno OLLAMA_NUM_CTX (global para todos los modelos)
$env:OLLAMA_NUM_CTX = "65536"
# ¿Se puede agregar esta var al startup de Ollama en Windows?

# Opción B: Parámetro directo en Hermes config (no documentado)
# ¿Existe model.ollama_options.num_ctx en hermes?
# Ver si hay documentación oficial en hermes-agent 0.15.2

# Opción C: Usar los modelos originales (gemma4:12b) si OLLAMA_NUM_CTX se setea antes de iniciar Ollama
```

Si `OLLAMA_NUM_CTX=65536` funciona como env var global, podemos:
- Eliminar los alias `gemma4-chat` y `qwen3-chat`
- Usar directamente `gemma4:12b` y `qwen3.6:35b-a3b` en config.yaml
- Agregar `$env:OLLAMA_NUM_CTX = "65536"` en `start-hermes.ps1` antes de iniciar Ollama

---

### Hipótesis 4 — El modelo no es óptimo para uso en agentes
gemma4:12b y qwen3.6:35b-a3b son **modelos de razonamiento** (thinking models) diseñados para tareas complejas paso a paso. Para agentes que toman muchas decisiones rápidas, un modelo más pequeño y rápido podría ser mejor.

**Investigar alternativas:**
- `llama3.2:3b` — 2GB, muy rápido, sin thinking, bueno para tool use básico
- `qwen2.5:7b` — 4.7GB, rápido, excelente para tool use, sin thinking
- `mistral:7b` — 4.1GB, balanceado, ampliamente usado en agentes
- Comparar: `ollama run llama3.2:3b` vs `gemma4:12b` en velocidad con la misma pregunta

---

## Plan de acción S022

1. **Diagnóstico GPU/CPU** — `ollama ps` y `nvidia-smi` mientras corre gemma4-chat → saber si el problema es VRAM
2. **Test sin thinking** — Probar `/no_think` en qwen3-chat y medir tokens/tiempo
3. **Test OLLAMA_NUM_CTX env var** — Ver si elimina necesidad de alias
4. **Benchmark de modelos alternativos** — llama3.2:3b y qwen2.5:7b vs gemma4:12b en velocidad
5. **Decisión final** — Quedarse con gemma4-chat/qwen3-chat ó cambiar a modelo más rápido para agentes

---

## Comandos de diagnóstico rápido para iniciar S022

```powershell
# 1. Ver si GPU está siendo usada
$env:OLLAMA_MODELS = "D:\ollama"; ollama ps

# 2. Cargar gemma4-chat y medir tiempo real
$start = Get-Date
$body = @{ model = "gemma4-chat"; messages = @(@{ role = "user"; content = "di hola en 5 palabras" }); stream = $false } | ConvertTo-Json
$r = Invoke-RestMethod -Uri "http://localhost:11434/api/chat" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 300
$elapsed = (Get-Date) - $start
Write-Host "Tokens: $($r.eval_count) | Tiempo: $([math]::Round($elapsed.TotalSeconds, 1))s | Tokens/s: $([math]::Round($r.eval_count / $elapsed.TotalSeconds, 1))"

# 3. Ver capas en GPU desde log
Get-Content "$env:LOCALAPPDATA\Ollama\server.log" -Tail 30 | Select-String "gpu|layer|offload" -CaseSensitive:$false
```

**Velocidad de referencia esperada:**
- GPU (con VRAM suficiente): 5-20 tokens/s → ~10-30s para respuesta simple
- CPU puro: 0.5-2 tokens/s → 1-5 minutos para respuesta simple ← probable causa actual
