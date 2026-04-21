# UI/UX Design Prompt for Claude AI Design

## PROJECT OVERVIEW
Design a modern, futuristic portfolio management dashboard for tracking investments across multiple asset classes (US Stocks, Indian Stocks, Mutual Funds, Crypto, Lending). The platform supports multi-currency transactions, real-time price updates, performance analytics (IRR/CAGR), and multi-account management. All existing features must be retained with significantly improved UX/UI.

---

## DESIGN PHILOSOPHY
- **Style**: Modern Fintech + Futuristic Elements
- **Theme**: Dark mode (primary) with light mode option
- **Vibe**: Professional yet approachable, tech-forward, data-driven with micro-interactions
- **Audience**: Individual investors tracking diverse portfolios

---

## COLOR PALETTE

### Primary Colors
- **Dark Background**: #0A0E27 (deep navy-black)
- **Card Background**: #0F1429 (slightly lighter navy)
- **Accent Green**: #06D6A0 (profit/gains highlight)
- **Accent Blue**: #3B82F6 (secondary metrics, info)
- **Accent Orange**: #FF9D00 (warnings, attention)
- **Text Primary**: #F8F9FA (off-white)
- **Text Secondary**: #A0AEC0 (muted gray)
- **Border**: #1E293B (subtle dividers)

### Gradient Accents
- Green to Teal fade for positive metrics
- Orange to Red fade for losses/warnings
- Blue gradient for secondary information

---

## TYPOGRAPHY
- **Headlines**: Modern sans-serif (Inter, Poppins) - bold, clear hierarchy
- **Body**: Clean sans-serif with 1.5 line-height for readability
- **Numbers/Data**: Monospace font for precise alignment and data clarity
- **Font Sizes**: Use clear hierarchy (H1: 32px, H2: 24px, Body: 14px)

---

## LAYOUT & NAVIGATION

### Header/Top Navigation
- Logo + App name (left aligned)
- Tab navigation: Overview | Manage Positions | Performance Analytics | Reports | Settings
- Currency toggle (₹ / $) in top right
- User profile menu
- Real-time sync status indicator

### Sidebar (Optional - Collapsible)
- Asset Class quick links with icons:
  - 🇺🇸 US Market
  - 📈 Indian Stock Market
  - 🏦 Indian Mutual Funds
  - ₿ Crypto
  - 🤝 Lending
- Active account selector (multi-select dropdown)
- Quick access to add transaction, refresh prices
- Settings link

---

## PAGE: GLOBAL DASHBOARD/OVERVIEW

### Hero Section (Top)
- Large, prominent portfolio total value card
- Centered metric: "Total Portfolio Value: $XXXXX"
- Subtext: "Last updated: X minutes ago" with sync status
- Quick stat badges below (Total Invested, Total Gain, Gain %, Accounts Count)

### Row 2 - Key Performance Cards (4-column grid)
- Card 1: Total Invested (amount + trend)
- Card 2: Current Value (amount + trend)
- Card 3: Total Gain/Loss (amount + percentage with green/red indicator)
- Card 4: Time Period Selector (7D, 30D, 90D, YTD, All-time)

### Row 3 - Visualizations (2-column layout)
- **Left**: Donut/Pie chart showing allocation by asset class with legends
  - Interactive on hover (highlight, show %)
  - Colors per asset type
- **Right**: Line chart showing portfolio value over time (selectable period)
  - Multiple line options: Total Value, Total Invested, Gain/Loss

### Row 4 - Asset Class Performance Grid (5 columns - one per asset class)
Each card shows:
- Asset class icon + name
- Current value (large number)
- Invested amount (smaller)
- Gain/Loss with percentage
- Status dot (red/green/gray)
- Click to drill down into asset details
- Numbers should be color-coded (green for gains, red for losses)

---

## PAGE: ASSET CLASS DETAIL (e.g., US Market, Indian Stocks, Crypto)

### Header Section
- Asset class icon + name + status indicator
- Current value + total invested (side by side)
- Performance metric: CAGR % (with tooltip explaining calculation)
- IRR % (with tooltip)
- Currency toggle for this asset class

### Main Content - Tabbed Interface

#### Tab 1: Holdings / Positions
- Data table with columns:
  - Ticker symbol (bold, click to expand)
  - Quantity
  - Avg Price (with currency indicator)
  - Current Price (live, with up/down arrow)
  - Total Invested
  - Current Value
  - Gain/Loss (amount + %)
  - Last Updated time
- **Actions per row**: Edit quantity, Add note, Remove position
- **Table features**:
  - Sort by any column
  - Filter by gain/loss status
  - Search by ticker
  - Bulk actions (export, refresh prices for this asset)
- **Refresh Prices Button**: "🔄 Refresh Prices (⚡ Turbo Mode)" with real-time progress indicator

#### Tab 2: Transactions
- Timeline view OR table view (toggle)
- Each transaction shows:
  - Date
  - Type (Buy/Sell/Dividend)
  - Amount
  - Currency (USD/INR/etc)
  - Price per unit
  - Quantity
  - Notes
- Search + filter by date range, type, amount
- Add new transaction button (opens modal)
- Export as CSV

#### Tab 3: Cash & Reserves
- Show current cash held in this asset class
- Currency breakdown if multi-currency
- Add/Edit cash button
- Floating cash visual indicator

---

## PAGE: PERFORMANCE ANALYTICS

### Header
- Title: "Performance Analysis"
- Date range selector (7D, 30D, 90D, 1Y, 5Y, All-time)
- Currency toggle

