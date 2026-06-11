# -*- coding: utf-8 -*-
"""
VER-05 — Extractor de casos reales SMC/ICT sobre EURUSD H1.
Implementa las definiciones de docs/reglas-smc-ict.md. NO inventa: detecta sobre
las velas reales de eurusd_h1.csv (extraidas via TradingView MCP data_get_ohlcv).
"""
import csv, datetime, os

HERE = os.path.dirname(os.path.abspath(__file__))

def gmt(epoch):
    return datetime.datetime.fromtimestamp(int(epoch), datetime.UTC).strftime("%Y-%m-%d %H:%M")

bars = []
with open(os.path.join(HERE, "eurusd_h1.csv")) as f:
    for row in csv.DictReader(f):
        bars.append({
            "t": int(row["epoch"]),
            "o": float(row["open"]), "h": float(row["high"]),
            "l": float(row["low"]),  "c": float(row["close"]),
        })
N = len(bars)
print(f"bars={N}  first={gmt(bars[0]['t'])}  last={gmt(bars[-1]['t'])}")

# ---- ATR(14) Wilder ----
def atr_series(period=14):
    tr = [None]*N
    for i in range(N):
        h,l = bars[i]["h"], bars[i]["l"]
        if i==0:
            tr[i] = h-l
        else:
            pc = bars[i-1]["c"]
            tr[i] = max(h-l, abs(h-pc), abs(l-pc))
    atr=[None]*N
    seed = sum(tr[1:period+1])/period
    atr[period] = seed
    for i in range(period+1, N):
        atr[i] = (atr[i-1]*(period-1)+tr[i])/period
    return atr, tr
ATR, TR = atr_series(14)

# ---- Pivots ----
def pivots(L):
    ph=[None]*N; pl=[None]*N  # confirmed-at index marker -> store center idx
    res_h=[]; res_l=[]
    for c in range(L, N-L):
        hh = bars[c]["h"]; ll = bars[c]["l"]
        is_h = all(hh > bars[c-k]["h"] and hh > bars[c+k]["h"] for k in range(1,L+1))
        is_l = all(ll < bars[c-k]["l"] and ll < bars[c+k]["l"] for k in range(1,L+1))
        if is_h: res_h.append(c)
        if is_l: res_l.append(c)
    return res_h, res_l

swH, swL = pivots(5)    # swing structure
inH, inL = pivots(3)    # internal

print(f"\n== SWINGS (swingLen=5) ==  highs={len(swH)} lows={len(swL)}")

# ---- Clasificacion HH/HL/LH/LL sobre swings (ordenados por indice) ----
events = sorted([(c,"H") for c in swH]+[(c,"L") for c in swL])
prevH=None; prevL=None
classified=[]
for c,typ in events:
    if typ=="H":
        if prevH is None: lab="H?"
        elif bars[c]["h"]>prevH: lab="HH"
        elif bars[c]["h"]<prevH: lab="LH"
        else: lab="EQ-H"
        classified.append((c,"high",bars[c]["h"],lab))
        prevH=bars[c]["h"]
    else:
        if prevL is None: lab="L?"
        elif bars[c]["l"]>prevL: lab="HL"
        elif bars[c]["l"]<prevL: lab="LL"
        else: lab="EQ-L"
        classified.append((c,"low",bars[c]["l"],lab))
        prevL=bars[c]["l"]
print("\n== CLASIFICACION SWINGS ==")
for c,k,p,lab in classified:
    print(f"  idx{c:3d} {gmt(bars[c]['t'])}  {k:4s} {p:.5f}  {lab}  (confirma idx{c+5} {gmt(bars[c+5]['t'])})")

# ---- BOS / CHoCH / MSS (modelo structure high/low, ruptura por CIERRE) ----
# Camina barra a barra; al confirmarse un pivote (en c+L) actualiza top/btm.
def disp(i):
    rng = bars[i]["h"]-bars[i]["l"]
    body = abs(bars[i]["c"]-bars[i]["o"])
    a = ATR[i]
    if a is None or rng==0: return False, rng, body, a
    return (rng >= 1.5*a and body >= 0.70*rng), rng, body, a

