// Net Worth (Home) page
const { useState: useStateH, useMemo: useMemoH } = React;

function NetWorthPage({ currency, portfolioData }){
  const sym = currency === 'INR' ? '₹' : '$';
  const { summary, assetClasses, holdings, cash } = portfolioData;
  const V = summary.total_value || 0;
  const I = summary.total_invested || 0;
  const G = summary.total_gain || 0;
  const pct = summary.abs_return_pct || 0;
  const cashTotal = cash.reduce((s,c) => s + c.amount, 0);

  const [range, setRange] = useStateH('1Y');
  const ranges = ['1W','1M','3M','6M','YTD','1Y','ALL'];

  return (
    <div className="content">
      {/* HERO */}
      <section className="hero">
        <div className="hero-main">
          <div className="hero-label">Total Net Worth · as of {new Date().toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'})}</div>
          <div className="hero-value serif">
            <span className="cur">{sym}</span>
            {Math.floor(V).toLocaleString('en-US')}
            <span className="cents">.{((V%1).toFixed(2)).slice(2)}</span>
          </div>
          <div className="hero-delta">
            <span className={`chip ${G>=0?'up':'down'}`}>{G>=0?'▲':'▼'} {fmt(Math.abs(G), sym)} ({fmtPct(pct)})</span>
            {summary.portfolio_years && <span className="mute" style={{fontSize:12}}>since first investment · {summary.portfolio_years.toFixed(1)} yrs</span>}
            {summary.cagr_pct != null && <span className="chip">CAGR {summary.cagr_pct.toFixed(1)}%</span>}
            {summary.irr_pct != null && <span className="chip">IRR {summary.irr_pct.toFixed(1)}%</span>}
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
              <div className="stat-v up">{fmt(Math.abs(G), sym)}</div>
            </div>
            <span className={`stat-sub ${G>=0?'up':'down'}`}>{fmtPct(pct)}</span>
          </div>
          <div className="stat">
            <div className="stat-l">
              <div className="stat-k">Positions / Tickers</div>
              <div className="stat-v">{holdings.length}</div>
            </div>
            <span className="stat-sub mute">across {assetClasses.length} classes</span>
          </div>
          <div className="stat">
            <div className="stat-l">
              <div className="stat-k">Cash Reserves</div>
              <div className="stat-v">{fmt(cashTotal, sym)}</div>
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
          {assetClasses.map((a,i)=>{
            const sp = mkSpark(i+3, 24, 0.03);
            return (
              <a key={a.key} href={`#/${a.key}`} className="class-card" style={{textDecoration:'none'}}>
                <div className="class-head">
                  <div className="tkr-logo" style={{background:a.color, color:'#0B0B0D', borderColor:a.color, width:24, height:24, fontSize:12, fontWeight:600}}>{a.icon}</div>
                  <span className={`mono ${a.gain_pct>=0?'up':'down'}`} style={{fontSize:11}}>{fmtPct(a.gain_pct)}</span>
                </div>
                <div className="class-name">{a.name}</div>
                <div className="class-value">{fmt(a.value, sym)}</div>
                <div className="class-spark">
                  <Sparkline data={sp} color={a.color} stroke={1.2} height={28}/>
                </div>
                <div className="class-sub">
                  <span className="mute">inv {fmt(a.invested, sym)}</span>
                  <span className={a.gain>=0?'up':'down'}>{fmt(a.gain, sym)}</span>
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
              {assetClasses.map(a=>{
                const w = V > 0 ? (a.value / V) * 100 : 0;
                return <div key={a.key} className="alloc-seg" style={{flex:w, background:a.color}} title={a.name}/>
              })}
            </div>
            <div className="alloc-legend">
              {assetClasses.map(a=>{
                const w = V > 0 ? (a.value / V) * 100 : 0;
                return (
                  <div key={a.key} className="alloc-row">
                    <span className="alloc-sw" style={{background:a.color}}/>
                    <span className="alloc-name">{a.name}<small>{a.txns} txns</small></span>
                    <span className="alloc-amt">{fmt(a.value, sym)}</span>
                    <span className="alloc-pct">{w.toFixed(1)}%</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* UNIFIED HOLDINGS */}
      <HoldingsTable currency={currency} portfolioData={portfolioData}/>
    </div>
  );
}

// ───────── Holdings Table ─────────
function HoldingsTable({ currency, portfolioData, cls=null }){
  const sym = currency === 'INR' ? '₹' : '$';
  const [sort, setSort] = useStateH({ k:'value', dir:'desc' });
  const [expanded, setExpanded] = useStateH(new Set());
  const [filter, setFilter] = useStateH('all');
  const [query, setQuery] = useStateH('');

  const { holdings, assetClasses, summary } = portfolioData;
  const clsMap = Object.fromEntries(assetClasses.map(a=>[a.key, a]));
  const total = summary.total_value || 1;

  const rows = useMemoH(()=>{
    return holdings
      .filter(h => !cls || h.cls === cls)
      .map(h => ({ ...h, weight: total > 0 ? (h.value / total) * 100 : 0 }))
      .filter(r => filter==='all' || (filter==='gain' ? r.gain_pct>=0 : r.gain_pct<0))
      .filter(r => !query || r.sym.toLowerCase().includes(query.toLowerCase()))
      .sort((a,b)=>{
        const v = sort.dir==='asc' ? 1 : -1;
        return (a[sort.k] > b[sort.k] ? 1 : -1) * v;
      });
  }, [sort, filter, query, holdings, cls, total]);

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

  return (
    <section className="card" style={{padding:0}}>
      <div style={{padding:'20px 20px 12px', display:'flex', alignItems:'center', justifyContent:'space-between', borderBottom:'1px solid var(--line)'}}>
        <div>
          <div className="card-title">Holdings · {rows.length} positions</div>
          <h2 className="serif" style={{fontSize:22, marginTop:4}}>{cls ? (clsMap[cls]?.name || cls) : 'All'} — <em className="mute">by current value</em></h2>
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
              <SortH k="gain_pct" num>%</SortH>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {rows.map(r=>{
              const ac = clsMap[r.cls] || { color:'#888' };
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
                    <td className={`num ${r.gain_pct>=0?'up':'down'}`}><b>{fmtPct(r.gain_pct)}</b></td>
                    <td style={{textAlign:'right', color:'var(--fg-mute)'}}>{isOpen?Ico.down:Ico.right}</td>
                  </tr>
                  {isOpen && r.accounts && (
                    <tr className="expand-row">
                      <td colSpan={10}>
                        <div className="expand-inner">
                          <div className="expand-grid expand-head">
                            <span>Account</span><span>Platform</span><span>Qty</span><span>Invested</span><span>P&L</span>
                          </div>
                          {r.accounts.map((a,i)=>(
                            <div key={i} className="expand-grid">
                              <span style={{color:'var(--fg)'}}>{a.account_name}</span>
                              <span>{a.platform}</span>
                              <span>{a.qty.toLocaleString('en-US',{maximumFractionDigits:4})}</span>
                              <span>{fmt(a.invested, sym)}</span>
                              <span className={a.gain>=0?'up':'down'}>{fmt(a.gain, sym)}</span>
                            </div>
                          ))}
                          <div style={{display:'flex', gap:8, marginTop:8}}>
                            <button className="fchip">Edit qty</button>
                            <button className="fchip">Add note</button>
                            <button className="fchip">View transactions</button>
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