### Section 1 - Key Metrics (Interactive Cards)
Display grid with hover tooltips:
- **Total Return %** (calculation breakdown in tooltip)
- **IRR %** (Money-weighted return - with explanation)
- **CAGR %** (Compound annual growth rate - explains withdrawal handling)
- **Absolute Gain/Loss** (currency amount)
- **Best Performing Asset** (asset + return %)
- **Worst Performing Asset** (asset + return %)

Each metric should have:
- Large number
- Trend indicator (↑/↓)
- Color coding (green/red)
- Info icon with tooltip explaining calculation method

### Section 2 - Charts (2-column layout)
- **Left**: Stacked area chart showing contribution by asset class over time
- **Right**: Waterfall chart showing invested → gains/losses → current value

### Section 3 - By Asset Class Breakdown (Expandable Accordion)
For each asset class:
- Name + icon
- Investment metrics (total invested, current value, gain)
- Performance (IRR, CAGR, Absolute return)
- Number of transactions
- Date range (earliest to latest)
- Expand button to see individual holdings performance

### Section 4 - Transaction History Timeline
- Chronological view of all transactions
- Color-coded by type (green buy, red sell, blue dividend)
- Filterable by asset class, date range
- Show impact on portfolio value at each transaction

---

## PAGE: MANAGE ACCOUNTS & SETTINGS

### Section 1 - Active Accounts
- List of all connected accounts (US Broker 1, Zerodha Account 1, etc)
- For each account:
  - Account name (editable)
  - Asset class type
  - Broker name
  - Connection status (✓ Connected/✗ Disconnected)
  - Last sync time
  - Action buttons: Sync Now, Edit, Disconnect

### Section 2 - Add New Account
- Modal/form with fields:
  - Account name
  - Asset class type (dropdown)
  - Broker selection
  - Auto-sync frequency toggle
- Info icon explaining each field

### Section 3 - Settings
- Preferred currency (INR/USD/etc)
- Exchange rate source configuration
- Auto-refresh frequency
- Theme (Dark/Light)
- Notifications preferences (price alerts, performance milestones)
- Data export (CSV, PDF format)

---

## INTERACTIVE ELEMENTS & MICRO-INTERACTIONS

### Buttons & CTAs
- Primary buttons: Gradient (blue to cyan), rounded corners, glow effect on hover
- Secondary buttons: Outlined, smooth color transition
- Icon buttons: Hover reveals label tooltip

### Data Tables
- Hover effect: Rows highlight with subtle background change
- Sortable columns: Arrow indicator on header
- Expandable rows: Smooth height animation
- Loading state: Skeleton placeholders

### Cards
- Glassmorphism effect (semi-transparent, slight blur background)
- Subtle shadow/glow on hover
- Corner radius: 12px

### Progress Indicators
- Linear progress for price refresh (animated bar, percentage label)
- Circular progress for loading states
- Spinner with pulsing effect

### Tooltips & Modals
- Appear with fade-in + scale animation
- Smooth close animation
- Info icons with consistent placement

### Color Coding
- Green (#06D6A0): Gains, positive metrics, buy orders
- Red/Orange: Losses, warnings, sell orders
- Blue (#3B82F6): Info, neutral metrics
- Gray: Neutral, secondary data

### Responsive Design
- Mobile: Single column, collapsible navigation
- Tablet: 2-column layouts become responsive stacks
- Desktop: Full multi-column layouts
- Touch-friendly: Larger tap targets (44px minimum)

---

## SPECIFIC FEATURE HIGHLIGHTS TO DESIGN

### 1. Real-Time Price Updates
- Show last update timestamp
- Visual indicator: "⚡ Updated 2 mins ago"
- Animated refresh spinner during fetch

### 2. Multi-Currency Support
- Currency badge on every amount (USD, INR, etc)
- Toggle to switch view currency
- Show conversion rate inline

### 3. Transaction Management
- Add transaction modal with validation
- Quick add buttons for common actions
- Undo action for recent transactions

### 4. Performance Metrics Explanation
- Hover tooltips with calculation formulas
- Links to detailed explanation page
- Examples showing withdrawal impact on CAGR

### 5. Account Linking Integration
- Visual flow for connecting brokers
- Clear success/error states
- Sync progress indication

### 6. Export & Reporting
- Export button → CSV/PDF options
- Date range selection
- Preview before download

---

## DESIGN CONSIDERATIONS

- **Data Density**: Balance information density with whitespace
- **Accessibility**: AA compliance, sufficient color contrast, keyboard navigation
- **Performance Visualization**: Use animations to show value changes (smooth number transitions)
- **Error States**: Clear, helpful error messages with action suggestions
- **Empty States**: Design for when a user has no data (onboarding flow)
- **Print Friendly**: Reports should be printable

---

## EXISTING FEATURES TO PRESERVE

✓ Multi-asset class tracking  
✓ Real-time price updates (US Market - Finnhub/Alpha Vantage)  
✓ Indian Stock integration  
✓ Mutual Fund tracking (mfapi.in)  
✓ Crypto tracking (Binance)  
✓ Lending portfolio  
✓ Multi-currency support (USD/INR conversion)  
✓ IRR calculation (money-weighted returns)  
✓ CAGR with withdrawal handling  
✓ Multi-account management  
✓ Cash reserves tracking per asset  
✓ Transaction history with withdrawal support  
✓ Zerodha integration  
✓ Email report sync  

---

## DELIVERABLES

1. Complete UI/UX design mockups (all pages)
2. Interactive component library
3. Color palette & design tokens
4. Typography system
5. Micro-interaction animations (Lottie files)
6. Mobile/tablet responsive variants
7. Dark & light mode designs

---

**Use this prompt on https://claude.ai/design to create a modern, futuristic redesign of your portfolio tracker.**