def run_structure(Hidx, Lidx, L, label):
    Hset = {c+L: c for c in Hidx}   # confirm-bar -> center
    Lset = {c+L: c for c in Lidx}
    top=None; btm=None; topC=None; btmC=None
    topBroken=True; btmBroken=True
    bias=0
    out=[]
    for i in range(N):
        # confirmar pivotes nacidos en esta barra
        if i in Hset:
            c=Hset[i]; top=bars[c]["h"]; topC=c; topBroken=False
        if i in Lset:
            c=Lset[i]; btm=bars[c]["l"]; btmC=c; btmBroken=False
        cl=bars[i]["c"]
        if top is not None and not topBroken and cl>top:
            kind = "BOS" if bias==1 else "CHoCH"
            d,rng,body,a = disp(i)
            mss = (kind=="CHoCH" and d)
            out.append((i,"up",kind,top,topC,cl,mss,rng,body,a))
            bias=1; topBroken=True
        if btm is not None and not btmBroken and cl<btm:
            kind = "BOS" if bias==-1 else "CHoCH"
            d,rng,body,a = disp(i)
            mss = (kind=="CHoCH" and d)
            out.append((i,"down",kind,btm,btmC,cl,mss,rng,body,a))
            bias=-1; btmBroken=True
    print(f"\n== {label} (ruptura por close) ==")
    for i,dirn,kind,lvl,lvlC,cl,mss,rng,body,a in out:
        tag = "  <-- MSS (displacement)" if mss else ""
        rr = f" rng={rng/a:.2f}xATR body={body/rng*100:.0f}%" if a and rng else ""
        print(f"  idx{i:3d} {gmt(bars[i]['t'])}  {kind:5s} {dirn:4s} rompe nivel {lvl:.5f}"
              f" (swing idx{lvlC} {gmt(bars[lvlC]['t'])}) close={cl:.5f}{rr}{tag}")
    return out

bos_swing = run_structure(swH, swL, 5, "ESTRUCTURA SWING (BOS/CHoCH/MSS)")
bos_int   = run_structure(inH, inL, 3, "ESTRUCTURA INTERNA (BOS/CHoCH interno)")

# ---- Displacement (todas las velas) ----
print("\n== DISPLACEMENT (rango>=1.5xATR y cuerpo>=70%) ==")
for i in range(15,N):
    d,rng,body,a = disp(i)
    if d:
        dirn = "+1" if bars[i]["c"]>bars[i]["o"] else "-1"
        print(f"  idx{i:3d} {gmt(bars[i]['t'])} {dirn} rng={rng/a:.2f}xATR body={body/rng*100:.0f}% O{bars[i]['o']:.5f} C{bars[i]['c']:.5f}")

# ---- FVG (3 velas, umbral 0.25xATR) ----
print("\n== FVG (fixed 0.25xATR, confirma cierre 3a vela) ==")
for i in range(2,N):
    a=ATR[i]
    if a is None: continue
    thr=0.25*a
    # alcista: low[i] > high[i-2]
    if bars[i]["l"] > bars[i-2]["h"]:
        gap = bars[i]["l"]-bars[i-2]["h"]
        if gap>=thr:
            ce=(bars[i]["l"]+bars[i-2]["h"])/2
            print(f"  idx{i:3d} {gmt(bars[i]['t'])} ALCISTA gap=[{bars[i-2]['h']:.5f},{bars[i]['l']:.5f}] "
                  f"h={gap/a:.2f}xATR CE={ce:.5f}")
    if bars[i]["h"] < bars[i-2]["l"]:
        gap = bars[i-2]["l"]-bars[i]["h"]
        if gap>=thr:
            ce=(bars[i]["h"]+bars[i-2]["l"])/2
            print(f"  idx{i:3d} {gmt(bars[i]['t'])} BAJISTA gap=[{bars[i]['h']:.5f},{bars[i-2]['l']:.5f}] "
                  f"h={gap/a:.2f}xATR CE={ce:.5f}")

# ---- EQH / EQL (|h1-h2|<=0.1xATR entre swings consecutivos del mismo tipo) ----
print("\n== EQH / EQL (umbral 0.1xATR, swings 5/5) ==")
def eqhl(idxs, kind):
    key = "h" if kind=="EQH" else "l"
    for a_,b_ in zip(idxs, idxs[1:]):
        diff=abs(bars[a_][key]-bars[b_][key])
        atrv=ATR[b_+5] if b_+5<N else ATR[b_]
        if atrv and diff<=0.1*atrv:
            print(f"  {kind}: idx{a_} {gmt(bars[a_]['t'])} {bars[a_][key]:.5f}  ~=  "
                  f"idx{b_} {gmt(bars[b_]['t'])} {bars[b_][key]:.5f}  (diff={diff/atrv:.3f}xATR)")
eqhl(swH,"EQH"); eqhl(swL,"EQL")

# ---- Premium/Discount sobre rango dominante (strong high/low de la ventana) ----
print("\n== PREMIUM/DISCOUNT (rango ventana completa) ==")
HI=max(b["h"] for b in bars); LO=min(b["l"] for b in bars)
eq=(HI+LO)/2
print(f"  strong_high={HI:.5f}  strong_low={LO:.5f}  eq(50%)={eq:.5f}")
print(f"  banda equilibrium 45-55% = [{LO+0.45*(HI-LO):.5f}, {LO+0.55*(HI-LO):.5f}]")
print(f"  precio actual={bars[-1]['c']:.5f} -> "
      f"{'DISCOUNT' if bars[-1]['c']<eq else 'PREMIUM'}")
