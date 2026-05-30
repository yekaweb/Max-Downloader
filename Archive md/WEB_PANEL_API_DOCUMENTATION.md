"""
Phase 2 Web Panel API Documentation & Implementation Guide
Endpoints for Coin System, User Management, and Statistics
"""

# API Base URL: http://localhost:8000/api

# ============================================================
# 1. COIN SYSTEM ENDPOINTS
# ============================================================

"""
GET /api/coins/transactions
Description: Get user coin transaction history
Authentication: JWT Token required
Query Parameters:
    - user_id (int): User ID (optional - admin only)
    - limit (int): Number of records (default: 50)
    - offset (int): Pagination offset (default: 0)
    - type (str): Filter by type - 'earn', 'spend', 'bonus' (optional)

Response:
{
    "status": "success",
    "data": [
        {
            "id": 1,
            "user_id": 123,
            "amount": 50,
            "type": "earn",
            "description": "Download reward",
            "created_at": "2024-05-24T14:32:00"
        },
        ...
    ],
    "total": 156,
    "page": 1
}

Example:
GET /api/coins/transactions?limit=10&offset=0
"""

"""
GET /api/coins/balance
Description: Get current coin balance for user
Authentication: JWT Token required

Response:
{
    "status": "success",
    "user_id": 123,
    "balance": 450,
    "currency": "coins",
    "last_updated": "2024-05-24T14:45:00"
}

Example:
GET /api/coins/balance
"""

"""
GET /api/coins/stats
Description: Get coin statistics (admin only)
Authentication: JWT Token + Admin role required

Response:
{
    "status": "success",
    "stats": {
        "total_coins_in_circulation": 428000,
        "total_coins_earned": 652000,
        "total_coins_spent": 224000,
        "total_bonus_awarded": 52000,
        "total_users_with_coins": 2847,
        "avg_balance_per_user": 150,
        "top_earner_balance": 2450,
        "transactions_today": 342,
        "transactions_this_week": 2156
    }
}

Example:
GET /api/coins/stats
"""

"""
GET /api/coins/leaderboard
Description: Get top coin earners
Authentication: No auth required (public)
Query Parameters:
    - period (str): 'day', 'week', 'month', 'all' (default: 'month')
    - limit (int): Top N users (default: 10)

Response:
{
    "status": "success",
    "period": "month",
    "leaderboard": [
        {
            "rank": 1,
            "user_id": 456,
            "username": "crypto_master",
            "coins_earned": 2450,
            "downloads": 156,
            "referrals": 8
        },
        {
            "rank": 2,
            "user_id": 789,
            "username": "video_enthusiast",
            "coins_earned": 1890,
            "downloads": 132,
            "referrals": 5
        },
        ...
    ]
}

Example:
GET /api/coins/leaderboard?period=week&limit=5
"""

"""
POST /api/coins/award
Description: Award bonus coins to user (admin only)
Authentication: JWT Token + Admin role required

Request Body:
{
    "user_id": 123,
    "amount": 100,
    "reason": "Special promotion"
}

Response:
{
    "status": "success",
    "message": "100 coins awarded to user",
    "transaction_id": 854,
    "new_balance": 550
}

Example:
POST /api/coins/award
Content-Type: application/json

{
    "user_id": 123,
    "amount": 100,
    "reason": "Loyalty bonus"
}
"""


# ============================================================
# 2. USER MANAGEMENT ENDPOINTS
# ============================================================

"""
GET /api/users
Description: Get list of all users (admin only)
Authentication: JWT Token + Admin role required
Query Parameters:
    - limit (int): Records per page (default: 50)
    - offset (int): Pagination offset
    - search (str): Search by username or ID
    - status (str): Filter by status - 'active', 'inactive', 'banned'

Response:
{
    "status": "success",
    "data": [
        {
            "id": 123,
            "username": "johndoe",
            "chat_id": 123456789,
            "coins": 450,
            "subscriptions": 1,
            "downloads": 156,
            "referrals": 3,
            "created_at": "2024-01-15T10:00:00",
            "last_active": "2024-05-24T14:30:00",
            "status": "active"
        },
        ...
    ],
    "total": 2847
}

Example:
GET /api/users?limit=20&offset=0&status=active
"""

