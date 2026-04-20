# 🚀 PERFORMANCE TRACKER v2 - QUICK START

## What Just Happened? 📦

Your portfolio app has been completely upgraded with a **professional performance tracking system**:

✅ **Money-Weighted Returns (IRR)** - Now calculates accurate returns accounting for investment timing  
✅ **Transaction-Based System** - Track MULTIPLE investments/withdrawals per asset  
✅ **Direct UI Input** - Add transactions without touching Google Sheets  
✅ **Smart Calculations** - Separates "money invested" from "current value"  

---

## ⚡ Quick Start (3 Steps)

### Step 1: Install Dependencies (2 minutes)

```bash
cd /Users/shubham/projects/portfolio
source venv/bin/activate
pip install gspread google-auth scipy
```

### Step 2: Create "Transactions" Sheet (5 minutes)

1. Open: https://docs.google.com/spreadsheets/d/1z_22sy-HriW9LvBQLQ7TEsdhASHV_f0AdwbawXfC5l0/
2. Create new sheet tab named: **`Transactions`**
3. Add 4 headers:
   - `asset_class`
   - `amount`
   - `investment_date`
   - `notes`

### Step 3: Migrate Your Data (5 minutes)

Add your current investments as separate rows. For example:

| asset_class | amount | investment_date | notes |
|---|---|---|---|
| Crypto | 300000 | 2021-03-15 | Initial BTC + ETH |
| Crypto | 50000 | 2024-01-15 | Additional ETH |
| Crypto | -20000 | 2025-06-20 | Profit withdrawal |
| US Market | 1850000 | 2023-03-01 | Vested |
| US Market | 500000 | 2026-04-20 | New investment |
| Indian Stock Market | 1603240 | 2022-06-01 | Zerodha |
| Indian Stock Market | -10000 | 2026-04-20 | Profit booking |

Then reload your app → **Pages > Performance** 

✨ **You should see full metrics now!**

---

## 🎯 How to Use

### Add a New Investment
1. Go to **Pages > Performance**
2. Scroll to **"➕ Add New Transaction"**
3. Select asset class → Enter amount (positive) → Pick date → Add notes
4. Click **"✅ Add Transaction"**
5. **Done!** Data syncs to Google Sheet automatically

### Record Profit Booking (Withdrawal)
1. Same form as above
2. But use **NEGATIVE amount**: `-50000`
3. Note: "Realized gains in bull market"
4. **This reduces current value but NOT the total capital invested** ❌

### View Transaction History
- Click the expandable **"📋 View X Transactions"** under each asset class
- See all your historical entries

### Check Metrics
- **Portfolio Summary:** Top 5 cards show total invested, current value, gain, IRR, years
- **Per Asset:** Each card shows invested amount, current value, absolute return %, and IRR
- **Charts:** Capital allocation (pie) + IRR by asset (bar)

---

## 📊 What Do These Numbers Mean?

### Portfolio Summary (Example)
```
💰 Total Invested: ₹72,98,728
   ↳ Sum of ALL money you've actually put in
   ↳ Doesn't reduce even if you book profits

📈 Current Value: ₹1,00,50,000
   ↳ What your portfolio is worth TODAY
   ↳ Auto-synced from your holdings

✨ Total Gain: ₹27,51,272
   ↳ Current Value - Total Invested

📊 Absolute Return: +37.70%
   ↳ (Gain / Invested) × 100
   ↳ Simple percentage return

🎯 Portfolio IRR: +12.45%
   ↳ Money-weighted return
   ↳ Accounts for timing of investments
   ↳ Most accurate metric
   
📊 Years Invested: 5.1
   ↳ From earliest investment to today
```

### Per Asset Example (Crypto)
```
📈 Invested: ₹3,30,000 (3 transactions)
   ↳ 300k initial + 50k added - 20k withdrawn = 330k total

💰 Current Value: ₹5,50,000
   ↳ Live price from your holdings

✨ Absolute Gain: ₹2,20,000
   ↳ UP 66.67% since you started

🎯 IRR: 12.45% (MWR)
   ↳ Your actual annualized return
```

---

## ⚠️ Important Rules

### DO ✅
- ✅ Use the form to add transactions
- ✅ Use negative numbers for withdrawals
- ✅ Use format: `YYYY-MM-DD` for dates
- ✅ Pick from dropdown for asset class
- ✅ Click "Refresh Data" if not seeing updates

