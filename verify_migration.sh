#!/bin/bash
# Quick verification script for migration success

echo ""
echo "=============================================="
echo "🔍 Migration Verification Script"
echo "=============================================="
echo ""

# Check database exists
echo "📁 Checking database files..."
if [ -f "instance/stonks.db" ]; then
    echo "   ✅ New database exists: instance/stonks.db"
else
    echo "   ❌ New database NOT found!"
    exit 1
fi

if [ -f "instance/stonks.db.backup" ]; then
    echo "   ✅ Backup database preserved: instance/stonks.db.backup"
else
    echo "   ⚠️  Backup database not found!"
fi

echo ""
echo "📊 Checking record counts..."

# Count records
USERS=$(sqlite3 instance/stonks.db "SELECT COUNT(*) FROM users;")
GRANTS=$(sqlite3 instance/stonks.db "SELECT COUNT(*) FROM grants;")
VESTS=$(sqlite3 instance/stonks.db "SELECT COUNT(*) FROM vest_events;")

echo "   Users: $USERS (expected: 3)"
echo "   Grants: $GRANTS (expected: 16)"
echo "   Vest Events: $VESTS (expected: 183)"

# Verify counts
if [ "$USERS" -eq 3 ] && [ "$GRANTS" -eq 16 ] && [ "$VESTS" -eq 183 ]; then
    echo "   ✅ All counts match!"
else
    echo "   ⚠️  Count mismatch detected!"
fi

echo ""
echo "👥 User details..."
sqlite3 instance/stonks.db "SELECT username, email, is_admin FROM users ORDER BY id;" | while read line; do
    echo "   - $line"
done

echo ""
echo "📈 Grant summary by user..."
sqlite3 instance/stonks.db "
    SELECT u.username, COUNT(g.id) as grant_count, COUNT(DISTINCT v.id) as vest_count
    FROM users u
    LEFT JOIN grants g ON u.id = g.user_id
    LEFT JOIN vest_events v ON g.id = v.grant_id
    GROUP BY u.username
    ORDER BY u.id;
" | while read line; do
    echo "   - $line"
done

echo ""
echo "🔐 Security fields initialized..."
HAS_SECURITY=$(sqlite3 instance/stonks.db "SELECT COUNT(*) FROM users WHERE failed_login_attempts IS NOT NULL AND is_locked IS NOT NULL;")
echo "   Security fields present: $HAS_SECURITY/3 users"

if [ "$HAS_SECURITY" -eq 3 ]; then
    echo "   ✅ All users have security fields"
else
    echo "   ⚠️  Some users missing security fields"
fi

echo ""
echo "=============================================="
echo "🎉 Verification Complete!"
echo "=============================================="
echo ""
echo "Next steps:"
echo "  1. Start app: PORT=5001 python main.py"
echo "  2. Open browser: http://127.0.0.1:5001"
echo "  3. Login with: admin / admin"
echo ""
