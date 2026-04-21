// API client for Orbit Portfolio Frontend
// Communicates with FastAPI backend at http://localhost:8000

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiCall = async (endpoint, method = 'GET', body = null) => {
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
    },
  };

  if (body && method !== 'GET') {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(`${API_BASE}${endpoint}`, options);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'API Error');
  }

  return await response.json();
};

// Portfolio API
export const portfolio = {
  // Get portfolio summary
  getSummary: (currency = 'INR') =>
    apiCall(`/portfolio/summary?currency=${currency}`),

  // Get asset classes breakdown
  getAssets: (currency = 'INR') =>
    apiCall(`/portfolio/assets?currency=${currency}`),
};

// Holdings API
export const holdings = {
  // Get all holdings
  getAll: (assetClass = null, currency = 'INR') => {
    let url = `/holdings?currency=${currency}`;
    if (assetClass) url += `&asset_class=${assetClass}`;
    return apiCall(url);
  },

  // Get holdings for specific asset class
  getByClass: (assetClass, currency = 'INR') =>
    holdings.getAll(assetClass, currency),
};

// Transactions API
export const transactions = {
  // Get all transactions
  getAll: (assetClass = null, currency = 'INR') => {
    let url = `/transactions?currency=${currency}`;
    if (assetClass) url += `&asset_class=${assetClass}`;
    return apiCall(url);
  },

  // Get transactions for specific asset class
  getByClass: (assetClass, currency = 'INR') =>
    transactions.getAll(assetClass, currency),
};

// Cash Reserves API
export const cash = {
  // Get cash reserves
  getAll: (currency = 'INR') =>
    apiCall(`/cash?currency=${currency}`),
};

// Prices API
export const prices = {
  // Refresh prices for category
  refresh: (category, finnhubKey = null, avKey = null) => {
    let url = `/prices/refresh?category=${encodeURIComponent(category)}`;
    if (finnhubKey) url += `&finnhub_key=${finnhubKey}`;
    if (avKey) url += `&av_key=${avKey}`;
    return apiCall(url, 'POST');
  },
};

// Accounts API
export const accounts = {
  // Get all accounts
  getAll: () =>
    apiCall('/accounts'),
};

// Health Check
export const health = {
  check: () =>
    apiCall('/health'),
};

export default {
  portfolio,
  holdings,
  transactions,
  cash,
  prices,
  accounts,
  health,
};
