// Asset class detail page & other secondary pages
const { useState: useStateA } = React;

function AssetClassPage({ clsKey, currency, portfolioData }){
  const cls = portfolioData.assetClasses.find(a => a.key === clsKey);
  if (!cls) return <div className="content"><div className="mute" style={{padding:40}}>No data for this asset class.</div></div>;

  const sym = currency === 'INR' ? '₹' : '$';
  const [tab, setTab] = useStateA('holdings');

  const val = cls.value;
  const inv = cls.invested;
  const gain = cls.gain;
  const pct = cls.gain_pct;
  const sp = mkSpark(clsKey.length+3, 80, 0.025);

  const classTxns = portfolioData.transactions.filter(t => t.asset_class === cls.apiName);
  const classCash = portfolioData.cash.filter(c => c.asset_class === cls.apiName);

  return (
    <div className="content">
      <section className="hero" style={{gridTemplateColumns:'1.4fr 1fr'}}>
        <div className="hero-main">
          <div style={{display:'flex', alignItems:'center', gap:12}}>
            <div className="tkr-logo" style={{background:cls.color, color:'#0B0B0D', borderColor:cls.color, width:36, height:36, fontSize:18}}>{cls.icon}</div>
            <div>
              <div className="hero-label" style={{marginBottom:2}}>{cls.name}</div>
              <div className="mute" style={{fontSize:12}}>{cls.txns} transactions</div>
            </div>
          </div>
          <div className="hero-value serif" style={{fontSize:92, marginTop:24}}>
            <span className="cur">{sym}</span>{Math.floor(val).toLocaleString()}
            <span className="cents">.{((val%1).toFixed(2)).slice(2)}</span>
          </div>
          <div className="hero-delta">
            <span className={`chip ${pct>=0?'up':'down'}`}>{pct>=0?'▲':'▼'} {fmt(Math.abs(gain), sym)} ({fmtPct(pct)})</span>
            {cls.cagr_pct != null && <span className="chip">CAGR {cls.cagr_pct.toFixed(1)}%</span>}
            {cls.irr_pct != null && <span className="chip">IRR {cls.irr_pct.toFixed(1)}%</span>}
          </div>
          <div className="hero-spark">
            <Sparkline data={sp} color={cls.color} area={true}/>
          </div>
        </div>

        <div className="hero-side">
          <div className="stat"><div className="stat-l"><div className="stat-k">Invested</div><div className="stat-v">{fmt(inv, sym)}</div></div></div>
          <div className="stat"><div className="stat-l"><div className="stat-k">Current</div><div className="stat-v">{fmt(val, sym)}</div></div><span className={`stat-sub ${pct>=0?'up':'down'}`}>{fmtPct(pct)}</span></div>
          {cls.cash_reserves > 0 && <div className="stat"><div className="stat-l"><div className="stat-k">Cash held</div><div className="stat-v">{fmt(cls.cash_reserves, sym)}</div></div></div>}
          {cls.earliest_date && <div className="stat"><div className="stat-l"><div className="stat-k">Since</div><div className="stat-v" style={{fontSize:14}}>{cls.earliest_date}</div></div></div>}
        </div>
      </section>

      <section>
        <div className="section-head" style={{borderBottom:0, paddingBottom:0}}>
          <div className="chips">
            {['holdings','transactions','cash'].map(t=>(
              <button key={t} className={`fchip ${tab===t?'on':''}`} onClick={()=>setTab(t)}>
                {t==='holdings'?'Holdings':t==='transactions'?'Transactions':'Cash & Reserves'}
              </button>
            ))}
          </div>
          <div className="section-tools">
            <button className="btn">{Ico.refresh} Refresh prices</button>
            <button className="btn primary">{Ico.plus} Add transaction</button>
          </div>
        </div>
      </section>

      {tab==='holdings' && <HoldingsTable currency={currency} portfolioData={portfolioData} cls={clsKey}/>}

      {tab==='transactions' && (
        <section className="card">
          <div className="card-head">
            <div className="card-title">Transaction history · {classTxns.length} items</div>
          </div>
          <div style={{display:'flex', flexDirection:'column', gap:8}}>
            {classTxns.length === 0
              ? <div className="mute" style={{fontSize:13, padding:8}}>No transactions found.</div>
              : classTxns.map((t,i)=>(
                <div key={i} className="txn">
                  <span className="d">{t.investment_date}</span>
                  <span className="t">{t.notes || cls.name}</span>
                  <span className={`k ${t.type==='Withdrawal'?'sell':'buy'}`}>{t.type}</span>
                  <span className={`a ${t.type==='Withdrawal'?'down':'up'}`}>{t.type==='Withdrawal'?'-':'+'}{fmt(Math.abs(t.amount), sym, 0)}</span>
                </div>
              ))
            }
          </div>
        </section>
      )}

      {tab==='cash' && (
        <section className="card">
          <div className="card-head">
            <div className="card-title">Cash & reserves · available capital</div>
            <button className="btn">{Ico.plus} Add cash</button>
          </div>
          {classCash.length === 0
            ? <div className="mute" style={{fontSize:13, padding:8}}>No cash reserves for this class.</div>
            : <div className="grid-3">
                {classCash.map((c,i)=>(
                  <div key={i} className="panel" style={{padding:18}}>
                    <div className="card-title">{c.native_currency}</div>
                    <div className="serif" style={{fontSize:32, marginTop:8}}>{sym}{c.amount.toLocaleString('en-US',{maximumFractionDigits:0})}</div>
                    <div className="mute" style={{fontSize:11, marginTop:4}}>available for investment</div>
                  </div>
                ))}
              </div>
          }
        </section>
      )}
    </div>
  );
}

