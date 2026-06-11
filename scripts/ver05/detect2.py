# -*- coding: utf-8 -*-
"""VER-05 parte 2 — OB, sweep/grab, rejection, EMAs, session opens, kill zones,
OTE/GP, impulso/correccion y contraejemplos. Sobre eurusd_h1.csv (datos reales)."""
import csv, datetime, os
HERE = os.path.dirname(os.path.abspath(__file__))
def gmt(e): return datetime.datetime.fromtimestamp(int(e), datetime.UTC).strftime("%Y-%m-%d %H:%M")
def hod(e): return datetime.datetime.fromtimestamp(int(e), datetime.UTC).hour
def wd(e):  return datetime.datetime.fromtimestamp(int(e), datetime.UTC).weekday()

bars=[]
with open(os.path.join(HERE,"eurusd_h1.csv")) as f:
    for r in csv.DictReader(f):
        bars.append({"t":int(r["epoch"]),"o":float(r["open"]),"h":float(r["high"]),
                     "l":float(r["low"]),"c":float(r["close"])})
N=len(bars)

def atr_series(p=14):
    tr=[0.0]*N
    for i in range(N):
        h,l=bars[i]["h"],bars[i]["l"]
        tr[i]=h-l if i==0 else max(h-l,abs(h-bars[i-1]["c"]),abs(l-bars[i-1]["c"]))
    a=[None]*N; a[p]=sum(tr[1:p+1])/p
    for i in range(p+1,N): a[i]=(a[i-1]*(p-1)+tr[i])/p
    return a,tr
ATR,TR=atr_series(14)
# cumulative mean range (volMeasure estilo LuxAlgo)
cmr=[None]*N; s=0.0
for i in range(N):
    s+=TR[i]; cmr[i]=s/(i+1)

def ema(period):
    k=2/(period+1); e=[None]*N; e[0]=bars[0]["c"]
    for i in range(1,N): e[i]=bars[i]["c"]*k+e[i-1]*(1-k)
    return e
E20,E50,E200=ema(20),ema(50),ema(200)

def piv(L):
    H=[];Lo=[]
    for c in range(L,N-L):
        if all(bars[c]["h"]>bars[c-k]["h"] and bars[c]["h"]>bars[c+k]["h"] for k in range(1,L+1)): H.append(c)
        if all(bars[c]["l"]<bars[c-k]["l"] and bars[c]["l"]<bars[c+k]["l"] for k in range(1,L+1)): Lo.append(c)
    return H,Lo
swH,swL=piv(5)

# ---------- CONTRAEJEMPLO swing: high mayor solo a un lado ----------
print("== CONTRAEJEMPLO SWING (high mayor a la IZQ 5 pero NO a la der: no es swing) ==")
cnt=0
for c in range(5,N-5):
    left=all(bars[c]["h"]>bars[c-k]["h"] for k in range(1,6))
    right=all(bars[c]["h"]>bars[c+k]["h"] for k in range(1,6))
    if left and not right:
        # encontrar cual vela derecha lo supera
        viol=next(k for k in range(1,6) if bars[c+k]["h"]>=bars[c]["h"])
        print(f"  idx{c} {gmt(bars[c]['t'])} high={bars[c]['h']:.5f} supera 5 izq pero idx{c+viol} "
              f"({gmt(bars[c+viol]['t'])}) high={bars[c+viol]['h']:.5f} >= -> NO swing"); cnt+=1
        if cnt>=3: break

# ---------- SWEEP / GRAB (mecha perfora swing no roto, close vuelve dentro) ----------
print("\n== GRAB (mecha supera swing high/low previo, close de vuelta) ==")
def grabs():
    out=[]
    for i in range(6,N):
        # buscar swing high confirmado mas reciente antes de i con nivel no superado por close aun
        for c in [x for x in swH if x+5<i][-6:]:
            lvl=bars[c]["h"]
            if bars[i]["h"]>lvl and bars[i]["c"]<lvl:
                out.append((i,"BSL",c,lvl)); break
        for c in [x for x in swL if x+5<i][-6:]:
            lvl=bars[c]["l"]
            if bars[i]["l"]<lvl and bars[i]["c"]>lvl:
                out.append((i,"SSL",c,lvl)); break
    return out
for i,side,c,lvl in grabs():
    print(f"  idx{i} {gmt(bars[i]['t'])} {side} barre swing idx{c}({gmt(bars[c]['t'])}) "
          f"nivel={lvl:.5f} mecha={'H'+format(bars[i]['h'],'.5f') if side=='BSL' else 'L'+format(bars[i]['l'],'.5f')} close={bars[i]['c']:.5f}")

# ---------- REJECTION (mecha >= 2x cuerpo) ----------
print("\n== REJECTION (mecha >= 2x cuerpo, cierre en mitad fav) ==")
for i in range(15,N):
    o,h,l,c=bars[i]["o"],bars[i]["h"],bars[i]["l"],bars[i]["c"]
    body=abs(c-o);
    if body==0: continue
    lw=min(o,c)-l; uw=h-max(o,c); rng=h-l
    if lw>=2*body and c>(l+rng/2):
        print(f"  idx{i} {gmt(bars[i]['t'])} ALCISTA mecha_inf={lw/body:.1f}x cuerpo low={l:.5f} close={c:.5f}")
    elif uw>=2*body and c<(l+rng/2):
        print(f"  idx{i} {gmt(bars[i]['t'])} BAJISTA mecha_sup={uw/body:.1f}x cuerpo high={h:.5f} close={c:.5f}")

