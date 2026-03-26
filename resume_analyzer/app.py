"""
app.py

Main entry point for the Smart AI Resume Analyzer.
Initializes Flask, registers blueprints, sets up the database,
and defines custom template filters for handling JSON-serialized lists.
"""

import os
import json
from flask import Flask, render_template
from config import UPLOAD_FOLDER, SECRET_KEY
from database.db import create_tables

# Import Blueprints
from routes.upload import upload_bp
from routes.analyze import analyze_bp
from routes.dashboard import dashboard_bp

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.secret_key = SECRET_KEY
    
    # Ensure upload directory exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # ─── Register Blueprints ──────────────────────────────────────────────────
    app.register_blueprint(upload_bp)
    app.register_blueprint(analyze_bp)
    app.register_blueprint(dashboard_bp)

    # ─── Custom Template Filters ──────────────────────────────────────────────
    @app.template_filter('from_json')
    def from_json_filter(value):
        """Parse JSON string back to list/dict in templates."""
        try:
            return json.loads(value) if value else []
        except:
            return []

    # ─── Error Handlers ───────────────────────────────────────────────────────
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', content="Error 404: Page Not Found"), 404

    return app

if __name__ == "__main__":
    # Initialize Database
    print("Initializing SQLite Database...")
    create_tables()
    
    # Create and Run App
    app = create_app()
    print("\n🚀 Smart AI Resume Analyzer is starting...")
    print("URL: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
