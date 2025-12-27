# AI Assistant + Angel One Integration Plan

## Overview

Integrate the existing AI Assistant with Angel One API to enable natural language queries for live market data.

## Proposed Changes

### Backend Changes

#### [MODIFY] ai_agent.py
Add Angel One integration tools and update query handling to recognize market data requests.

**New Functions**:
- `get_live_price_tool(symbol)` - Fetch current price
- `subscribe_symbol_tool(symbol)` - Subscribe to symbol
- `get_subscribed_symbols_tool()` - List subscriptions
- `compare_symbols_tool(symbols)` - Compare multiple symbols

#### [NEW] angel_one_tools.py
Create dedicated file for Angel One tools with symbol mapping.

### Frontend Changes  

#### [MODIFY] AIAssistant.jsx  
Add quick action buttons for common market queries and enhance response formatting for market data.

## Example Queries

- "What's NIFTY price?"
- "Subscribe to RELIANCE"
- "Compare INFY and TCS"

## Verification Plan

### Manual Testing
1. Start backend and frontend
2. Open AI Assistant
3. Ask "What's NIFTY price?"
4. Verify response shows live price (during market hours) or last cached price
5. Ask "Subscribe to BANKNIFTY"
6. Navigate to Live Markets tab and verify BANKNIFTY is subscribed

### Implementation Phases
1. Phase 1: Basic price queries (2-3 hours)
2. Phase 2: Subscription management (2 hours)
3. Phase 3: Analysis features (3-4 hours)
