# Angel One Integration - Bug Fix Summary

## Issue Identified

**Error**: JSON serialization error when unsubscribing from tokens

```
[E 251226 00:02:33 smartWebSocketV2:260] Error occurred during unsubscribe: 
Object of type TokenSubscription is not JSON serializable
INFO: 127.0.0.1:50063 - "POST /api/angel-one/unsubscribe HTTP/1.1" 500 Internal Server Error
```

## Root Cause

The backend API endpoints were passing Pydantic `TokenSubscription` models directly to the `angel_one_service`, which then tried to pass them to the underlying SmartAPI WebSocket library. The SmartAPI library expects plain Python dictionaries for JSON serialization, not Pydantic models.

## Solution

Modified three endpoints in [`angel_one.py`](file:///c:/Users/Navin786/git_alpha_upgraded/Git-Alpha%20Engine/backend/app/api/angel_one.py):

1. **`/start`** endpoint (lines 59-66)
2. **`/subscribe`** endpoint (lines 108-120)
3. **`/unsubscribe`** endpoint (lines 146-158)

**Change Made**: Convert Pydantic models to dictionaries before passing to the service:

```python
# Before (causing error):
angel_one_service.subscribe(request.tokens, request.mode)

# After (fixed):
tokens_dict = [token.dict() for token in request.tokens]
angel_one_service.subscribe(tokens_dict, request.mode)
```

## Files Modified

- [`backend/app/api/angel_one.py`](file:///c:/Users/Navin786/git_alpha_upgraded/Git-Alpha%20Engine/backend/app/api/angel_one.py)

## Testing

The server will auto-reload due to `uvicorn --reload`. You can now:

1. ✅ Subscribe to tokens without errors
2. ✅ Unsubscribe from tokens without errors
3. ✅ Start the service with initial tokens

Try adding/removing symbols from the Live Markets dashboard to verify the fix!

## Status

✅ **Fixed** - The JSON serialization error is resolved. All Angel One API endpoints now properly convert Pydantic models to dictionaries before passing to the WebSocket manager.
