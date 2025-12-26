"""
Security decorators for route protection and access control.
"""

from functools import wraps
from flask import abort, redirect, url_for, flash
from flask_login import current_user
from app.utils.audit_log import AuditLogger


def admin_required(f):
    """
    Decorator to require admin privileges for a route.
    
    Usage:
        @admin_required
        def admin_only_view():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin:
            AuditLogger.log_security_event('UNAUTHORIZED_ADMIN_ACCESS_ATTEMPT', {
                'user_id': current_user.id,
                'username': current_user.username,
                'route': f.__name__
            })
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def owns_resource(model_class, id_param='id', foreign_key='user_id'):
    """
    Decorator to verify user owns the requested resource.
    
    Args:
        model_class: The SQLAlchemy model class
        id_param: The URL parameter containing the resource ID
        foreign_key: The foreign key field that links to user
        
    Usage:
        @owns_resource(Grant, id_param='grant_id', foreign_key='user_id')
        def edit_grant(grant_id):
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('auth.login'))
            
            resource_id = kwargs.get(id_param)
            if not resource_id:
                abort(404)
            
            resource = model_class.query.get_or_404(resource_id)
            
            # Check ownership (unless admin)
            if not current_user.is_admin and getattr(resource, foreign_key) != current_user.id:
                AuditLogger.log_security_event('UNAUTHORIZED_RESOURCE_ACCESS', {
                    'user_id': current_user.id,
                    'resource_type': model_class.__name__,
                    'resource_id': resource_id,
                    'owner_id': getattr(resource, foreign_key)
                })
                abort(403)
            
            # Add resource to kwargs for convenience
            kwargs[model_class.__name__.lower()] = resource
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def role_required(*roles):
    """
    Decorator to require specific roles for a route.
    
    Usage:
        @role_required('admin', 'manager')
        def manager_view():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('auth.login'))
            
            user_role = getattr(current_user, 'role', None)
            if user_role not in roles:
                AuditLogger.log_security_event('UNAUTHORIZED_ROLE_ACCESS', {
                    'user_id': current_user.id,
                    'required_roles': roles,
                    'user_role': user_role,
                    'route': f.__name__
                })
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def verified_email_required(f):
    """
    Decorator to require verified email.
    
    Usage:
        @verified_email_required
        def sensitive_action():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        
        if hasattr(current_user, 'email_verified') and not current_user.email_verified:
            flash('Please verify your email address to access this feature.', 'warning')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function


def rate_limit_user(limit: str):
    """
    Per-user rate limiting decorator.
    
    Args:
        limit: Rate limit string (e.g., "10 per minute")
        
    Usage:
        @rate_limit_user("5 per minute")
        def expensive_operation():
            ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This would integrate with Flask-Limiter
            # For now, just pass through
            return f(*args, **kwargs)
        return decorated_function
    return decorator