# ---------- OB (ultima vela contraria antes de ruptura, leg con vela alta vol >=2x cmr) ----------
print("\n== ORDER BLOCKS (ultima vela contraria antes de BOS/CHoCH, filtro 2x CMR) ==")
# rupturas swing detectadas en detect.py (reproducimos minimal): close cruza swing no roto
def breaks():
    Hc={c+5:c for c in swH}; Lc={c+5:c for c in swL}
    top=btm=None;tb=lb=True;bias=0;out=[]
    for i in range(N):
        if i in Hc: top=bars[Hc[i]]["h"];tb=False;topc=Hc[i]
        if i in Lc: btm=bars[Lc[i]]["l"];lb=False;btmc=Lc[i]
        if top is not None and not tb and bars[i]["c"]>top:
            out.append((i,"up"));bias=1;tb=True
        if btm is not None and not lb and bars[i]["c"]<btm:
            out.append((i,"down"));bias=-1;lb=True
    return out
for i,dirn in breaks():
    # leg = desde el ultimo swing opuesto hasta i; buscar ultima vela contraria
    lo=max(0,i-12)
    if dirn=="up":
        cand=[j for j in range(lo,i) if bars[j]["c"]<bars[j]["o"]]
        hv=any((bars[j]["h"]-bars[j]["l"])>=2*cmr[j] for j in range(lo,i+1))
        if cand and hv:
            j=cand[-1]; print(f"  OB alcista idx{j} {gmt(bars[j]['t'])} zona=[{bars[j]['l']:.5f},{bars[j]['h']:.5f}] -> ruptura up idx{i} {gmt(bars[i]['t'])}")
    else:
        cand=[j for j in range(lo,i) if bars[j]["c"]>bars[j]["o"]]
        hv=any((bars[j]["h"]-bars[j]["l"])>=2*cmr[j] for j in range(lo,i+1))
        if cand and hv:
            j=cand[-1]; print(f"  OB bajista idx{j} {gmt(bars[j]['t'])} zona=[{bars[j]['l']:.5f},{bars[j]['h']:.5f}] -> ruptura down idx{i} {gmt(bars[i]['t'])}")

# ---------- EMAs ----------
print("\n== EMAs 20/50/200 (ultimas barras, alineacion) ==")
for i in [N-1,N-20,N-40,N-60,N-80]:
    if E200[i] is None: continue
    al = "20>50>200(+1)" if E20[i]>E50[i]>E200[i] else ("20<50<200(-1)" if E20[i]<E50[i]<E200[i] else "mixto")
    rel=f"close{'>' if bars[i]['c']>E200[i] else '<'}EMA200"
    print(f"  idx{i} {gmt(bars[i]['t'])} c={bars[i]['c']:.5f} E20={E20[i]:.5f} E50={E50[i]:.5f} E200={E200[i]:.5f}  {rel}  {al}")

# ---------- SESSION OPENS (broker day = 22:00 UTC; weekly = lunes/domingo 22:00) ----------
print("\n== SESSION OPENS (apertura diaria broker 22:00 UTC) + proximidad 0.5xATR ==")
opens=[]
for i in range(N):
    if hod(bars[i]["t"])==22:
        opens.append((i,bars[i]["o"]))
for i,op in opens[:6]:
    print(f"  daily open idx{i} {gmt(bars[i]['t'])} = {op:.5f}")

# ---------- KILL ZONES (London BST 06-09 UTC, NY AM EDT 12-15 UTC, junio) ----------
print("\n== KILL ZONES (junio: London=06-09 UTC, NY AM=12-15 UTC) ejemplos ==")
ln=[i for i in range(N) if 6<=hod(bars[i]["t"])<9][:4]
ny=[i for i in range(N) if 12<=hod(bars[i]["t"])<15][:4]
for i in ln: print(f"  London idx{i} {gmt(bars[i]['t'])} (1a mitad: {hod(bars[i]['t'])<8})")
for i in ny: print(f"  NY-AM  idx{i} {gmt(bars[i]['t'])}")

# ---------- OTE/GP sobre el impulso bajista idx206 (1.16416->1.14997) ----------
print("\n== OTE / GOLDEN POCKET (impulso bajista 05-29..06-08) ==")
# impulso de origen high idx89? usar leg impulsiva 1.16859(idx89) -> 1.14997(idx227) NO; usar BOS down idx206
hi=1.16455; lo=1.14997  # swing high idx181 a swing low idx227 (pierna bajista que produjo BOS)
for name,a,b in [("GP",0.5,0.618),("OTE",0.618,0.79)]:
    z1=lo+(hi-lo)*a; z2=lo+(hi-lo)*b
    print(f"  {name}: retroceso {a*100:.0f}-{b*100:.0f}% de [{lo:.5f},{hi:.5f}] = [{z1:.5f},{z2:.5f}]")
# buscar barras que entraron a la zona OTE tras el low
z1=lo+(hi-lo)*0.618; z2=lo+(hi-lo)*0.79
hits=[i for i in range(228,N) if z1<=bars[i]["h"]<=z2 or z1<=bars[i]["c"]<=z2][:5]
for i in hits: print(f"    toca OTE idx{i} {gmt(bars[i]['t'])} h={bars[i]['h']:.5f} c={bars[i]['c']:.5f}")
