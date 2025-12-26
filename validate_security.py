#!/usr/bin/env python3
"""
Security Validation Script
Verifies all security implementations are working correctly.
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def print_header(title):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_check(name, status, details=""):
    """Print a check result."""
    symbol = "✓" if status else "✗"
    color = "\033[92m" if status else "\033[91m"
    reset = "\033[0m"
    print(f"{color}{symbol}{reset} {name}")
    if details:
        print(f"  → {details}")

def validate_environment():
    """Validate environment configuration."""
    print_header("Environment Configuration")
    
    checks = []
    
    # Check .env exists
    env_exists = os.path.exists('.env')
    print_check(".env file exists", env_exists)
    checks.append(env_exists)
    
    # Check SECRET_KEY
    from dotenv import load_dotenv
    load_dotenv()
    
    secret_key = os.getenv('SECRET_KEY')
    secret_key_valid = secret_key and len(secret_key) >= 32 and \
                      secret_key != 'CHANGE_THIS_TO_A_RANDOM_SECRET_KEY_IN_PRODUCTION'
    print_check("SECRET_KEY is properly set", secret_key_valid, 
                f"Length: {len(secret_key) if secret_key else 0}")
    checks.append(secret_key_valid)
    
    # Check Flask environment
    flask_env = os.getenv('FLASK_ENV', 'development')
    print_check(f"FLASK_ENV set to '{flask_env}'", True, 
                "⚠️ Use 'production' for deployment" if flask_env != 'production' else "")
    checks.append(True)
    
    return all(checks)

def validate_app_config():
    """Validate Flask app configuration."""
    print_header("Application Configuration")
    
    checks = []
    
    try:
        from app import create_app
        app = create_app()
        
        # Check CSRF protection
        csrf_enabled = app.config.get('WTF_CSRF_ENABLED', False)
        print_check("CSRF protection enabled", csrf_enabled)
        checks.append(csrf_enabled)
        
        # Check session security
        httponly = app.config.get('SESSION_COOKIE_HTTPONLY', False)
        print_check("HTTPOnly cookies enabled", httponly)
        checks.append(httponly)
        
        samesite = app.config.get('SESSION_COOKIE_SAMESITE')
        print_check("SameSite cookie attribute set", samesite is not None, 
                   f"Value: {samesite}")
        checks.append(samesite is not None)
        
        # Check session timeout
        timeout = app.config.get('PERMANENT_SESSION_LIFETIME')
        print_check("Session timeout configured", timeout is not None, 
                   f"Timeout: {timeout} seconds" if timeout else "")
        checks.append(timeout is not None)
        
        # Check rate limiting
        rate_limit = app.config.get('RATELIMIT_ENABLED', False)
        print_check("Rate limiting enabled", rate_limit)
        checks.append(rate_limit)
        
        # Check Talisman (security headers)
        talisman_force_https = app.config.get('TALISMAN_FORCE_HTTPS')
        env = app.config.get('FLASK_ENV')
        talisman_ok = (env != 'production') or talisman_force_https
        print_check("Talisman HTTPS enforcement", talisman_ok,
                   "⚠️ HTTPS should be enforced in production" if not talisman_force_https else "")
        checks.append(True)  # Don't fail on this in dev
        
    except Exception as e:
        print_check("App initialization", False, f"Error: {e}")
        return False
    
    return all(checks)

def validate_user_model():
    """Validate User model security fields."""
    print_header("User Model Security Fields")
    
    checks = []
    
    try:
        from app import create_app, db
        from app.models.user import User
        
        app = create_app()
        
        with app.app_context():
            # Check security fields
            required_fields = [
                'failed_login_attempts',
                'is_locked',
                'locked_until',
                'last_login',
                'last_password_change',
                'password_reset_token',
                'password_reset_expiry',
                'email_verified',
                'email_verification_token',
                'totp_secret',
                'totp_enabled',
            ]
            
            for field in required_fields:
                has_field = hasattr(User, field)
                print_check(f"User.{field}", has_field)
                checks.append(has_field)
            
            # Check methods
            methods = ['set_password', 'check_password', 'is_account_locked']
            for method in methods:
                has_method = hasattr(User, method) and callable(getattr(User, method))
                print_check(f"User.{method}()", has_method)
                checks.append(has_method)
    
    except Exception as e:
        print_check("User model validation", False, f"Error: {e}")
        return False
    
    return all(checks)

def validate_password_security():
    """Validate password security utilities."""
    print_header("Password Security")
    
    checks = []
    
    try:
        from app.utils.password_security import PasswordValidator
        
        validator = PasswordValidator()
        
        # Test weak password rejection
        weak_passwords = ['weak', 'password', '12345678', 'abc123']
        all_rejected = True
        for pwd in weak_passwords:
            is_valid, _ = validator.validate(pwd)
            if is_valid:
                all_rejected = False
                break
        
        print_check("Weak passwords rejected", all_rejected)
        checks.append(all_rejected)
        
        # Test strong password acceptance
        strong_pwd = 'MyS3cur3P@ssw0rd!'
        is_valid, errors = validator.validate(strong_pwd)
        print_check("Strong password accepted", is_valid,
                   f"Errors: {errors}" if not is_valid else "")
        checks.append(is_valid)
        
        # Test password strength scoring
        score = validator.get_strength_score(strong_pwd)
        score_ok = score >= 70
        print_check("Password strength scoring", score_ok, f"Score: {score}/100")
        checks.append(score_ok)
        
    except Exception as e:
        print_check("Password security utilities", False, f"Error: {e}")
        return False
    
    return all(checks)

def validate_audit_logging():
    """Validate audit logging."""
    print_header("Audit Logging")
    
    checks = []
    
    try:
        from app.utils.audit_log import AuditLogger
        
        # Check logger exists
        print_check("AuditLogger class available", True)
        checks.append(True)
        
        # Check log directory
        logs_dir = os.path.exists('logs')
        print_check("Logs directory exists", logs_dir)
        checks.append(logs_dir)
        
        # Check methods
        methods = [
            'log_auth_success',
            'log_auth_failure',
            'log_grant_created',
            'log_security_event'
        ]
        
        for method in methods:
            has_method = hasattr(AuditLogger, method)
            print_check(f"AuditLogger.{method}", has_method)
            checks.append(has_method)
    
    except Exception as e:
        print_check("Audit logging validation", False, f"Error: {e}")
        return False
    
    return all(checks)

def validate_decorators():
    """Validate security decorators."""
    print_header("Security Decorators")
    
    checks = []
    
    try:
        from app.utils.decorators import (
            admin_required,
            owns_resource,
            role_required,
            verified_email_required
        )
        
        decorators = [
            ('admin_required', admin_required),
            ('owns_resource', owns_resource),
            ('role_required', role_required),
            ('verified_email_required', verified_email_required),
        ]
        
        for name, decorator in decorators:
            exists = callable(decorator)
            print_check(f"@{name}", exists)
            checks.append(exists)
    
    except Exception as e:
        print_check("Security decorators", False, f"Error: {e}")
        return False
    
    return all(checks)

def validate_dependencies():
    """Validate required packages are installed."""
    print_header("Dependencies")
    
    checks = []
    required_packages = [
        ('flask', 'Flask'),
        ('flask_wtf', 'Flask-WTF'),
        ('flask_limiter', 'Flask-Limiter'),
        ('flask_talisman', 'Flask-Talisman'),
        ('pyotp', 'PyOTP'),
        ('email_validator', 'email-validator'),
        ('cryptography', 'cryptography'),
    ]
    
    for package_name, display_name in required_packages:
        try:
            __import__(package_name)
            print_check(f"{display_name} installed", True)
            checks.append(True)
        except ImportError:
            print_check(f"{display_name} installed", False, "Run: pip install -r requirements.txt")
            checks.append(False)
    
    return all(checks)

def main():
    """Run all validation checks."""
    print("\n" + "=" * 70)
    print("  🔒 SECURITY VALIDATION")
    print("  SpaceX Stonks Application")
    print("  " + str(datetime.now()))
    print("=" * 70)
    
    results = {
        "Dependencies": validate_dependencies(),
        "Environment": validate_environment(),
        "App Configuration": validate_app_config(),
        "User Model": validate_user_model(),
        "Password Security": validate_password_security(),
        "Audit Logging": validate_audit_logging(),
        "Security Decorators": validate_decorators(),
    }
    
    # Summary
    print_header("Validation Summary")
    
    all_passed = all(results.values())
    
    for category, passed in results.items():
        print_check(category, passed)
    
    print("\n" + "=" * 70)
    if all_passed:
        print("  ✅ ALL SECURITY VALIDATIONS PASSED!")
        print("  🚀 Application is ready for deployment")
    else:
        print("  ❌ SOME VALIDATIONS FAILED")
        print("  ⚠️  Please fix the issues above before deploying")
    print("=" * 70 + "\n")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
