# CAGR Calculation Guide

## Overview

This document explains how **CAGR (Compound Annual Growth Rate)** is calculated in your portfolio tracker, including how it handles different scenarios like withdrawals, multiple investments, and edge cases.

---

## What is CAGR?

**CAGR** measures the average annual growth rate of your investment from the earliest transaction date to today.

### Basic Formula (No Withdrawals)
```
CAGR = (Final Value / Total Invested) ^ (1 / Years) - 1
```

### With Withdrawals (Net Capital Formula)
```
CAGR = (Final Value / Net Capital) ^ (1 / Years) - 1
Where: Net Capital = Total Invested - Total Withdrawn
```

---

## Scenario 1: Simple Investment (No Withdrawals)

**The Situation:**
- You invest ₹100,000 on Jan 15, 2022
- Today (April 20, 2026): Portfolio value is ₹150,000
- Time elapsed: 4.26 years

**Calculation:**

```
Total Invested = ₹100,000
Total Withdrawn = ₹0
Net Capital = ₹100,000
Final Value = ₹150,000
Years = 4.26

CAGR = (150,000 / 100,000) ^ (1 / 4.26) - 1
CAGR = (1.5) ^ (0.235) - 1
CAGR = 1.0988 - 1
CAGR = 0.0988 = 9.88% ✅
```

**What it means:** Your investment grew at an average of **9.88% per year**.

---

## Scenario 2: Investment with One Withdrawal

**The Situation:**
- Jan 15, 2022: Invest ₹100,000
- June 20, 2024: Withdraw ₹30,000 (need cash)
- Today (April 20, 2026): Portfolio value is ₹85,000
- Time elapsed: 4.26 years (from first investment)

**Calculation:**

```
Total Invested = ₹100,000
Total Withdrawn = ₹30,000
Net Capital = 100,000 - 30,000 = ₹70,000
Final Value = ₹85,000
Years = 4.26

CAGR = (85,000 / 70,000) ^ (1 / 4.26) - 1
CAGR = (1.214) ^ (0.235) - 1
CAGR = 1.0463 - 1
CAGR = 0.0463 = 4.63% ✅
```

**What it means:** Your remaining capital earned **4.63% annually**.

**Why not use 100,000?**
- ❌ WRONG: (85,000 / 100,000) ^ (1/4.26) = -3.8% (looks like a loss!)
- ✅ RIGHT: (85,000 / 70,000) ^ (1/4.26) = +4.63% (reflects actual growth on your capital)

The withdrawal reduced your capital, so the denominator should be the net capital that stayed invested.

---

## Scenario 3: Multiple Investments (Dollar-Cost Averaging)

**The Situation:**
- Jan 15, 2022: Invest ₹100,000
- June 20, 2023: Invest ₹50,000 (more capital)
- Today (April 20, 2026): Portfolio value is ₹180,000
- Time elapsed: 4.26 years (from earliest investment)

**Calculation:**

```
Total Invested = 100,000 + 50,000 = ₹150,000
Total Withdrawn = ₹0
Net Capital = ₹150,000
Final Value = ₹180,000
Years = 4.26

CAGR = (180,000 / 150,000) ^ (1 / 4.26) - 1
CAGR = (1.2) ^ (0.235) - 1
CAGR = 1.0442 - 1
CAGR = 0.0442 = 4.42% ✅
```

**What it means:** Your average annual return on total capital deployed is **4.42%**.

**Why use earliest date for years?**
- The later investment only has 2.8 years of history
- CAGR uses the **earliest investment date** to show long-term performance
- This is more conservative (accounts for older capital having more time to grow)

---

## Scenario 4: Multiple Investments + Withdrawals (Complex Case)

**The Situation:**
- Jan 15, 2022: Invest ₹100,000
- June 20, 2023: Invest ₹50,000
- Dec 15, 2024: Withdraw ₹40,000 (partial withdrawal)
- Today (April 20, 2026): Portfolio value is ₹140,000
- Time elapsed: 4.26 years

**Calculation:**

```
Total Invested = 100,000 + 50,000 = ₹150,000
Total Withdrawn = ₹40,000
Net Capital = 150,000 - 40,000 = ₹110,000
Final Value = ₹140,000
Years = 4.26

CAGR = (140,000 / 110,000) ^ (1 / 4.26) - 1
CAGR = (1.2727) ^ (0.235) - 1
CAGR = 1.0597 - 1
CAGR = 0.0597 = 5.97% ✅
```

