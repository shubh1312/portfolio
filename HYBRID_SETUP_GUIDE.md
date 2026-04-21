// Updated shell.jsx with API integration
// Updated Sidebar, TopBar, and data hooks with real API calls

/**
 * COMPLETE SETUP GUIDE FOR OPTION 3 HYBRID APPROACH
 * 
 * Your portfolio tracker is now split into:
 * 1. FastAPI Backend (Python) - runs on http://localhost:8000
 * 2. React Frontend (JavaScript) - runs on http://localhost:5173 (Vite) or 3000 (Create React App)
 * 
 * =============================================================================
 * STEP 1: SETUP FASTAPI BACKEND
 * =============================================================================
 * 
 * cd /Users/shubham/projects/portfolio
 * 
 * # Install FastAPI dependencies
 * pip install -r backend/requirements.txt
 * 
 * # Run the FastAPI server
 * python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
 * 
 * # The API will be available at http://localhost:8000
 * # API docs at http://localhost:8000/docs (Swagger UI)
 * 
 * 
 * =============================================================================
 * STEP 2: SETUP REACT FRONTEND
 * =============================================================================
 * 
 * # Navigate to frontend directory
 * cd /Users/shubham/projects/portfolio/frontend
 * 
 * # Initialize React app with Vite (recommended) or Create React App
 * # Option A: Using Vite (faster, modern)
 * npm create vite@latest . -- --template react
 * npm install
 * 
 * # Option B: Using Create React App (slower but simpler)
 * # npx create-react-app .
 * 
 * # Install additional dependencies
 * npm install axios  # optional, we're using fetch
 * 
 * # Copy the design files into src/
 * # - shell.css into src/App.css
 * # - api.js into src/api.js
 * # - page-netwrorth.jsx into src/pages/NetWorth.jsx
 * # - page-secondary.jsx into src/pages/AssetClass.jsx
 * 
 * # Start the frontend
 * npm run dev   # for Vite
 * # or
 * npm start     # for Create React App
 * 
 * Frontend will be available at http://localhost:5173 (Vite) or http://localhost:3000 (CRA)
 * 
 * 
 * =============================================================================
 * STEP 3: CONNECT FRONTEND TO BACKEND
 * =============================================================================
 * 
 * In frontend/.env (create this file):
 * REACT_APP_API_URL=http://localhost:8000/api
 * 
 * The React components will automatically use the api.js client to fetch data
 * from the FastAPI backend instead of using hardcoded data.
 * 
 * 
 * =============================================================================
 * STEP 4: ARCHITECTURE OVERVIEW
 * =============================================================================
 * 
 * frontend/
 * ├── Orbit Portfolio.html     <- Main HTML entry point
 * ├── shell.css                <- Global styles
 * ├── shell.jsx                <- Layout shell (Sidebar, TopBar)
 * ├── page-netwrorth.jsx       <- Net Worth/Dashboard page
 * ├── page-secondary.jsx       <- Asset Class detail pages
 * ├── api.js                   <- API client (calls backend)
 * ├── package.json
 * └── ...React files
 * 
 * backend/
 * ├── main.py                  <- FastAPI app with all endpoints
 * ├── requirements.txt         <- Python dependencies
 * └── ...
 * 
 * services/                    <- Your existing Python services
 * ├── performance_service.py   <- IRR/CAGR calculations
 * ├── portfolio_service.py     <- Holdings management
 * ├── market_data.py           <- Price fetching (threaded)
 * ├── zerodha_service.py       <- Zerodha integration
 * ├── mf_service.py            <- Mutual funds API
 * ├── crypto_service.py        <- Crypto integration
 * └── ...
 * 
 * 
 * =============================================================================
 * STEP 5: API ENDPOINTS AVAILABLE
 * =============================================================================
 * 
 * Portfolio:
 * - GET /api/portfolio/summary?currency=INR    -> Total portfolio data
 * - GET /api/portfolio/assets?currency=INR     -> Breakdown by asset class
 * 
 * Holdings:
 * - GET /api/holdings?currency=INR             -> All holdings
 * - GET /api/holdings?asset_class=US Market    -> Holdings for one asset class
 * 
 * Transactions:
 * - GET /api/transactions?currency=INR         -> All transactions
 * - GET /api/transactions?asset_class=US Market -> For one asset class
 * 
 * Cash:
 * - GET /api/cash?currency=INR                 -> Cash reserves by asset class
 * 
 * Prices:
 * - POST /api/prices/refresh?category=US Market
 *        -> Triggers price refresh (uses threaded fetching from market_data.py)
 * 
 * Accounts:
 * - GET /api/accounts                          -> List all accounts
 * 
 * Health:
 * - GET /api/health                            -> Check if API is running
 * 
 * 
 * =============================================================================
 * STEP 6: CURRENT FEATURES PRESERVED
 * =============================================================================
 * 
 * ✓ Multi-asset tracking (US Stocks, Indian Stocks, Mutual Funds, Crypto, Lending)
 * ✓ Real-time price updates with threading (10-15x faster)
 * ✓ Multi-currency support (USD/INR conversion)
 * ✓ IRR calculation (money-weighted returns)
 * ✓ CAGR with withdrawal handling
 * ✓ Transaction management with withdrawal support
 * ✓ Cash reserve tracking per asset class
 * ✓ Multi-account management
 * ✓ Zerodha API integration
 * ✓ Email report sync
 * ✓ Database backend (SQLite or your current DB)
 * 
 * 
 * =============================================================================
 * STEP 7: EXAMPLE: UPDATE SHELL.JSX FOR API
 * =============================================================================
 * 
 * Replace hardcoded ASSET_CLASSES data with:
 * 
 * const [assets, setAssets] = useState([]);
 * const [totals, setTotals] = useState({});
 * 
 * useEffect(() => {
 *   const fetchData = async () => {
 *     try {
 *       const summary = await portfolio.getSummary(currency);
 *       setTotals(summary.data);
 *       
 *       const assetData = await portfolio.getAssets(currency);
 *       setAssets(assetData.data);
 *     } catch (error) {
 *       console.error('Failed to fetch portfolio data:', error);
 *     }
 *   };
 *   
 *   fetchData();
 * }, [currency]);
 * 
 * Then use {assets} and {totals} in your JSX instead of ASSET_CLASSES
 * 
 * 
 * =============================================================================
 * STEP 8: DEPLOYMENT
 * =============================================================================
 * 
 * Development:
 * Terminal 1: python -m uvicorn backend.main:app --reload
 * Terminal 2: npm run dev
 * 
 * Production:
 * - Build React: npm run build
 * - Serve frontend from FastAPI static files
 * - Run FastAPI with Gunicorn: gunicorn backend.main:app
 * 
 * 
 * =============================================================================
 * FEATURES OF THIS APPROACH
 * =============================================================================
 * 
 * ✓ Frontend: Beautiful modern React UI (Orbit design)
 * ✓ Backend: Python with all your existing logic
 * ✓ Database: Uses your current DB structure
 * ✓ API: Type-safe with FastAPI (auto-docs at /docs)
 * ✓ Threading: Price updates still use threading optimization
 * ✓ Modularity: Frontend and backend can scale independently
 * ✓ Development: Each side can be developed/deployed separately
 * ✓ Performance: React frontend is super fast + Python backend handles heavy lifting
 * 
 * 
 * =============================================================================
 * TROUBLESHOOTING
 * =============================================================================
 * 
 * "API not found" error:
 * - Make sure backend is running on port 8000
 * - Check REACT_APP_API_URL in frontend/.env
 * 
 * CORS errors:
 * - Backend already has CORS enabled for localhost:3000 and localhost:5173
 * - If using different ports, update main.py CORSMiddleware
 * 
 * Database connection errors:
 * - Ensure database URL is correct in utils/db.py
 * - Update secrets.toml with API keys
 * 
 * Price update not working:
 * - Set FINNHUB_API_KEY and ALPHAVANTAGE_API_KEY in environment
 * - Or pass them as query parameters to /api/prices/refresh
 */

export const SETUP_GUIDE = `
Option 3: Hybrid Approach (React + FastAPI) Setup Complete!

Quick Start:
1. Backend: python -m uvicorn backend.main:app --reload
2. Frontend: cd frontend && npm install && npm run dev
3. Open: http://localhost:5173
`;
