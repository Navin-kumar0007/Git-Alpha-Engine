# Frontend Angel One Integration - Implementation Plan

## Goal

Implement complete frontend integration for Angel One API to display live market data from NSE/BSE stocks and indices with real-time updates via WebSocket.

## Proposed Changes

###Component 1: WebSocket Connection Hook

#### [NEW] useAngelOneWebSocket.js

**Purpose**: Custom React hook to manage WebSocket connection for live market data

**Features**:
- Auto-reconnect on connection loss
- Connection status tracking
- Live data reception and state management
- Error handling
- Cleanup on unmount

**State Management**:
- `marketData` - Map of token → latest tick data
- `isConnected` - WebSocket connection status
- `error` - Connection errors

---

### Component 2: Angel One Service API

#### [NEW] angelOneService.js

**Purpose**: API client for Angel One backend endpoints

**Functions**:
- `getStatus()` - Get service status  
- `startService(tokens)` - Start WebSocket connection
- `stopService()` - Stop WebSocket connection
- `subscribe(tokens, mode)` - Subscribe to additional tokens
- `unsubscribe(tokens, mode)` - Unsubscribe from tokens
- `getLastTick(token)` - Get cached last tick for a token

---

### Component 3: Angel One Control Panel

#### [NEW] AngelOneControl.jsx

**Purpose**: UI component for managing Angel One service

**Features**:
- Connection status display
- Service controls (Start/Stop)
- Token subscription manager
- Subscription mode selector

---

### Component 4: Live Market Widget

#### [NEW] LiveMarketWidget.jsx

**Purpose**: Display live prices with real-time updates

---

### Component 5: Live Markets Dashboard

#### [NEW] LiveMarketsDashboard.jsx

**Purpose**: Full-page dashboard for live market data

---

### Component 6: Integration into Main App

#### [MODIFY] App.jsx

**Changes**:
1. Import Angel One components
2. Add WebSocket hook initialization
3. Add "Live Markets" tab
4. Integrate LiveMarketWidget

## Implementation Strategy

### Phase 1: Core Infrastructure
1. Create WebSocket hook
2. Create API service
3. Add connection status indicator

### Phase 2: Basic UI
4. Create control panel component
5. Create live widget component
6. Test with NIFTY/BANKNIFTY

### Phase 3: Dashboard Integration
7. Create full dashboard
8. Integrate into App.jsx
9. Add navigation tab

## Verification Plan

### Manual Verification
1. During market hours: Verify real-time price updates
2. After hours: Verify graceful no-data state
3. Error scenarios: Test reconnection logic

## Timeline

- **Phase 1-2**: 1 hour (Core + Basic UI)
- **Phase 3**: 30 minutes (Integration)

**Total**: ~2 hours for complete implementation