### DON'T ❌
- ❌ Don't manually edit Google Sheet anymore
- ❌ Don't mix old format with new format
- ❌ Don't forget the minus sign for withdrawals
- ❌ Don't enter amounts with currency symbols (₹, $)

### Key Insight 💡
**Withdrawals (profit booking) DON'T reduce your "total capital invested"**

```
Timeline:
1. Invest ₹100k        → Capital = 100k
2. It grows to ₹150k   → Capital = 100k (unchanged)
3. Withdraw ₹50k       → Capital = 100k (still unchanged!)
4. Now worth ₹100k     → But you're still down from withdrawing
```

This is intentional! Your "capital invested" is separate from your "current value."

---

## 📚 Documentation Files

I've created comprehensive guides:

| File | Purpose | Read When |
|------|---------|-----------|
| **PERFORMANCE_SETUP_GUIDE.md** | Complete setup + concepts | First time setup |
| **DATA_MIGRATION_GUIDE.md** | Step-by-step data migration | Migrating old data |
| **TECHNICAL_REFERENCE.md** | Architecture, formulas, code | Advanced/developers |

---

## 🔧 Optional: Google Sheets API Setup

For automatic syncing (recommended), configure Google Sheets API:

**5-minute setup:**

1. Go to: https://console.cloud.google.com/
2. Create service account
3. Download JSON key
4. Create `.streamlit/secrets.toml`:

```toml
[google_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "..."
client_email = "..."
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

5. Share your Google Sheet with the `client_email`
6. Done! UI transactions now sync automatically

**Without this?** You can still:
- ✅ View data from Google Sheet
- ✅ Manually edit Sheet
- ⚠️ UI transactions won't sync (error message appears)

---

## ❓ FAQ

### Q: Can I track multiple investments in same asset?
**A:** Yes! Each transaction is separate. Invest ₹100k one day and ₹50k another = 2 rows.

### Q: How do I handle profit reinvestment?
**A:** As 2 separate transactions:
1. Withdraw profit: `amount = -50000`
2. Reinvest: `amount = +50000`

### Q: Will withdrawal reduce my "total invested"?
**A:** No! Only positive amounts count. This is intentional.

### Q: Which is more important: IRR or CAGR?
**A:** **IRR** for accurate returns (what we show).   
**CAGR** is simpler but less accurate for multi-period portfolios.

### Q: Can I edit past transactions?
**A:** Not via UI (future feature). Options:
- Add a correction transaction
- Manually edit Google Sheet
- Contact support for data correction

### Q: What if portfolio data isn't updating?
**A:** 
1. Ensure Zerodha/broker sync is running
2. Click "Refresh Data" in sidebar
3. Check if holdings have current_price > 0

### Q: Can I track expenses/fees?
**A:** Not in this version. Recommend:
- Enter gross amounts (as-is)
- Track fees separately if needed

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| No data showing | Create "Transactions" sheet, click Refresh |
| Amount shows 0 | Don't use ₹ symbol, just numbers |
| IRR shows "—" | Need live portfolio data from DB |
| Transaction won't save | Check if API is configured |
| Form validation error | Check amount ≠ 0 and date is valid |
| Cache not clearing | Manually click Refresh button |

---

## 🎓 Learn More

**These 3 files have all details:**

1. **PERFORMANCE_SETUP_GUIDE.md** - Comprehensive setup
2. **DATA_MIGRATION_GUIDE.md** - Data format & migration
3. **TECHNICAL_REFERENCE.md** - How it works under the hood

---

## ✨ What's Next?

1. **Right now:** Install dependencies (1 command)
2. **Next (5min):** Create Transactions sheet in Google Sheets
3. **Then (5min):** Add your historical data as rows
4. **Finally:** Reload app and check the Performance page

**Total time: ~15 minutes → Full setup! 🎉**

---

## 📞 Quick Reference

**Key Files:**
- Main page: `pages/7_Performance.py`
- Business logic: `services/performance_service.py`
- Sheets API: `services/gsheet_service.py`

**Google Sheet:**
- Link: https://docs.google.com/spreadsheets/d/1z_22sy-HriW9LvBQLQ7TEsdhASHV_f0AdwbawXfC5l0/
- New sheet: "Transactions"

**Canonical Asset Class Names:**
- Crypto
- US Market
- Indian Stock Market
- Indian Mutual Funds
- Lending

---

**Version:** Performance Tracker v2.0  
**Status:** Ready to Use ✓  
**Last Updated:** 2026-04-20
