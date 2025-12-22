"""
Database initialization utilities.
"""

from app import db
from app.models.user import User
from app.models.stock_price import StockPrice
from datetime import date
import os


def init_admin_user():
    """Create admin user if it doesn't exist."""
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin')
    
    admin = User.query.filter_by(username=admin_username).first()
    if not admin:
        admin = User(
            username=admin_username,
            email='admin@spacex.com',
            is_admin=True
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin user created: {admin_username}")


def init_stock_prices():
    """Initialize with a default stock price if none exist."""
    price_count = StockPrice.query.count()
    if price_count == 0:
        initial_price = StockPrice(
            valuation_date=date.today(),
            price_per_share=100.0,
            notes='Initial stock price - update via admin panel'
        )
        db.session.add(initial_price)
        db.session.commit()
        print("Initial stock price created: $100.00")


def get_stock_price_at_date(target_date: date) -> float:
    """
    Get the stock price at or before a specific date.
    
    Args:
        target_date: The date to find the price for
        
    Returns:
        The stock price per share
    """
    price = StockPrice.query.filter(
        StockPrice.valuation_date <= target_date
    ).order_by(StockPrice.valuation_date.desc()).first()
    
    if price:
        return price.price_per_share
    
    # Fallback to earliest price if date is before all records
    earliest = StockPrice.query.order_by(StockPrice.valuation_date.asc()).first()
    return earliest.price_per_share if earliest else 100.0


def get_latest_stock_price() -> float:
    """Get the most recent stock price."""
    price = StockPrice.query.order_by(StockPrice.valuation_date.desc()).first()
    return price.price_per_share if price else 100.0