// ───────── Performance page ─────────
function PerformancePage({ currency, portfolioData }){
  const sym = currency === 'INR' ? '₹' : '$';
  const { summary, assetClasses } = portfolioData;
  const V = summary.total_value || 0;
  const I = summary.total_invested || 0;
  const G = summary.total_gain || 0;

  const sorted = assetClasses.slice().sort((a,b) => (b.cagr_pct||0) - (a.cagr_pct||0));
  const best = sorted[0];
  const worst = sorted[sorted.length - 1];

  return (
    <div className="content">
      <div className="section-head">
        <h2>Performance <em>analytics</em></h2>
        <div className="section-tools">
          <div className="chips">
            {['7D','30D','90D','1Y','5Y','ALL'].map(r=>(
              <button key={r} className={`fchip ${r==='1Y'?'on':''}`}>{r}</button>
            ))}
          </div>
        </div>
      </div>

      <section className="perf-hero">
        <div className="perf-card">
          {Ico.info}
          <div className="perf-k">Total Return</div>
          <div className={`perf-v ${G>=0?'up':'down'}`}>{fmtPct(summary.abs_return_pct || 0)}</div>
          <div className="perf-s">abs gain {fmt(Math.abs(G), sym)}</div>
        </div>
        <div className="perf-card">
          {Ico.info}
          <div className="perf-k">IRR · Money-weighted</div>
          <div className="perf-v">{summary.irr_pct != null ? summary.irr_pct.toFixed(1)+'%' : '—'}</div>
          <div className="perf-s">weighted by cash-flow timing</div>
        </div>
        <div className="perf-card">
          {Ico.info}
          <div className="perf-k">CAGR{summary.portfolio_years ? ' · '+summary.portfolio_years.toFixed(1)+' yrs' : ''}</div>
          <div className="perf-v">{summary.cagr_pct != null ? summary.cagr_pct.toFixed(1)+'%' : '—'}</div>
          <div className="perf-s">withdrawal-aware</div>
        </div>
        <div className="perf-card">
          {Ico.info}
          <div className="perf-k">Invested capital</div>
          <div className="perf-v">{fmt(I, sym)}</div>
          <div className="perf-s">{summary.portfolio_years ? summary.portfolio_years.toFixed(1)+' yrs invested' : ''}</div>
        </div>
      </section>

      <section className="grid-2">
        <div className="card">
          <div className="card-head">
            <div className="card-title">Stacked contribution · by asset class</div>
            <span className="mono mute" style={{fontSize:11}}>illustrative</span>
          </div>
          <div className="chart-frame" style={{height:280, display:'flex', alignItems:'flex-end', gap:2, padding:'10px 0'}}>
            {Array.from({length:48}).map((_,i)=>{
              const h = 30 + Math.sin(i*0.3)*20 + i*1.0;
              return (
                <div key={i} style={{flex:1, display:'flex', flexDirection:'column-reverse', gap:1, height:'100%', justifyContent:'flex-start'}}>
                  {assetClasses.map((a,j)=>(
                    <div key={j} style={{height:`${h*(0.1+j*0.05)}%`, background:a.color, opacity:0.85}}/>
                  ))}
                </div>
              );
            })}
          </div>
          <div style={{display:'flex', gap:14, marginTop:12, flexWrap:'wrap'}}>
            {assetClasses.map(a=>(
              <div key={a.key} style={{display:'flex', alignItems:'center', gap:6, fontSize:11, color:'var(--fg-dim)'}}>
                <span style={{width:10, height:10, background:a.color, borderRadius:2}}/>{a.name}
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="card-head">
            <div className="card-title">Waterfall · invested → gains → value</div>
          </div>
          <div className="wf">
            <div className="wf-col">
              <div className="bar-lbl">{fmt(I, sym)}</div>
              <div className="wf-bar" style={{height:'60%', background:'var(--fg-dim)'}}/>
              <div className="bar-k">Invested</div>
            </div>
            <div className="wf-col">
              <div className={`bar-lbl ${G>=0?'up':'down'}`}>{G>=0?'+':''}{fmt(G, sym)}</div>
              <div className="wf-bar" style={{height:'22%', background: G>=0 ? 'var(--lime)' : 'var(--loss)', marginTop:'60%', transform:'translateY(-100%)'}}/>
              <div className="bar-k">Unrealised gain</div>
            </div>
            <div className="wf-col">
              <div className="bar-lbl">{fmt(V, sym)}</div>
              <div className="wf-bar" style={{height:'76%', background:'var(--lime)'}}/>
              <div className="bar-k">Current value</div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid-2">
        <div className="card">
          <div className="card-head"><div className="card-title">Best performer · CAGR</div></div>
          {best && <div style={{display:'flex', alignItems:'center', gap:14}}>
            <div className="tkr-logo" style={{background:best.color, color:'#0B0B0D', borderColor:best.color, width:40, height:40, fontSize:18}}>{best.icon}</div>
            <div>
              <div style={{fontSize:14}}>{best.name}</div>
              <div className="serif up" style={{fontSize:36, letterSpacing:'-.02em'}}>{fmtPct(best.cagr_pct || 0)}</div>
            </div>
          </div>}
        </div>
        <div className="card">
          <div className="card-head"><div className="card-title">Laggard · CAGR</div></div>
          {worst && <div style={{display:'flex', alignItems:'center', gap:14}}>
            <div className="tkr-logo" style={{background:worst.color, color:'#0B0B0D', borderColor:worst.color, width:40, height:40, fontSize:18}}>{worst.icon}</div>
            <div>
              <div style={{fontSize:14}}>{worst.name}</div>
              <div className={`serif ${(worst.cagr_pct||0)>=0?'up':'down'}`} style={{fontSize:36, letterSpacing:'-.02em'}}>{fmtPct(worst.cagr_pct || 0)}</div>
            </div>
          </div>}
        </div>
      </section>

      <section className="card">
        <div className="card-head"><div className="card-title">Asset class breakdown</div></div>
        <table className="hold">
          <thead>
            <tr>
              <th>Asset class</th>
              <th className="num">Invested</th>
              <th className="num">Value</th>
              <th className="num">Gain</th>
              <th className="num">IRR</th>
              <th className="num">CAGR</th>
              <th className="num">Txns</th>
            </tr>
          </thead>
          <tbody>
            {assetClasses.map(a=>(
              <tr key={a.key}>
                <td>
                  <div className="tkr">
                    <div className="tkr-logo" style={{background:a.color+'22', color:a.color, borderColor:a.color+'44'}}>{a.icon}</div>
                    <div className="tkr-name"><b>{a.name}</b><span>{a.txns} transactions</span></div>
                  </div>
                </td>
                <td className="num mute">{fmt(a.invested, sym)}</td>
                <td className="num">{fmt(a.value, sym)}</td>
                <td className={`num ${a.gain>=0?'up':'down'}`}>{fmt(a.gain, sym)}</td>
                <td className="num">{a.irr_pct != null ? a.irr_pct.toFixed(1)+'%' : '—'}</td>
                <td className="num">{a.cagr_pct != null ? a.cagr_pct.toFixed(1)+'%' : '—'}</td>
                <td className="num mute">{a.txns}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}

// ───────── Connections page ─────────
function ConnectionsPage(){
  const conns = [
    ['V','Vested','US Market · broker','on','2 min ago'],
    ['I','INDmoney','US Market · broker','on','12 min ago'],
    ['Z','Zerodha Primary','Indian Stocks · Kite API','on','4 min ago'],
    ['Z','Zerodha Secondary','Indian Stocks · Kite API','off','2 days ago'],
    ['P','Paytm Money','Mutual Funds · Google Sheet','on','1 hr ago'],
    ['C','Coin by Zerodha','Mutual Funds · Kite API','on','16 min ago'],
    ['B','Binance','Crypto · API','on','6 min ago'],
    ['G','Google Sheets','Lending · manual','on','Yesterday'],
  ];
  return (
    <div className="content">
      <div className="section-head">
        <h2>Connections <em>& sync</em></h2>
        <button className="btn primary">{Ico.plus} Add account</button>
      </div>
      <section style={{display:'flex', flexDirection:'column', gap:10}}>
        {conns.map((c,i)=>(
          <div key={i} className="conn-row">
            <div className="conn-logo">{c[0]}</div>
            <div className="conn-name"><b>{c[1]}</b><span>{c[2]}</span></div>
            <span className={`conn-status ${c[3]==='off'?'off':''}`}><span className="d"/>{c[3]==='off'?'Disconnected':'Connected'}</span>
            <span className="conn-last">synced {c[4]}</span>
            <div style={{display:'flex', gap:6}}>
              <button className="fchip">Sync now</button>
              <button className="fchip">Edit</button>
            </div>
          </div>
        ))}
      </section>
    </div>
  );
}

function SettingsPage(){
  return (
    <div className="content">
      <div className="section-head"><h2>Settings <em>& preferences</em></h2></div>
      <section className="grid-2">
        <div className="card">
          <div className="card-title">Display</div>
          <div style={{display:'flex', flexDirection:'column', gap:14, marginTop:14}}>
            <div className="kv"><span>Preferred currency</span><span>INR (₹)</span></div>
            <div className="kv"><span>USD/INR source</span><span>exchangerate.host</span></div>
            <div className="kv"><span>Auto-refresh</span><span>15 min</span></div>
            <div className="kv"><span>Theme</span><span>Dark · Ember</span></div>
            <div className="kv"><span>Number format</span><span>Indian · lakhs/crore</span></div>
          </div>
        </div>
        <div className="card">
          <div className="card-title">Notifications</div>
          <div style={{display:'flex', flexDirection:'column', gap:14, marginTop:14}}>
            <div className="kv"><span>Price alerts</span><span className="up">On</span></div>
            <div className="kv"><span>Performance milestones</span><span className="up">On</span></div>
            <div className="kv"><span>Weekly digest</span><span className="mute">Off</span></div>
            <div className="kv"><span>Withdrawal confirmations</span><span className="up">On</span></div>
          </div>
        </div>
      </section>
      <section className="card">
        <div className="card-title">Data export</div>
        <div style={{display:'flex', gap:10, marginTop:14}}>
          <button className="btn">Export CSV</button>
          <button className="btn">Export PDF report</button>
          <button className="btn">Download full database</button>
        </div>
      </section>
    </div>
  );
}

Object.assign(window, { AssetClassPage, PerformancePage, ConnectionsPage, SettingsPage });
