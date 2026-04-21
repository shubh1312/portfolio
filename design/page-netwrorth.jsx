// Net Worth (Home) page
const { useState: useStateH } = React;

function NetWorthPage({ currency }){
  const sym = currency === 'INR' ? '₹' : '$';
  const T = totals();
  const rate = currency === 'INR' ? 83.42 : 1;
  const V = T.value * rate;
  const I = T.invested * rate;
  const G = T.gain * rate;

  const [range, setRange] = useStateH('1Y');
  const ranges = ['1W','1M','3M','6M','YTD','1Y','ALL'];

  return (
    <div className="content">
      {/* HERO */}
      <section className="hero">
        <div className="hero-main">
          <div className="hero-label">Total Net Worth · as of Apr 21, 2026</div>
          <div className="hero-value serif">
            <span className="cur">{sym}</span>
            {Math.floor(V).toLocaleString('en-US')}
            <span className="cents">.{((V%1).toFixed(2)).slice(2)}</span>
          </div>
          <div className="hero-delta">
            <span className="chip up">▲ {fmt(G, sym)} ({fmtPct(T.pct)})</span>
            <span className="mute" style={{fontSize:12}}>since first investment · 3.2 yrs</span>
            <span className="chip">CAGR 19.4%</span>
            <span className="chip">IRR 21.8%</span>
          </div>
          <div className="hero-spark">
            <Sparkline data={SERIES.map(s=>s.v)} color="#C7F651" area={true}/>
          </div>
          <div style={{display:'flex', gap:6, marginTop:36, position:'relative', zIndex:2}}>
            {ranges.map(r=>(
              <button key={r} className={`fchip ${range===r?'on':''}`} onClick={()=>setRange(r)}>{r}</button>
            ))}
          </div>
        </div>

        <div className="hero-side">
          <div className="stat">
            <div className="stat-l">
              <div className="stat-k">Invested</div>
              <div className="stat-v">{fmt(I, sym)}</div>
            </div>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" width="28" height="28" className="stat-ico"><path d="M12 20V4M5 11l7-7 7 7"/></svg>
          </div>
          <div className="stat">
            <div className="stat-l">
              <div className="stat-k">Unrealised Gain</div>
              <div className="stat-v up">{fmt(G, sym)}</div>
            </div>
            <span className="stat-sub up">{fmtPct(T.pct)}</span>
          </div>
          <div className="stat">
            <div className="stat-l">
              <div className="stat-k">Positions / Tickers</div>
              <div className="stat-v">{HOLDINGS.length}</div>
            </div>
            <span className="stat-sub mute">across 5 classes</span>
          </div>
          <div className="stat">
            <div className="stat-l">
              <div className="stat-k">Cash Reserves</div>
              <div className="stat-v">{fmt(8400 * rate, sym)}</div>
            </div>
            <span className="stat-sub mute">ready to deploy</span>
          </div>
        </div>
      </section>

      {/* ASSET CLASSES (hero grid) */}
      <section>
        <div className="section-head">
          <h2>By <em>asset class</em></h2>
          <div className="section-tools">
            <div className="chips">
              <button className="fchip on">All</button>
              <button className="fchip">Gainers</button>
              <button className="fchip">Losers</button>
            </div>
          </div>
        </div>
        <div className="grid-5" style={{marginTop:18}}>
          {ASSET_CLASSES.map((a,i)=>{
            const gain = (a.value-a.invested) * rate;
            const pct = (a.value-a.invested)/a.invested*100;
            const sp = mkSpark(i+3, 24, 0.03);
            return (
              <a key={a.key} href={`#/${a.key}`} className="class-card" style={{textDecoration:'none'}}>
                <div className="class-head">
                  <div className="tkr-logo" style={{background:a.color, color:'#0B0B0D', borderColor:a.color, width:24, height:24, fontSize:12, fontWeight:600}}>{a.icon}</div>
                  <span className={`mono ${pct>=0?'up':'down'}`} style={{fontSize:11}}>{fmtPct(pct)}</span>
                </div>
                <div className="class-name">{a.name}</div>
                <div className="class-value">{fmt(a.value*rate, sym)}</div>
                <div className="class-spark">
                  <Sparkline data={sp} color={a.color} stroke={1.2} height={28}/>
                </div>
                <div className="class-sub">
                  <span className="mute">inv {fmt(a.invested*rate, sym)}</span>
                  <span className={pct>=0?'up':'down'}>{fmt(gain, sym)}</span>
                </div>
              </a>
            );
          })}
        </div>
      </section>

      {/* ALLOCATION + CHART */}
      <section className="grid-2">
        <div className="card">
          <div className="card-head">
            <div className="card-title">Portfolio Journey</div>
            <div className="chips">
              <button className="fchip on">Value</button>
              <button className="fchip">Invested</button>
              <button className="fchip">Gain</button>
            </div>
          </div>
          <div className="chart-frame">
            <Sparkline data={SERIES.map(s=>s.v)} color="#EDE6D6" area={true} height={320} stroke={1.5}/>
            <div style={{position:'absolute', right:10, top:10, fontFamily:'var(--mono)', fontSize:11, color:'var(--fg-mute)'}}>
              range: <span style={{color:'var(--fg)'}}>{range}</span>
            </div>
          </div>
          <div style={{display:'flex', justifyContent:'space-between', marginTop:12, fontFamily:'var(--mono)', fontSize:11, color:'var(--fg-mute)'}}>
            <span>Jan '25</span><span>Apr '25</span><span>Jul '25</span><span>Oct '25</span><span>Jan '26</span><span style={{color:'var(--fg)'}}>Apr '26</span>
          </div>
        </div>

        <div className="card">
          <div className="card-head">
            <div className="card-title">Allocation</div>
            <span className="mono mute" style={{fontSize:11}}>{fmt(V, sym)}</span>
          </div>
          <div className="alloc">
            <div className="alloc-bar">
              {ASSET_CLASSES.map(a=>{
                const w = (a.value / T.value) * 100;
                return <div key={a.key} className="alloc-seg" style={{flex:w, background:a.color}} title={a.name}/>
              })}
            </div>
            <div className="alloc-legend">
              {ASSET_CLASSES.map(a=>{
                const w = (a.value / T.value) * 100;
                return (
                  <div key={a.key} className="alloc-row">
                    <span className="alloc-sw" style={{background:a.color}}/>
                    <span className="alloc-name">{a.name}<small>{a.txns} txns</small></span>
                    <span className="alloc-amt">{fmt(a.value*rate, sym)}</span>
                    <span className="alloc-pct">{w.toFixed(1)}%</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* UNIFIED HOLDINGS */}
      <HoldingsTable currency={currency}/>
    </div>
  );
}

// ───────── Holdings Table ─────────
function HoldingsTable({ currency, cls=null }){
  const sym = currency === 'INR' ? '₹' : '$';
  const rate = currency === 'INR' ? 83.42 : 1;
  const [sort, setSort] = useStateH({ k:'value', dir:'desc' });
  const [expanded, setExpanded] = useStateH(new Set());
  const [filter, setFilter] = useStateH('all');
  const [query, setQuery] = useStateH('');

  const total = totals().value * rate;

  const rows = useMemo(()=>{
    return HOLDINGS
      .filter(h => !cls || h.cls === cls)
      .map(h => {
        const native = h.cur === 'INR' ? (currency==='INR'?1:1/rate) : (currency==='INR'?rate:1);
        const invested = h.qty * h.avg * native;
        const value = h.qty * h.price * native;
        const gain = value - invested;
        const pct = gain/invested*100;
        return { ...h, invested, value, gain, pct, weight: value/total*100 };
      })
      .filter(r => filter==='all' || (filter==='gain'?r.pct>=0:r.pct<0))
      .filter(r => !query || (r.sym+r.name).toLowerCase().includes(query.toLowerCase()))
      .sort((a,b)=>{
        const v = sort.dir==='asc' ? 1 : -1;
        return (a[sort.k] > b[sort.k] ? 1 : -1) * v;
      });
  }, [sort, filter, query, currency, cls]);

  const toggle = (sym) => {
    const s = new Set(expanded);
    s.has(sym) ? s.delete(sym) : s.add(sym);
    setExpanded(s);
  };
  const SortH = ({k, children, num}) => (
    <th className={num?'num':''}>
      <button onClick={()=>setSort({k, dir: sort.k===k && sort.dir==='desc' ? 'asc':'desc'})} style={{color:'inherit', fontSize:'inherit', letterSpacing:'inherit', textTransform:'inherit'}}>
        {children} {sort.k===k ? (sort.dir==='desc'?'↓':'↑') : ''}
      </button>
    </th>
  );

  const clsMap = Object.fromEntries(ASSET_CLASSES.map(a=>[a.key,a]));

  return (
    <section className="card" style={{padding:0}}>
      <div style={{padding:'20px 20px 12px', display:'flex', alignItems:'center', justifyContent:'space-between', borderBottom:'1px solid var(--line)'}}>
        <div>
          <div className="card-title">Holdings · {rows.length} positions</div>
          <h2 className="serif" style={{fontSize:22, marginTop:4}}>{cls?clsMap[cls].name:'All'} — <em className="mute">by current value</em></h2>
        </div>
        <div style={{display:'flex', gap:10, alignItems:'center'}}>
          <div className="chips">
            <button className={`fchip ${filter==='all'?'on':''}`} onClick={()=>setFilter('all')}>All</button>
            <button className={`fchip ${filter==='gain'?'on':''}`} onClick={()=>setFilter('gain')}>Gainers</button>
            <button className={`fchip ${filter==='loss'?'on':''}`} onClick={()=>setFilter('loss')}>Losers</button>
          </div>
          <div className="search" style={{minWidth:200}}>
            {Ico.search}
            <input placeholder="Filter ticker…" value={query} onChange={e=>setQuery(e.target.value)}/>
          </div>
        </div>
      </div>
      <div className="table-wrap">
        <table className="hold">
          <thead>
            <tr>
              <SortH k="sym">Ticker</SortH>
              <SortH k="qty" num>Qty</SortH>
              <SortH k="avg" num>Avg Buy</SortH>
              <SortH k="price" num>Current</SortH>
              <SortH k="invested" num>Invested</SortH>
              <SortH k="value" num>Value</SortH>
              <SortH k="weight" num>Weight</SortH>
              <SortH k="gain" num>Gain</SortH>
              <SortH k="pct" num>%</SortH>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {rows.map(r=>{
              const ac = clsMap[r.cls];
              const isOpen = expanded.has(r.sym);
              return (
                <React.Fragment key={r.sym}>
                  <tr className={isOpen?'expanded':''} onClick={()=>toggle(r.sym)} style={{cursor:'pointer'}}>
                    <td>
                      <div className="tkr">
                        <div className="tkr-logo" style={{background:ac.color+'22', color:ac.color, borderColor:ac.color+'44'}}>{r.sym[0]}</div>
                        <div className="tkr-name">
                          <b>{r.sym}</b>
                          <span>{r.name}</span>
                        </div>
                      </div>
                    </td>
                    <td className="num">{r.qty.toLocaleString('en-US',{maximumFractionDigits:4})}</td>
                    <td className="num mute">{fmt(r.avg, sym, 2)}</td>
                    <td className="num">{fmt(r.price, sym, 2)}</td>
                    <td className="num mute">{fmt(r.invested, sym)}</td>
                    <td className="num">{fmt(r.value, sym)}</td>
                    <td className="num">
                      <div className="bar-cell">
                        <div className="b"><span style={{width:`${Math.min(100,r.weight*6)}%`}}/></div>
                        <span className="n">{r.weight.toFixed(1)}%</span>
                      </div>
                    </td>
                    <td className={`num ${r.gain>=0?'up':'down'}`}>{fmt(r.gain, sym)}</td>
                    <td className={`num ${r.pct>=0?'up':'down'}`}><b>{fmtPct(r.pct)}</b></td>
                    <td style={{textAlign:'right', color:'var(--fg-mute)'}}>{isOpen?Ico.down:Ico.right}</td>
                  </tr>
                  {isOpen && (
                    <tr className="expand-row">
                      <td colSpan={10}>
                        <div className="expand-inner">
                          <div className="expand-grid expand-head">
                            <span>Account</span><span>Platform</span><span>Qty</span><span>Invested</span><span>P&L</span>
                          </div>
                          <div className="expand-grid">
                            <span style={{color:'var(--fg)'}}>Primary · INR-1</span><span>Zerodha</span><span>{(r.qty*0.6).toFixed(2)}</span><span>{fmt(r.invested*0.6, sym)}</span><span className={r.pct>=0?'up':'down'}>{fmt(r.gain*0.6, sym)}</span>
                          </div>
                          <div className="expand-grid">
                            <span style={{color:'var(--fg)'}}>Secondary · {r.cur==='USD'?'Vested':'INDmoney'}</span><span>{r.cur==='USD'?'Vested':'INDmoney'}</span><span>{(r.qty*0.4).toFixed(2)}</span><span>{fmt(r.invested*0.4, sym)}</span><span className={r.pct>=0?'up':'down'}>{fmt(r.gain*0.4, sym)}</span>
                          </div>
                          <div style={{display:'flex', gap:8, marginTop:8}}>
                            <button className="fchip">Edit qty</button>
                            <button className="fchip">Add note</button>
                            <button className="fchip">View transactions</button>
                            <button className="fchip">Remove</button>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}

Object.assign(window, { NetWorthPage, HoldingsTable });
