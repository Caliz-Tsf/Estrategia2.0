(function(){
  var bars = window.TradingViewApi._activeChartWidgetWV.value()._chartWidget.model().mainSeries().bars();
  if(!bars || typeof bars.lastIndex!=='function') return 'NO_BARS';
  var end=bars.lastIndex(), start=Math.max(bars.firstIndex(), end-NBARS+1);
  var B=[];
  for(var i=start;i<=end;i++){var v=bars.valueAt(i); if(v) B.push({t:v[0],o:v[1],h:v[2],l:v[3],c:v[4]});}
  var n=B.length;
  if(n<60) return 'POCAS_BARRAS:'+n;

  // ATR14 (RMA), igual que ta.atr(14)
  var atr=[], prev=null;
  for(var i=0;i<n;i++){
    var tr = i===0 ? (B[0].h-B[0].l) : Math.max(B[i].h-B[i].l, Math.abs(B[i].h-B[i-1].c), Math.abs(B[i].l-B[i-1].c));
    prev = (prev===null) ? tr : (prev*13+tr)/14;
    atr.push(prev);
  }

  var LEN=5, TOL=0.1, MINT=2;
  var pools=[];               // {level,dir,touches,idx,swept,sweptIdx}
  var grabs=[];

  function upsert(isHigh, level, idx, tol){
    var dir = isHigh ? 1 : -1;
    for(var k=0;k<pools.length;k++){
      var p=pools[k];
      if(!p.swept && p.dir===dir && Math.abs(level-p.level)<=tol){
        p.level=(p.level*p.touches+level)/(p.touches+1); p.touches+=1;
        if(idx>p.idx) p.idx=idx;
        return;
      }
    }
    pools.push({level:level,dir:dir,touches:1,idx:idx,firstIdx:idx,swept:false,sweptIdx:-1});
  }

  for(var i=LEN;i<n;i++){
    // pivote simetrico estricto confirmado en i, centrado en i-LEN (== ta.pivothigh(5,5))
    var pi=i-LEN;
    if(pi-LEN>=0){
      var isPH=true, isPL=true;
      for(var d=1;d<=LEN;d++){
        if(!(B[pi].h>B[pi-d].h && B[pi].h>B[pi+d].h)) isPH=false;
        if(!(B[pi].l<B[pi-d].l && B[pi].l<B[pi+d].l)) isPL=false;
      }
      var tol=TOL*atr[i];
      if(isPH) upsert(true,  B[pi].h, pi, tol);
      if(isPL) upsert(false, B[pi].l, pi, tol);
    }
    // MARK barridos con high/low de la barra i
    for(var k=0;k<pools.length;k++){
      var p=pools[k];
      if(!p.swept && ((p.dir===1 && B[i].h>=p.level) || (p.dir===-1 && B[i].l<=p.level))){
        p.swept=true; p.sweptIdx=i;
      }
    }
    // GRAB: barrido EN esta barra, touches < MINT, close de vuelta dentro; el mas cercano al close
    var best=null, bestD=1e9;
    for(var k=0;k<pools.length;k++){
      var p=pools[k];
      if(p.swept && p.sweptIdx===i && p.touches<MINT){
        var trapBSL = p.dir===1  && B[i].c<p.level;
        var trapSSL = p.dir===-1 && B[i].c>p.level;
        var dd=Math.abs(B[i].c-p.level);
        if((trapBSL||trapSSL) && dd<bestD){ bestD=dd; best={p:p,bsl:trapBSL}; }
      }
    }
    if(best) grabs.push({
      t:B[i].t, lado: best.bsl?'BSL':'SSL', nivel:+best.p.level.toFixed(5), toques:best.p.touches,
      origen:B[best.p.firstIdx].t,
      mecha: best.bsl ? +B[i].h.toFixed(5) : +B[i].l.toFixed(5),
      close:+B[i].c.toFixed(5), atr:+atr[i].toFixed(5)
    });
  }
  return {barras:n, desde:new Date(B[0].t).toISOString(), pools_totales:pools.length, grabs_totales:grabs.length,
          ultimos: grabs.slice(-6).map(function(g){return {fecha:new Date(g.t).toISOString(), origen:new Date(g.origen).toISOString(),
            lado:g.lado, nivel:g.nivel, toques:g.toques, mecha:g.mecha, close:g.close, atr:g.atr};})};
})()
