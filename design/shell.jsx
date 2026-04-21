// Shared components, data, icons
const { useState, useEffect, useMemo, useRef } = React;

// ───────── ICONS (stroke 1.5, 16×16) ─────────
const Ico = {
  home:  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="nav-ico"><path d="M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-7h-6v7H4a1 1 0 0 1-1-1z"/></svg>,
  us:    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="nav-ico"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 10h18"/></svg>,
  ind:   <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="nav-ico"><path d="M3 3v18h18"/><path d="M7 15l4-4 3 3 6-7"/></svg>,
  mf:    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="nav-ico"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/></svg>,
  crypto:<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="nav-ico"><path d="M12 2 22 7v10L12 22 2 17V7z"/><path d="M12 2v20M2 7l10 5 10-5M2 17l10-5 10 5"/></svg>,
  lend:  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="nav-ico"><path d="M4 7h16M6 7v12a1 1 0 0 0 1 1h10a1 1 0 0 0 1-1V7"/><path d="M9 7V5a3 3 0 0 1 6 0v2"/></svg>,
  perf:  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="nav-ico"><path d="M3 17l5-5 4 4 8-9"/><path d="M14 7h6v6"/></svg>,
  conn:  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="nav-ico"><path d="M10 13a5 5 0 0 0 7 0l3-3a5 5 0 0 0-7-7l-1 1"/><path d="M14 11a5 5 0 0 0-7 0l-3 3a5 5 0 0 0 7 7l1-1"/></svg>,
  set:   <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="nav-ico"><circle cx="12" cy="12" r="3"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>,
  refresh: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" width="14" height="14"><path d="M4 4v6h6M20 20v-6h-6"/><path d="M20 10A8 8 0 0 0 6 6l-2 2M4 14a8 8 0 0 0 14 4l2-2"/></svg>,
  plus:  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="14" height="14"><path d="M12 5v14M5 12h14"/></svg>,
  search:<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" width="14" height="14"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>,
  bell:  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" width="14" height="14"><path d="M6 8a6 6 0 1 1 12 0v5l2 3H4l2-3zM10 19a2 2 0 0 0 4 0"/></svg>,
  info:  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" width="16" height="16" className="perf-ico"><circle cx="12" cy="12" r="9"/><path d="M12 8h.01M11 12h1v5"/></svg>,
  down:  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" width="10" height="10"><path d="m6 9 6 6 6-6"/></svg>,
  right: <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" width="10" height="10"><path d="m9 18 6-6-6-6"/></svg>,
};

// ───────── DATA ─────────
const ASSET_CLASSES = [
  { key:'us',     name:'US Market',      color:'#C7F651', icon:'$', cagr:18.4,
    value: 62340, invested: 48200, txns: 24 },
  { key:'ind',    name:'Indian Stocks',  color:'#D9C78B', icon:'₹', cagr:22.1,
    value: 91200, invested: 68400, txns: 37 },
  { key:'mf',     name:'Mutual Funds',   color:'#8BB8D8', icon:'M', cagr:14.6,
    value: 54100, invested: 44800, txns: 18 },
  { key:'crypto', name:'Crypto',         color:'#E89B8B', icon:'₿', cagr:31.2,
    value: 28450, invested: 19300, txns: 12 },
  { key:'lend',   name:'Lending',        color:'#A78BE8', icon:'L', cagr:10.8,
    value: 12700, invested: 12000, txns:  5 },
];