**What it means:** After withdrawing ₹40,000, your remaining ₹110,000 grew at **5.97% annually**.

---

## Scenario 5: Full Redemption (All Withdrawn)

**The Situation:**
- Jan 15, 2022: Invest ₹100,000
- March 20, 2024: Withdraw ₹100,000 (full exit)
- Today (April 20, 2026): No holdings left

**Calculation:**

```
Total Invested = ₹100,000
Total Withdrawn = ₹100,000
Net Capital = 100,000 - 100,000 = ₹0

CAGR = Cannot calculate (Net Capital = 0)
Result: Returns None ✅
```

**What it means:** You've exited completely, so CAGR isn't meaningful. In this case, look at:
- **Gain**: Cash withdrawn - Capital invested = Loss indicator
- **IRR**: Will show actual time-weighted return on your capital

---

## Scenario 6: Loss Scenario (Negative Returns)

**The Situation:**
- Jan 15, 2022: Invest ₹100,000
- Today (April 20, 2026): Portfolio value is ₹80,000
- Time elapsed: 4.26 years

**Calculation:**

```
Total Invested = ₹100,000
Total Withdrawn = ₹0
Net Capital = ₹100,000
Final Value = ₹80,000
Years = 4.26

CAGR = (80,000 / 100,000) ^ (1 / 4.26) - 1
CAGR = (0.8) ^ (0.235) - 1
CAGR = 0.9528 - 1
CAGR = -0.0472 = -4.72% ✅
```

**What it means:** Your investment declined at **-4.72% per year**.

---

## How to Use CAGR in Your Portfolio

### When CAGR is Most Useful
- ✅ Long-term investments (2+ years)
- ✅ No frequent withdrawals
- ✅ Comparing to benchmark returns (Nifty 50, S&P 500, etc.)
- ✅ After you have a few years of history

### When to Use IRR Instead
- ✅ Frequent withdrawals or deposits
- ✅ Timing matters (concentrated investments)
- ✅ Short-term analysis (< 1 year)
- ✅ You want a money-weighted return

---

## Code Reference

Your portfolio system uses this logic:

```python
def _calculate_segmented_cagr(cash_flows, current_value):
    """
    CAGR calculation with withdrawal support:
    1. Calculate total_invested (all positive amounts)
    2. Calculate total_withdrawn (all negative amounts)
    3. If withdrawals exist: use net_capital formula
    4. Otherwise: use traditional formula
    """
    total_invested = sum(cf[1] for cf in cash_flows if cf[1] > 0)
    total_withdrawals = sum(abs(cf[1]) for cf in cash_flows if cf[1] < 0)
    
    if total_withdrawals > 0:
        # With withdrawals: use net capital
        net_capital = total_invested - total_withdrawals
        if net_capital > 0:
            return (current_value / net_capital) ^ (1 / years) - 1
    else:
        # No withdrawals: traditional formula
        return (current_value / total_invested) ^ (1 / years) - 1
```

---

## Quick Reference Table

| Scenario | Total Invested | Withdrawn | Net Capital | Final Value | CAGR | Notes |
|----------|---|---|---|---|---|---|
| Simple | ₹100K | ₹0 | ₹100K | ₹150K | +9.88% | Traditional case |
| With 1 Withdrawal | ₹100K | ₹30K | ₹70K | ₹85K | +4.63% | Use net capital |
| Multiple Deposits | ₹150K | ₹0 | ₹150K | ₹180K | +4.42% | DCA strategy |
| Complex | ₹150K | ₹40K | ₹110K | ₹140K | +5.97% | Combined scenario |
| Loss | ₹100K | ₹0 | ₹100K | ₹80K | -4.72% | Negative returns |
| Full Exit | ₹100K | ₹100K | ₹0 | ₹0 | N/A | Can't calculate |

---

## Summary

### The Key Rule
**When withdrawals are present, CAGR denominator = Net Capital (what stayed invested), NOT total capital deployed.**

This ensures your CAGR reflects the actual return on the capital that remained in the portfolio, not an artificially negative figure from pulling out funds.

### Three Takeaways
1. **CAGR uses earliest investment date** → measures from day 1
2. **Withdrawals reduce denominator** → using net capital, not gross invested
3. **IRR is complementary** → use both for complete picture

---

## Questions?

If your CAGR seems unexpectedly low or negative despite profits:
1. Check if you have **withdrawals** (they reduce the denominator)
2. Look at **IRR** (better for erratic cash flows)
3. Review **Absolute Return %** (simple: (gain/invested) × 100)
