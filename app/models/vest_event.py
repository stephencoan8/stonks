"""
Vest event model for tracking individual vesting events.
"""

from app import db
from datetime import datetime, date


class VestEvent(db.Model):
    """Individual vesting event for a grant."""
    
    __tablename__ = 'vest_events'
    
    id = db.Column(db.Integer, primary_key=True)
    grant_id = db.Column(db.Integer, db.ForeignKey('grants.id'), nullable=False, index=True)
    
    # Vest details
    vest_date = db.Column(db.Date, nullable=False)
    shares_vested = db.Column(db.Float, nullable=False)
    share_price_at_vest = db.Column(db.Float, nullable=True)
    
    # Tax handling
    payment_method = db.Column(db.String(20), default='sell_to_cover')  # 'sell_to_cover' or 'cash_to_cover'
    cash_to_cover = db.Column(db.Float, default=0.0)
    shares_sold_to_cover = db.Column(db.Float, default=0.0)
    
    # Status
    is_vested = db.Column(db.Boolean, default=False)
    vested_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f'<VestEvent {self.vest_date} - {self.shares_vested} shares>'
    
    @property
    def has_vested(self) -> bool:
        """Check if vest date has passed (based on today's date)."""
        return self.vest_date <= date.today()
    
    @property
    def needs_tax_info(self) -> bool:
        """Check if vested event is missing tax payment information."""
        if not self.has_vested:
            return False
        # Need info if vested but no cash or shares specified
        return self.cash_to_cover == 0 and self.shares_sold_to_cover == 0
    
    @property
    def value_at_vest(self) -> float:
        """Calculate value at vest."""
        if self.share_price_at_vest:
            return self.shares_vested * self.share_price_at_vest
        return 0.0
    
    @property
    def shares_withheld_for_taxes(self) -> float:
        """Calculate total shares withheld/sold for taxes."""
        if self.payment_method == 'cash_to_cover' and self.cash_to_cover > 0 and self.share_price_at_vest:
            # Convert cash paid to equivalent shares
            return self.cash_to_cover / self.share_price_at_vest
        elif self.payment_method == 'sell_to_cover':
            return self.shares_sold_to_cover
        return 0.0
    
    @property
    def shares_received(self) -> float:
        """Calculate actual shares physically received after taxes."""
        return self.shares_vested - self.shares_withheld_for_taxes
    
    @property
    def net_value(self) -> float:
        """Calculate net value of shares received."""
        if self.share_price_at_vest:
            return self.shares_received * self.share_price_at_vest
        return 0.0
