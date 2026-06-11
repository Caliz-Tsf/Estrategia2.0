# -*- coding: utf-8 -*-
"""VER-05 M5 — Judas, sweep/grab fino, false breakout, spring, raid, displacement.
Sobre eurusd_m5.csv (datos reales TradingView MCP). KZ junio: London 06-09 UTC, NY AM 12-15 UTC."""
import csv, datetime, os
HERE=os.path.dirname(os.path.abspath(__file__))
def gmt(e): return datetime.datetime.fromtimestamp(int(e),datetime.UTC).strftime("%Y-%m-%d %H:%M")
def hod(e):
    d=datetime.datetime.fromtimestamp(int(e),datetime.UTC); return d.hour+d.minute/60
bars=[]
with open(os.path.join(HERE,"eurusd_m5.csv")) as f:
    for r in csv.DictReader(f):
        bars.append({"t":int(r["epoch"]),"o":float(r["open"]),"h":float(r["high"]),"l":float(r["low"]),"c":float(r["close"])})
N=len(bars)
print(f"M5 bars={N} {gmt(bars[0]['t'])} -> {gmt(bars[-1]['t'])}")

tr=[0.0]*N
for i in range(N):
    h,l=bars[i]["h"],bars[i]["l"]
    tr[i]=h-l if i==0 else max(h-l,abs(h-bars[i-1]["c"]),abs(l-bars[i-1]["c"]))
ATR=[None]*N; ATR[14]=sum(tr[1:15])/14
for i in range(15,N): ATR[i]=(ATR[i-1]*13+tr[i])/14

def piv(L):
    H=[];Lo=[]
    for c in range(L,N-L):
        if all(bars[c]["h"]>bars[c-k]["h"] and bars[c]["h"]>bars[c+k]["h"] for k in range(1,L+1)): H.append(c)
        if all(bars[c]["l"]<bars[c-k]["l"] and bars[c]["l"]<bars[c+k]["l"] for k in range(1,L+1)): Lo.append(c)
    return H,Lo
swH,swL=piv(5); inH,inL=piv(3)

def disp(i):
    rng=bars[i]["h"]-bars[i]["l"]; body=abs(bars[i]["c"]-bars[i]["o"]); a=ATR[i]
    return (a and rng and rng>=1.5*a and body>=0.7*rng), rng, body, a

print("\n== DISPLACEMENT M5 (>=1.5xATR, cuerpo>=70%) ==")
for i in range(15,N):
    d,rng,body,a=disp(i)
    if d:
        print(f"  {gmt(bars[i]['t'])} {'+1' if bars[i]['c']>bars[i]['o'] else '-1'} rng={rng/a:.2f}xATR body={body/rng*100:.0f}% O{bars[i]['o']:.5f} C{bars[i]['c']:.5f}")

print("\n== SWEEP/GRAB M5 (mecha supera swing no roto, close vuelve) ==")
sweeps=[]
for i in range(6,N):
    for c in [x for x in swL if x+5<i][-8:]:
        if bars[i]["l"]<bars[c]["l"] and bars[i]["c"]>bars[c]["l"]:
            sweeps.append((i,"SSL",c,bars[c]["l"])); break
    for c in [x for x in swH if x+5<i][-8:]:
        if bars[i]["h"]>bars[c]["h"] and bars[i]["c"]<bars[c]["h"]:
            sweeps.append((i,"BSL",c,bars[c]["h"])); break
for i,side,c,lvl in sweeps:
    kz="London" if 6<=hod(bars[i]['t'])<9 else ("NY-AM" if 12<=hod(bars[i]['t'])<15 else "-")
    print(f"  {gmt(bars[i]['t'])} {side} nivel={lvl:.5f} mecha={(bars[i]['l'] if side=='SSL' else bars[i]['h']):.5f} close={bars[i]['c']:.5f}  KZ={kz}")

print("\n== FALSE BREAKOUT M5 (close cruza swing, otra vela cierra de vuelta <=2) ==")
for i in range(6,N-2):
    for c in [x for x in swL if x+5<i][-8:]:
        lvl=bars[c]["l"]
        if bars[i]["c"]<lvl:
            for j in range(i+1,min(i+3,N)):
                if bars[j]["c"]>lvl:
                    print(f"  {gmt(bars[i]['t'])} close={bars[i]['c']:.5f}<SSL {lvl:.5f} -> recupera {gmt(bars[j]['t'])} close={bars[j]['c']:.5f}"); break
            break
    for c in [x for x in swH if x+5<i][-8:]:
        lvl=bars[c]["h"]
        if bars[i]["c"]>lvl:
            for j in range(i+1,min(i+3,N)):
                if bars[j]["c"]<lvl:
                    print(f"  {gmt(bars[i]['t'])} close={bars[i]['c']:.5f}>BSL {lvl:.5f} -> recupera {gmt(bars[j]['t'])} close={bars[j]['c']:.5f}"); break
            break

print("\n== JUDAS (sweep en 1a mitad de KZ + displacement contrario <=6 velas) ==")
def kz_info(e):
    h=hod(e)
    if 6<=h<9: return "London", h<7.5
    if 12<=h<15: return "NY-AM", h<13.5
    return None,False
for i,side,c,lvl in sweeps:
    kz,firsthalf=kz_info(bars[i]['t'])
    if not kz or not firsthalf: continue
    want = +1 if side=="SSL" else -1
    for j in range(i+1,min(i+7,N)):
        d,rng,body,a=disp(j)
        dirn = 1 if bars[j]["c"]>bars[j]["o"] else -1
        if d and dirn==want:
            print(f"  {kz} sweep {side} {gmt(bars[i]['t'])} nivel={lvl:.5f} -> displacement {('+1' if dirn>0 else '-1')} {gmt(bars[j]['t'])} rng={rng/a:.2f}xATR"); break

print("\n== SPRING (sweep SSL del minimo de rango + reversion al alza) ==")
# minimo de rango reciente y reversion fuerte
lookback=60
for i in range(lookback,N):
    win=[bars[k]["l"] for k in range(i-lookback,i)]
    rangelow=min(win)
    if bars[i]["l"]<rangelow and bars[i]["c"]>rangelow:
        # reversion: siguiente displacement up dentro de 6
        for j in range(i,min(i+6,N)):
            d,rng,body,a=disp(j)
            if d and bars[j]["c"]>bars[j]["o"]:
                print(f"  SPRING {gmt(bars[i]['t'])} barre min rango {rangelow:.5f} (low={bars[i]['l']:.5f}) -> rally {gmt(bars[j]['t'])} rng={rng/a:.2f}xATR")
                break
