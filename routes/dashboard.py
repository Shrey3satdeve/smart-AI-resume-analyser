"""
routes/dashboard.py

Displays historical data of all analyzed resumes.
Provides filters for categories and sorting options.
"""

from flask import Blueprint, render_template, request
from database.db import get_all_candidates

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard")
def view_dashboard():
    candidates = get_all_candidates()
    
    # Simple category filtering
    category = request.args.get("category")
    if category:
        candidates = [c for c in candidates if c["prediction"] == category]
        
    # Get unique categories for filter dropdown
    categories = sorted(list(set(c["prediction"] for c in get_all_candidates() if c["prediction"])))
    
    return render_template("dashboard.html", candidates=candidates, categories=categories)
