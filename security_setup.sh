#!/bin/bash

# =============================================================================
# Security Setup Script
# Automatically configures security features for the application
# =============================================================================

set -e  # Exit on error

echo "=================================================="
echo "🔒 STONKS APPLICATION - SECURITY SETUP"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    cp .env.example .env
    
    # Generate SECRET_KEY
    echo ""
    echo "Generating secure SECRET_KEY..."
    SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_hex(32))')
    
    # Update .env with generated key
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    else
        # Linux
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
    fi
    
    echo -e "${GREEN}✓ Generated and saved SECRET_KEY${NC}"
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Check Python version
echo ""
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python $PYTHON_VERSION${NC}"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo ""
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source .venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Install/upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install requirements
echo ""
echo "Installing required packages..."
pip install -r requirements.txt
echo -e "${GREEN}✓ All packages installed${NC}"

# Create logs directory
echo ""
echo "Creating logs directory..."
mkdir -p logs
echo -e "${GREEN}✓ Logs directory created${NC}"

# Run database migration
echo ""
echo "Running database migration..."
python3 migrate_security.py << EOF
yes
EOF
echo -e "${GREEN}✓ Database migration complete${NC}"

# Verify installation
echo ""
echo "Verifying security installation..."
python3 << 'VERIFY_EOF'
from app import create_app
from app.models.user import User
from app.utils.password_security import PasswordValidator

app = create_app()
errors = []

# Check SECRET_KEY
secret_key = app.config.get('SECRET_KEY')
if not secret_key or len(secret_key) < 32 or secret_key == 'CHANGE_THIS_TO_A_RANDOM_SECRET_KEY_IN_PRODUCTION':
    errors.append("SECRET_KEY is not properly configured")

# Check CSRF
if not app.config.get('WTF_CSRF_ENABLED'):
    errors.append("CSRF protection is not enabled")

# Check session security
if not app.config.get('SESSION_COOKIE_HTTPONLY'):
    errors.append("HTTPOnly cookies not enabled")

# Check User model
with app.app_context():
    if not hasattr(User, 'failed_login_attempts'):
        errors.append("User security fields not added")

# Check password validator
try:
    validator = PasswordValidator()
    is_valid, _ = validator.validate('WeakPass')
    if is_valid:
        errors.append("Password validation not working correctly")
except Exception as e:
    errors.append(f"Password validator error: {e}")

if errors:
    print("❌ VERIFICATION FAILED:")
    for error in errors:
        print(f"  - {error}")
    exit(1)
else:
    print("✅ ALL SECURITY CHECKS PASSED!")

VERIFY_EOF

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Security verification passed${NC}"
else
    echo -e "${RED}✗ Security verification failed${NC}"
    exit 1
fi

# Summary
echo ""
echo "=================================================="
echo "🎉 SECURITY SETUP COMPLETE!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Review and update .env file with your settings"
echo "2. Add {{ csrf_token() }} to all form templates"
echo "3. Test the application: python main.py"
echo "4. Review SECURITY_IMPLEMENTATION_COMPLETE.md"
echo ""
echo "To start the application:"
echo "  source .venv/bin/activate"
echo "  python main.py"
echo ""
echo "=================================================="
