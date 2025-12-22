"""
Stock price model for tracking SpaceX stock valuations.
"""

from app import db
from datetime import datetime


class StockPrice(db.Model):
    """Stock price history for SpaceX."""
    
    __tablename__ = 'stock_prices'
    
    id = db.Column(db.Integer, primary_key=True)
    valuation_date = db.Column(db.Date, nullable=False, unique=True, index=True)
    price_per_share = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    def __repr__(self) -> str:
        return f'<StockPrice {self.valuation_date} - ${self.price_per_share}>'
