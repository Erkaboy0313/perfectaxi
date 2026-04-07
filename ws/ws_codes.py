# WebSocket message codes
# Positive  → success
# Negative  → error  (use these as the "code" key in frontend translation)

# ── Success ───────────────────────────────────────────────────────────────────
WS_SUCCESS = 1

# ── Authentication & Authorization ───────────────────────────────────────────
WS_INVALID_TOKEN      = -1   # Connection attempt with missing / invalid token
WS_USER_NOT_VERIFIED  = -2   # Driver connected but account not yet verified by admin
WS_INSUFFICIENT_FUND  = -3   # Driver balance too low to go online / accept orders

# ── Order Flow ────────────────────────────────────────────────────────────────
WS_ORDER_NOT_FOUND    = -4   # Order ID does not exist or belongs to another user
WS_ORDER_TAKEN        = -5   # Order already accepted by a different driver
WS_PRICE_CALC_FAILED  = -6   # Could not calculate ride price (route/service error)
WS_CANCEL_FAILED      = -7   # Cancel drive failed (order state does not allow it)
