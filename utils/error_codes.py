# ── Authentication & Authorization ───────────────────────────────────────────
NOT_AUTHENTICATED   = 'NOT_AUTHENTICATED'    # No token / unauthenticated request
ACCOUNT_INACTIVE    = 'ACCOUNT_INACTIVE'     # Token present but account not verified
USER_BLOCKED        = 'USER_BLOCKED'         # User has been blocked
PERMISSION_DENIED   = 'PERMISSION_DENIED'    # Authenticated but insufficient role
FORBIDDEN           = 'FORBIDDEN'            # Generic 403

# ── User & Verification ───────────────────────────────────────────────────────
USER_NOT_FOUND      = 'USER_NOT_FOUND'       # No user matching phone/role/id
DRIVER_NOT_FOUND    = 'DRIVER_NOT_FOUND'     # Driver record not found
INVALID_CODE        = 'INVALID_CODE'         # Wrong SMS verification code

# ── Request Issues ────────────────────────────────────────────────────────────
METHOD_NOT_ALLOWED  = 'METHOD_NOT_ALLOWED'   # HTTP method not allowed for this role
VALIDATION_ERROR    = 'VALIDATION_ERROR'     # Request data failed DRF validation

# ── Business Logic ────────────────────────────────────────────────────────────
SERVICE_ALREADY_EXISTS = 'SERVICE_ALREADY_EXISTS'  # Driver already has this service

# ── General ───────────────────────────────────────────────────────────────────
SERVER_ERROR        = 'SERVER_ERROR'         # Unhandled / unexpected server error
