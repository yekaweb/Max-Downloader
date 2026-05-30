# Alembic Migrations Setup - PHASE 2 Item 2.7

## Overview

Initial database schema migration has been generated with all models:
- Users (with referral milestone tracking)
- Downloads
- CachedFiles (with unique constraints)
- Plans
- Subscriptions
- Referrals
- CoinTransactions
- Payments
- Channels

## Migration Files

### File Structure
```
migrations/
├── env.py                          # Alembic environment configuration
├── versions/
│   ├── __init__.py
│   ├── 001_initial_schema.py       # Placeholder (keep for reference)
│   └── 001_initial_schema_complete.py  # ✅ ACTIVE - Contains all tables
```

### Migration Details

**File**: `migrations/versions/001_initial_schema_complete.py`
- **Revision**: 001 (initial)
- **Tables**: 9 (users, downloads, cached_files, plans, subscriptions, referrals, coin_transactions, payments, channels)
- **Indexes**: 25+ indexes for query optimization
- **Constraints**: Primary keys, foreign keys, unique constraints

## Usage

### Generate New Migration

After making model changes:
```bash
# Generate auto migration
alembic revision --autogenerate -m "Description of changes"

# Or manual migration
alembic revision -m "Description of changes"
```

### Apply Migrations

```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade <revision_id>

# Downgrade one step
alembic downgrade -1

# Downgrade all
alembic downgrade base
```

### Check Current Status

```bash
# Show current migration state
alembic current

# Show migration history
alembic history --oneline

# Show SQL that would be executed
alembic upgrade head --sql
```

## Configuration

**File**: `migrations/env.py`
- Uses `settings.db.dsn` from `config.py`
- Supports both offline and online modes
- Imports `Base` from `database.models`

**File**: `alembic.ini`
- Contains database URL and configuration
- Set by environment variables at runtime

## Important Notes

### 1. CachedFile Unique Constraint
```sql
UniqueConstraint('url_hash', 'format_id', 'codec', name='uq_cached_files_lookup')
```
- Prevents duplicate caches
- Ensures (url_hash, format_id, codec) triplet is unique
- Allows efficient cache lookups

### 2. User Referral Fields
```python
referral_milestone = Column(Integer)    # Last milestone reached (1, 5, 10, 20, 50)
referral_badge = Column(String(50))     # Current badge
```
- Added for milestone-based rewards
- Updated automatically by ReferralService

### 3. Indexes for Performance
- `ix_users_created_at`: For user timeline queries
- `ix_cached_files_platform_video`: For quick cache lookups
- `ix_payments_created_at`: For transaction history
- `ix_coin_transactions_user_id`: For user coin history

## Testing Migrations

### Test Upgrade
```bash
# Apply migration
alembic upgrade head

# Verify tables exist
psql dlbot_db -c "\dt"
```

### Test Downgrade
```bash
# Downgrade all
alembic downgrade base

# Verify tables removed
psql dlbot_db -c "\dt"
```

### Verify Schema
```bash
# Check table structure
psql dlbot_db -c "\d users"
psql dlbot_db -c "\d cached_files"

# Check constraints
psql dlbot_db -c "SELECT * FROM information_schema.table_constraints WHERE table_name = 'cached_files';"
```

## Best Practices

1. ✅ Always generate migration after model changes
2. ✅ Review generated migrations before applying
3. ✅ Test upgrade AND downgrade
4. ✅ Keep migrations in version control
5. ✅ Use descriptive revision messages
6. ✅ Never manually edit auto-generated migrations in production

## Troubleshooting

### Issue: "target_metadata not set"
- Solution: Check `env.py` imports `Base` correctly
- Ensure `database.models` is in Python path

### Issue: "No migrations detected"
- Solution: Check `versions/` directory exists
- Ensure migration file names follow convention: `###_description.py`

### Issue: Foreign key constraint failure
- Solution: Check tables are created in correct order (parent before child)
- Migration handles this automatically

## Next Steps

1. ✅ Initial migration created and tested
2. ⏳ Next: When models change, run `alembic revision --autogenerate`
3. ⏳ Before deployment: Review and test all migrations
4. ⏳ Production: Apply migrations during deployment phase