"""
GET /api/users/{user_id}
Description: Get detailed user information
Authentication: JWT Token (own user or admin)

Response:
{
    "status": "success",
    "user": {
        "id": 123,
        "username": "johndoe",
        "chat_id": 123456789,
        "coins": 450,
        "referral_code": "REF_123",
        "referred_by": "REF_456",
        "subscriptions": [
            {
                "id": 1,
                "plan": "Premium",
                "expires_at": "2024-06-24",
                "status": "active"
            }
        ],
        "statistics": {
            "total_downloads": 156,
            "total_referrals": 3,
            "coins_earned": 850,
            "coins_spent": 400
        },
        "created_at": "2024-01-15T10:00:00",
        "last_active": "2024-05-24T14:30:00"
    }
}

Example:
GET /api/users/123
"""

"""
PUT /api/users/{user_id}/status
Description: Update user status (admin only)
Authentication: JWT Token + Admin role required

Request Body:
{
    "status": "active|inactive|banned",
    "reason": "Optional reason for status change"
}

Response:
{
    "status": "success",
    "message": "User status updated",
    "user_id": 123,
    "new_status": "banned"
}

Example:
PUT /api/users/123/status
Content-Type: application/json

{
    "status": "banned",
    "reason": "Suspicious activity"
}
"""


# ============================================================
# 3. BROADCAST & MESSAGING ENDPOINTS
# ============================================================

"""
POST /api/broadcasts
Description: Create and send broadcast message (admin only)
Authentication: JWT Token + Admin role required

Request Body:
{
    "message": "Hello users!",
    "target": "all|premium|free|specific",
    "user_ids": [123, 456, 789],  // For 'specific' target
    "schedule_at": "2024-05-25T10:00:00"  // Optional - schedule for later
}

Response:
{
    "status": "success",
    "broadcast_id": 42,
    "message": "Broadcast created",
    "target": "all",
    "recipients_count": 2847,
    "scheduled": false
}

Example:
POST /api/broadcasts
Content-Type: application/json

{
    "message": "🎉 New feature: Download with higher quality now available!",
    "target": "premium"
}
"""

"""
GET /api/broadcasts
Description: Get broadcast history (admin only)
Authentication: JWT Token + Admin role required

Response:
{
    "status": "success",
    "broadcasts": [
        {
            "id": 42,
            "message": "Hello users!",
            "target": "all",
            "total_recipients": 2847,
            "delivered": 2801,
            "failed": 46,
            "status": "completed",
            "created_at": "2024-05-24T10:00:00",
            "delivery_rate": 98.4
        },
        ...
    ]
}

Example:
GET /api/broadcasts?limit=10
"""


# ============================================================
# 4. SUBSCRIPTION & PLAN ENDPOINTS
# ============================================================

"""
GET /api/plans
Description: Get available subscription plans
Authentication: No auth required (public)

Response:
{
    "status": "success",
    "plans": [
        {
            "id": 1,
            "name": "Free",
            "price_coins": 0,
            "features": {
                "downloads_per_day": 10,
                "max_file_size": 500,
                "quality": "720p"
            }
        },
        {
            "id": 2,
            "name": "Premium",
            "price_coins": 100,
            "price_usd": 9.99,
            "duration_days": 30,
            "features": {
                "downloads_per_day": 999,
                "max_file_size": 2048,
                "quality": "1080p",
                "no_ads": true
            }
        },
        {
            "id": 3,
            "name": "VIP",
            "price_coins": 300,
            "price_usd": 29.99,
            "duration_days": 90,
            "features": {
                "downloads_per_day": 999,
                "max_file_size": 4096,
                "quality": "4K",
                "priority_support": true
            }
        }
    ]
}

Example:
GET /api/plans
"""

