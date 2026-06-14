# -*- coding: utf-8 -*-
"""Escanea FVGs SUB-umbral (gap < 0.25xATR) = micro-ineficiencias descartadas.
Misma metodologia que detect.py (ATR14 Wilder, offsets [0]/[2])."""
import csv, datetime, os
HERE = os.path.dirname(os.path.abspath(__file__))
def gmt(e): return datetime.datetime.fromtimestamp(int(e), datetime.UTC).strftime("%Y-%m-%d %H:%M")
bars=[]
with open(os.path.join(HERE,"eurusd_h1.csv")) as f:
    for r in csv.DictReader(f):
        bars.append({"t":int(r["epoch"]),"o":float(r["open"]),"h":float(r["high"]),"l":float(r["low"]),"c":float(r["close"])})
N=len(bars)
def atr_series(p=14):
    tr=[None]*N
    for i in range(N):
        h,l=bars[i]["h"],bars[i]["l"]
        tr[i]= h-l if i==0 else max(h-l,abs(h-bars[i-1]["c"]),abs(l-bars[i-1]["c"]))
    atr=[None]*N; atr[p]=sum(tr[1:p+1])/p
    for i in range(p+1,N): atr[i]=(atr[i-1]*(p-1)+tr[i])/p
    return atr
ATR=atr_series(14)
print("== FVG SUB-UMBRAL (0 < gap < 0.25xATR) = descartados ==")
rows=[]
for i in range(2,N):
    a=ATR[i]
    if a is None: continue
    thr=0.25*a
    if bars[i]["l"]>bars[i-2]["h"]:
        gap=bars[i]["l"]-bars[i-2]["h"]
        if 0<gap<thr:
            ce=(bars[i]["l"]+bars[i-2]["h"])/2
            rows.append((gap/a,i,"ALCISTA",bars[i-2]["h"],bars[i]["l"],gap,ce,a))
    if bars[i]["h"]<bars[i-2]["l"]:
        gap=bars[i-2]["l"]-bars[i]["h"]
        if 0<gap<thr:
            ce=(bars[i]["h"]+bars[i-2]["l"])/2
            rows.append((gap/a,i,"BAJISTA",bars[i]["h"],bars[i-2]["l"],gap,ce,a))
for ratio,i,d,bot,top,gap,ce,a in sorted(rows,key=lambda x:-x[0]):
    print(f"  idx{i:3d} {gmt(bars[i]['t'])} {d} gap=[{bot:.5f},{top:.5f}] gap={gap:.5f} = {ratio:.3f}xATR (thr=0.25, ATR={a:.5f}) CE={ce:.5f}")
print(f"\n  total sub-umbral = {len(rows)}")
i=152; a=ATR[i]
gap=bars[i-2]["l"]-bars[i]["h"]
print(f"\n== caso documentado 06-03 06:00 (idx152) ==")
print(f"  high[0]={bars[i]['h']:.5f} low[2]={bars[i-2]['l']:.5f} -> gap={gap:.5f} = {gap/a:.3f}xATR  (thr 0.25xATR={0.25*a:.5f}) -> {'PASA' if gap>=0.25*a else 'DESCARTA'}")
print(f"  close[0]={bars[i]['c']:.5f}  bottom(high[0])={bars[i]['h']:.5f} -> invalida si close<bottom: {bars[i]['c']<bars[i]['h']}")