const HOLDINGS = [
  { sym:'AAPL',  name:'Apple Inc.',              cls:'us',    qty:42,   avg:142.10, price:192.30, cur:'USD' },
  { sym:'NVDA',  name:'NVIDIA Corp.',            cls:'us',    qty:18,   avg:221.40, price:864.20, cur:'USD' },
  { sym:'MSFT',  name:'Microsoft Corp.',         cls:'us',    qty:22,   avg:286.00, price:412.10, cur:'USD' },
  { sym:'GOOGL', name:'Alphabet Inc. Class A',   cls:'us',    qty:30,   avg:128.50, price:162.80, cur:'USD' },
  { sym:'TSLA',  name:'Tesla Inc.',              cls:'us',    qty:12,   avg:244.00, price:218.50, cur:'USD' },
  { sym:'RELIANCE', name:'Reliance Industries',  cls:'ind',   qty:120,  avg:2280,   price:2945,   cur:'INR' },
  { sym:'TCS',   name:'Tata Consultancy',        cls:'ind',   qty:54,   avg:3320,   price:3860,   cur:'INR' },
  { sym:'HDFCBANK', name:'HDFC Bank',            cls:'ind',   qty:88,   avg:1540,   price:1682,   cur:'INR' },
  { sym:'INFY',  name:'Infosys Ltd.',            cls:'ind',   qty:96,   avg:1410,   price:1548,   cur:'INR' },
  { sym:'PARAG',  name:'Parag Parikh Flexi Cap', cls:'mf',    qty:412,  avg:54.20,  price:78.10,  cur:'INR' },
  { sym:'AXIS',  name:'Axis Bluechip Direct',    cls:'mf',    qty:720,  avg:42.10,  price:51.30,  cur:'INR' },
  { sym:'BTC',   name:'Bitcoin',                 cls:'crypto',qty:0.22, avg:42000,  price:68400,  cur:'USD' },
  { sym:'ETH',   name:'Ethereum',                cls:'crypto',qty:3.4,  avg:2100,   price:3250,   cur:'USD' },
  { sym:'SOL',   name:'Solana',                  cls:'crypto',qty:42,   avg:88,     price:142,    cur:'USD' },
  { sym:'P2P',   name:'P2P Lending Pool A',      cls:'lend',  qty:1,    avg:8000,   price:8640,   cur:'USD' },
];

// Generate sparkline-friendly values
function mkSpark(seed, n=28, vol=0.04){
  let v=100, out=[];
  for(let i=0;i<n;i++){
    const s = Math.sin(i*0.6+seed)*vol + (Math.cos(i*0.27+seed*2)*vol*0.7);
    v *= 1 + s;
    out.push(v);
  }
  return out;
}
const ALL_SPARK = mkSpark(2, 36, 0.025);

// portfolio time series for hero
function mkSeries(n=120){
  const out=[]; let v=60000;
  for(let i=0;i<n;i++){
    v *= 1 + (Math.sin(i*0.18)*0.01) + (Math.random()-0.48)*0.012;
    out.push({ t:i, v });
  }
  return out;
}
const SERIES = mkSeries();

// ───────── helpers ─────────
const fmt = (n, sym='$', d=0) => (n<0?'-':'') + sym + Math.abs(n).toLocaleString('en-US',{minimumFractionDigits:d,maximumFractionDigits:d});
const fmtPct = (n, d=2) => (n>=0?'+':'') + n.toFixed(d) + '%';

function totals() {
  const invested = ASSET_CLASSES.reduce((s,a)=>s+a.invested,0);
  const value = ASSET_CLASSES.reduce((s,a)=>s+a.value,0);
  return { invested, value, gain: value-invested, pct: (value-invested)/invested*100 };
}

// ───────── Sparkline SVG ─────────
function Sparkline({ data, color='currentColor', fill=false, className='', area=true, height=40, stroke=1.5 }){
  const w = 400, h = 100;
  const min = Math.min(...data), max = Math.max(...data);
  const span = max-min || 1;
  const pts = data.map((v,i)=>[i/(data.length-1)*w, h - ((v-min)/span)*h]);
  const path = pts.map((p,i)=>(i?'L':'M')+p[0].toFixed(1)+' '+p[1].toFixed(1)).join(' ');
  const areaPath = path + ` L ${w} ${h} L 0 ${h} Z`;
  return (
    <svg className={`spark ${className}`} viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" style={{height}}>
      {area && <path d={areaPath} fill={color} opacity=".08"/>}
      <path d={path} fill="none" stroke={color} strokeWidth={stroke} vectorEffect="non-scaling-stroke"/>
    </svg>
  );
}