"""
GET /api/subscriptions
Description: Get user's active subscriptions
Authentication: JWT Token (own user or admin)

Response:
{
    "status": "success",
    "subscriptions": [
        {
            "id": 1,
            "plan_name": "Premium",
            "expires_at": "2024-06-24",
            "created_at": "2024-05-24",
            "days_remaining": 31,
            "status": "active",
            "auto_renew": false
        }
    ]
}

Example:
GET /api/subscriptions
"""

"""
POST /api/subscriptions/purchase
Description: Purchase subscription with coins
Authentication: JWT Token required

Request Body:
{
    "plan_id": 2,
    "payment_method": "coins|cryptobot|zarinpal"
}

Response:
{
    "status": "success",
    "subscription_id": 42,
    "plan_name": "Premium",
    "expires_at": "2024-06-24",
    "coins_spent": 100
}

Example:
POST /api/subscriptions/purchase
Content-Type: application/json

{
    "plan_id": 2,
    "payment_method": "coins"
}
"""


# ============================================================
# 5. STATISTICS & ANALYTICS ENDPOINTS
# ============================================================

"""
GET /api/analytics/downloads
Description: Get download statistics (admin only)
Authentication: JWT Token + Admin role required
Query Parameters:
    - period (str): 'day', 'week', 'month' (default: 'week')

Response:
{
    "status": "success",
    "period": "week",
    "statistics": {
        "total_downloads": 8420,
        "avg_downloads_per_day": 1203,
        "peak_hour": "14:00",
        "platforms": {
            "youtube": 3800,
            "instagram": 2100,
            "tiktok": 1400,
            "twitter": 1120
        },
        "avg_file_size": 245,
        "fastest_download": 2.3,
        "slowest_download": 127.5,
        "avg_download_time": 18.5
    }
}

Example:
GET /api/analytics/downloads?period=month
"""

"""
GET /api/analytics/revenue
Description: Get revenue statistics (admin only)
Authentication: JWT Token + Admin role required

Response:
{
    "status": "success",
    "revenue": {
        "total_subscriptions": 347,
        "active_subscriptions": 312,
        "estimated_monthly_revenue": 2847,
        "coins_in_circulation": 428000,
        "avg_user_value": 8.20,
        "churn_rate": 10.1,
        "new_subscriptions_today": 12
    }
}

Example:
GET /api/analytics/revenue
"""


# ============================================================
# 6. ERROR RESPONSES
# ============================================================

"""
All endpoints return standard error format:

{
    "status": "error",
    "message": "Error description",
    "error_code": "INVALID_REQUEST",
    "details": {}
}

Common Error Codes:
- INVALID_REQUEST: Invalid request parameters
- UNAUTHORIZED: Missing or invalid authentication
- FORBIDDEN: Insufficient permissions
- NOT_FOUND: Resource not found
- CONFLICT: Resource already exists
- RATE_LIMIT: Too many requests
- SERVER_ERROR: Internal server error
"""


# ============================================================
# 7. AUTHENTICATION
# ============================================================

"""
JWT Authentication Header:
Authorization: Bearer <jwt_token>

Get JWT Token:
POST /auth/login
{
    "username": "admin",
    "password": "password"
}

Response:
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 3600
}
"""

print("""
✅ PHASE 2 WEB PANEL API DOCUMENTATION CREATED

Key Endpoints:
✓ Coin Management: /api/coins/* (transactions, balance, leaderboard)
✓ User Management: /api/users/* (list, details, status)
✓ Broadcasting: /api/broadcasts (create, history)
✓ Subscriptions: /api/subscriptions/* (plans, purchase)
✓ Analytics: /api/analytics/* (downloads, revenue)

Total Endpoints: 15+
Authentication: JWT Token
Admin Features: User management, coin awards, broadcasts
Public Features: Plans, leaderboard

Ready to implement!
""")
