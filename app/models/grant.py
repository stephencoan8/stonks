"""
Grant model for stock compensation grants.
"""

from app import db
from datetime import datetime
from enum import Enum


class GrantType(str, Enum):
    """Types of grants available."""
    NEW_HIRE = "new_hire"
    ANNUAL_PERFORMANCE = "annual_performance"
    PROMOTION = "promotion"
    KICKASS = "kickass"
    ESPP = "espp"
    NQESPP = "nqespp"


class ShareType(str, Enum):
    """Types of shares."""
    RSU = "rsu"
    ISO_5Y = "iso_5y"
    ISO_6Y = "iso_6y"
    CASH = "cash"


class BonusType(str, Enum):
    """Bonus payout types."""
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"


class Grant(db.Model):
    """Grant model representing a stock compensation grant."""
    
    __tablename__ = 'grants'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Grant details
    grant_date = db.Column(db.Date, nullable=False)
    grant_type = db.Column(db.String(50), nullable=False)
    share_type = db.Column(db.String(20), nullable=False)
    share_quantity = db.Column(db.Float, nullable=False)
    share_price_at_grant = db.Column(db.Float, nullable=False)
    
    # Vesting details
    vest_years = db.Column(db.Integer, nullable=False)
    cliff_years = db.Column(db.Float, nullable=False)
    
    # For annual performance grants
    bonus_type = db.Column(db.String(20), nullable=True)  # short_term or long_term
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    vest_events = db.relationship('VestEvent', backref='grant', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self) -> str:
        return f'<Grant {self.grant_type} - {self.share_quantity} {self.share_type}>'
    
    @property
    def total_value_at_grant(self) -> float:
        """Calculate total value at grant."""
        return self.share_quantity * self.share_price_at_grant
