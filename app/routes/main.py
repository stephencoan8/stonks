"""
Main application routes - dashboard, home page.
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models.grant import Grant
from app.models.vest_event import VestEvent
from app.utils.init_db import get_latest_stock_price
from datetime import date
from sqlalchemy import func

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """User dashboard showing grant summary."""
    # Get user's grants
    grants = Grant.query.filter_by(user_id=current_user.id).all()
    
    # Calculate totals
    total_grants = len(grants)
    total_shares = sum(g.share_quantity for g in grants)
    current_price = get_latest_stock_price()
    total_value = total_shares * current_price
    
    # Get upcoming vests (vest_date in the future)
    upcoming_vests = VestEvent.query.join(Grant).filter(
        Grant.user_id == current_user.id,
        VestEvent.vest_date >= date.today()
    ).order_by(VestEvent.vest_date).limit(5).all()
    
    # Get ALL vest events and filter by has_vested property (vest_date in the past)
    all_vest_events = VestEvent.query.join(Grant).filter(
        Grant.user_id == current_user.id
    ).order_by(VestEvent.vest_date).all()
    
    # Filter vested events using the has_vested property
    vested_events = [v for v in all_vest_events if v.has_vested]
    vested_shares_gross = sum(v.shares_vested for v in vested_events)
    vested_shares_net = sum(v.shares_received for v in vested_events)
    vested_value_gross = vested_shares_gross * current_price
    vested_value_net = vested_shares_net * current_price
    
    # Prepare vesting timeline data for chart
    vesting_timeline = []
    cumulative_vested = 0
    cumulative_total = 0
    
    for vest in all_vest_events:
        cumulative_total += vest.shares_received  # Use net shares received
        if vest.has_vested:
            cumulative_vested += vest.shares_received
        
        vesting_timeline.append({
            'date': vest.vest_date.strftime('%Y-%m-%d'),
            'vested': cumulative_vested,
            'total': cumulative_total,
            'is_vested': vest.has_vested,
            'shares': vest.shares_received
        })
    
    return render_template('main/dashboard.html',
                         total_grants=total_grants,
                         total_shares=total_shares,
                         total_value=total_value,
                         vested_shares_gross=vested_shares_gross,
                         vested_shares_net=vested_shares_net,
                         vested_value_gross=vested_value_gross,
                         vested_value_net=vested_value_net,
                         upcoming_vests=upcoming_vests,
                         current_price=current_price,
                         vesting_timeline=vesting_timeline)
