// Asset class detail page & other secondary pages
const { useState: useStateA } = React;

function AssetClassPage({ clsKey, currency }){
  const cls = ASSET_CLASSES.find(a=>a.key===clsKey);
  const sym = currency === 'INR' ? '₹' : '$';
  const rate = currency === 'INR' ? 83.42 : 1;
  const [tab, setTab] = useStateA('holdings');

  const val = cls.value * rate;
  const inv = cls.invested * rate;
  const gain = val - inv;
  const pct = gain/inv*100;

  const sp = mkSpark(clsKey.length+3, 80, 0.025);

  return (
    <div className="content">
      <section className="hero" style={{gridTemplateColumns:'1.4fr 1fr'}}>
        <div className="hero-main">
          <div style={{display:'flex', alignItems:'center', gap:12}}>
            <div className="tkr-logo" style={{background:cls.color, color:'#0B0B0D', borderColor:cls.color, width:36, height:36, fontSize:18}}>{cls.icon}</div>
            <div>
              <div className="hero-label" style={{marginBottom:2}}>{cls.name}</div>
              <div className="mute" style={{fontSize:12}}>{cls.txns} transactions · {cls.key==='us'?2:cls.key==='ind'?3:1} accounts</div>
            </div>
          </div>
          <div className="hero-value serif" style={{fontSize:92, marginTop:24}}>
            <span className="cur">{sym}</span>{Math.floor(val).toLocaleString()}
            <span className="cents">.{((val%1).toFixed(2)).slice(2)}</span>
          </div>
          <div className="hero-delta">
            <span className={`chip ${pct>=0?'up':'down'}`}>{pct>=0?'▲':'▼'} {fmt(gain, sym)} ({fmtPct(pct)})</span>
            <span className="chip">CAGR {cls.cagr.toFixed(1)}%</span>
            <span className="chip">IRR {(cls.cagr+2.4).toFixed(1)}%</span>
          </div>
          <div className="hero-spark">
            <Sparkline data={sp} color={cls.color} area={true}/>
          </div>
        </div>

        <div className="hero-side">
          <div className="stat"><div className="stat-l"><div className="stat-k">Invested</div><div className="stat-v">{fmt(inv, sym)}</div></div></div>
          <div className="stat"><div className="stat-l"><div className="stat-k">Current</div><div className="stat-v">{fmt(val, sym)}</div></div><span className={`stat-sub ${pct>=0?'up':'down'}`}>{fmtPct(pct)}</span></div>
          <div className="stat"><div className="stat-l"><div className="stat-k">Cash held</div><div className="stat-v">{fmt(2400*rate, sym)}</div></div><span className="stat-sub mute">{cls.key==='us'?'USD':'INR'}</span></div>
          <div className="stat"><div className="stat-l"><div className="stat-k">Last sync</div><div className="stat-v" style={{fontSize:14}}>4 min ago</div></div><button className="btn" style={{fontSize:11}}>{Ico.refresh} Sync</button></div>
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

      {tab==='holdings' && <HoldingsTable currency={currency} cls={clsKey}/>}

      {tab==='transactions' && (
        <section className="card">
          <div className="card-head">
            <div className="card-title">Transaction history · {cls.txns} items</div>
            <div className="chips">
              <button className="fchip on">All</button>
              <button className="fchip">Buy</button>
              <button className="fchip">Sell</button>
              <button className="fchip">Dividend</button>
            </div>
          </div>
          <div style={{display:'flex', flexDirection:'column', gap:8}}>
            {[
              ['2026-04-12', 'Buy', 'AAPL · 5 units @ $192.30', 961.50, 'buy'],
              ['2026-04-02', 'Buy', 'NVDA · 2 units @ $864.20', 1728.40, 'buy'],
              ['2026-03-28', 'Dividend', 'MSFT · quarterly', 48.20, 'div'],
              ['2026-03-14', 'Sell', 'TSLA · 4 units @ $218.50', 874.00, 'sell'],
              ['2026-02-22', 'Buy', 'GOOGL · 10 units @ $162.80', 1628.00, 'buy'],
              ['2026-02-08', 'Buy', 'AAPL · 12 units @ $188.10', 2257.20, 'buy'],
              ['2026-01-18', 'Dividend', 'AAPL · quarterly', 28.40, 'div'],
            ].map((t,i)=>(
              <div key={i} className="txn">
                <span className="d">{t[0]}</span>
                <span className="t">{t[2]}</span>
                <span className={`k ${t[4]}`}>{t[1]}</span>
                <span className={`a ${t[4]==='sell'?'down':t[4]==='buy'?'':'up'}`}>{t[4]==='sell'?'-':t[4]==='div'?'+':''}{fmt(t[3]*rate, sym, 2)}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      {tab==='cash' && (
        <section className="card">
          <div className="card-head">
            <div className="card-title">Cash & reserves · available capital</div>
            <button className="btn">{Ico.plus} Add cash</button>
          </div>
          <div className="grid-3">
            {[['USD',2400],['INR',180000],['Pending settlement',420]].map((c,i)=>(
              <div key={i} className="panel" style={{padding:18}}>
                <div className="card-title">{c[0]}</div>
                <div className="serif" style={{fontSize:32, marginTop:8}}>{c[0]==='INR'?'₹':c[0]==='USD'?'$':sym}{c[1].toLocaleString()}</div>
                <div className="mute" style={{fontSize:11, marginTop:4}}>available for investment</div>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

// ───────── Performance page ─────────
function PerformancePage({ currency }){
  const sym = currency === 'INR' ? '₹' : '$';
  const rate = currency === 'INR' ? 83.42 : 1;
  const T = totals();
  const best = ASSET_CLASSES.slice().sort((a,b)=>b.cagr-a.cagr)[0];
  const worst = ASSET_CLASSES.slice().sort((a,b)=>a.cagr-b.cagr)[0];

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
          <div className="perf-v up">{fmtPct(T.pct)}</div>
          <div className="perf-s">abs gain {fmt(T.gain*rate, sym)}</div>
        </div>
        <div className="perf-card">
          {Ico.info}
          <div className="perf-k">IRR · Money-weighted</div>
          <div className="perf-v">21.8%</div>
          <div className="perf-s">weighted by cash-flow timing</div>
        </div>
        <div className="perf-card">
          {Ico.info}
          <div className="perf-k">CAGR · 3.2 yrs</div>
          <div className="perf-v">19.4%</div>
          <div className="perf-s">withdrawal-aware</div>
        </div>
        <div className="perf-card">
          {Ico.info}
          <div className="perf-k">Sharpe · est.</div>
          <div className="perf-v">1.42</div>
          <div className="perf-s">risk-adjusted return</div>
        </div>
      </section>

      <section className="grid-2">
        <div className="card">
          <div className="card-head">
            <div className="card-title">Stacked contribution · capital over time</div>
            <span className="mono mute" style={{fontSize:11}}>last 12 months</span>
          </div>
          <div className="chart-frame" style={{height:280, display:'flex', alignItems:'flex-end', gap:2, padding:'10px 0'}}>
            {Array.from({length:48}).map((_,i)=>{
              const h = 30 + Math.sin(i*0.3)*20 + i*1.0;
              return (
                <div key={i} style={{flex:1, display:'flex', flexDirection:'column-reverse', gap:1, height:'100%', justifyContent:'flex-start'}}>
                  {ASSET_CLASSES.map((a,j)=>(
                    <div key={j} style={{height:`${h*(0.1+j*0.05)}%`, background:a.color, opacity:0.85}}/>
                  ))}
                </div>
              );
            })}
          </div>
          <div style={{display:'flex', gap:14, marginTop:12, flexWrap:'wrap'}}>
            {ASSET_CLASSES.map(a=>(
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
              <div className="bar-lbl">{fmt(T.invested*rate, sym)}</div>
              <div className="wf-bar" style={{height:'60%', background:'var(--fg-dim)'}}/>
              <div className="bar-k">Invested</div>
            </div>
            <div className="wf-col">
              <div className="bar-lbl up">+{fmt(T.gain*rate, sym)}</div>
              <div className="wf-bar" style={{height:'22%', background:'var(--lime)', marginTop:'60%', transform:'translateY(-100%)'}}/>
              <div className="bar-k">Realised + unrealised</div>
            </div>
            <div className="wf-col">
              <div className="bar-lbl">-{fmt(8200*rate, sym)}</div>
              <div className="wf-bar" style={{height:'6%', background:'var(--loss)'}}/>
              <div className="bar-k">Withdrawals</div>
            </div>
            <div className="wf-col">
              <div className="bar-lbl">{fmt(T.value*rate, sym)}</div>
              <div className="wf-bar" style={{height:'76%', background:'var(--lime)'}}/>
              <div className="bar-k">Current value</div>
            </div>
          </div>
        </div>
      </section>

      <section className="grid-2">
        <div className="card">
          <div className="card-head">
            <div className="card-title">Best performer</div>
          </div>
          <div style={{display:'flex', alignItems:'center', gap:14}}>
            <div className="tkr-logo" style={{background:best.color, color:'#0B0B0D', borderColor:best.color, width:40, height:40, fontSize:18}}>{best.icon}</div>
            <div>
              <div style={{fontSize:14}}>{best.name}</div>
              <div className="serif up" style={{fontSize:36, letterSpacing:'-.02em'}}>+{best.cagr.toFixed(1)}%</div>
            </div>
          </div>
        </div>
        <div className="card">
          <div className="card-head">
            <div className="card-title">Laggard</div>
          </div>
          <div style={{display:'flex', alignItems:'center', gap:14}}>
            <div className="tkr-logo" style={{background:worst.color, color:'#0B0B0D', borderColor:worst.color, width:40, height:40, fontSize:18}}>{worst.icon}</div>
            <div>
              <div style={{fontSize:14}}>{worst.name}</div>
              <div className="serif" style={{fontSize:36, letterSpacing:'-.02em'}}>+{worst.cagr.toFixed(1)}%</div>
            </div>
          </div>
        </div>
      </section>

      <section className="card">
        <div className="card-head">
          <div className="card-title">Asset class breakdown</div>
        </div>
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
            {ASSET_CLASSES.map(a=>{
              const g = (a.value-a.invested)*rate;
              const p = (a.value-a.invested)/a.invested*100;
              return (
                <tr key={a.key}>
                  <td>
                    <div className="tkr">
                      <div className="tkr-logo" style={{background:a.color+'22', color:a.color, borderColor:a.color+'44'}}>{a.icon}</div>
                      <div className="tkr-name"><b>{a.name}</b><span>{a.txns} transactions</span></div>
                    </div>
                  </td>
                  <td className="num mute">{fmt(a.invested*rate, sym)}</td>
                  <td className="num">{fmt(a.value*rate, sym)}</td>
                  <td className={`num ${g>=0?'up':'down'}`}>{fmt(g, sym)}</td>
                  <td className="num">{(a.cagr+2).toFixed(1)}%</td>
                  <td className="num">{a.cagr.toFixed(1)}%</td>
                  <td className="num mute">{a.txns}</td>
                </tr>
              );
            })}
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