// ───────── Shell components ─────────
function Sidebar({ route, setRoute }){
  const items = [
    { key:'home',   label:'Net Worth',        ico:Ico.home, hash:'#/' },
    { key:'us',     label:'US Market',        ico:Ico.us,   hash:'#/us'     , badge:'24' },
    { key:'ind',    label:'Indian Stocks',    ico:Ico.ind,  hash:'#/ind'    , badge:'37' },
    { key:'mf',     label:'Mutual Funds',     ico:Ico.mf,   hash:'#/mf'     , badge:'18' },
    { key:'crypto', label:'Crypto',           ico:Ico.crypto,hash:'#/crypto', badge:'12' },
    { key:'lend',   label:'Lending',          ico:Ico.lend, hash:'#/lend'    , badge:'05' },
  ];
  const tools = [
    { key:'perf', label:'Performance', ico:Ico.perf, hash:'#/performance' },
    { key:'conn', label:'Connections', ico:Ico.conn, hash:'#/connections' },
    { key:'set',  label:'Settings',    ico:Ico.set,  hash:'#/settings' },
  ];
  return (
    <aside className="side">
      <div className="brand">
        <div className="brand-mark">Ø</div>
        <div>
          <div className="brand-name">Orbit</div>
          <div className="brand-sub">Portfolio · 2026</div>
        </div>
      </div>

      <div className="nav-group">
        <div className="nav-label">Overview</div>
        <nav className="nav">
          {items.slice(0,1).map(i=>(
            <a key={i.key} href={i.hash} className={route===i.key?'active':''} onClick={()=>setRoute(i.key)}>
              {i.ico}<span>{i.label}</span>
            </a>
          ))}
        </nav>
      </div>

      <div className="nav-group">
        <div className="nav-label">Asset classes</div>
        <nav className="nav">
          {items.slice(1).map(i=>(
            <a key={i.key} href={i.hash} className={route===i.key?'active':''} onClick={()=>setRoute(i.key)}>
              {i.ico}<span>{i.label}</span>
              {i.badge && <span className="nav-badge mono">{i.badge}</span>}
            </a>
          ))}
        </nav>
      </div>

      <div className="nav-group">
        <div className="nav-label">Analytics</div>
        <nav className="nav">
          {tools.map(i=>(
            <a key={i.key} href={i.hash} className={route===i.key?'active':''} onClick={()=>setRoute(i.key)}>
              {i.ico}<span>{i.label}</span>
            </a>
          ))}
        </nav>
      </div>

      <div className="side-foot">
        <div className="account-chip">
          <div className="avatar">A</div>
          <div className="account-meta">
            <b>Aditya K.</b>
            <span>5 accounts · synced</span>
          </div>
        </div>
      </div>
    </aside>
  );
}

function TopBar({ crumbs, currency, setCurrency }){
  return (
    <>
    <div className="topbar">
      <div className="crumbs">
        {crumbs.map((c,i)=>(
          <React.Fragment key={i}>
            {i>0 && <span className="crumb-sep">/</span>}
            {i===crumbs.length-1 ? <b>{c}</b> : <span>{c}</span>}
          </React.Fragment>
        ))}
      </div>
      <div className="top-actions">
        <div className="pill"><span className="dot"/>Markets open · live</div>
        <div className="search">
          {Ico.search}
          <input placeholder="Search ticker, transaction, note…" />
          <span className="mono faint" style={{fontSize:10}}>⌘K</span>
        </div>
        <div className="toggle">
          <button className={currency==='USD'?'on':''} onClick={()=>setCurrency('USD')}>USD</button>
          <button className={currency==='INR'?'on':''} onClick={()=>setCurrency('INR')}>INR</button>
        </div>
        <button className="btn">{Ico.refresh} Sync</button>
        <button className="btn primary">{Ico.plus} Add</button>
      </div>
    </div>
    <Ticker/>
    </>
  );
}

function Ticker(){
  const items = [
    ['NIFTY', '22,451.20', '+0.82%', true],
    ['SENSEX', '74,012.05', '+0.61%', true],
    ['S&P 500', '5,218.44', '-0.14%', false],
    ['NASDAQ', '16,302.76', '+0.22%', true],
    ['BTC', '$68,412', '+2.14%', true],
    ['ETH', '$3,254', '+1.05%', true],
    ['USD/INR', '83.42', '-0.04%', false],
    ['GOLD', '$2,338', '+0.41%', true],
    ['10Y-IN', '7.18%', '-0.02', false],
    ['OIL', '$82.10', '+0.55%', true],
  ];
  const Row = () => items.map(([t,p,c,up],i)=>(
    <div key={i} className="ticker-item">
      <b>{t}</b><span>{p}</span><span className={up?'up':'down'}>{c}</span>
    </div>
  ));
  return (
    <div className="ticker">
      <div className="ticker-track">
        <Row/><Row/><Row/>
      </div>
    </div>
  );
}

// expose
Object.assign(window, {
  React, Ico, ASSET_CLASSES, HOLDINGS, SERIES, ALL_SPARK,
  fmt, fmtPct, totals, mkSpark,
  Sparkline, Sidebar, TopBar, Ticker
});
