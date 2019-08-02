# -*- encoding: utf-8 -*-
"""
Flask application start
"""
from app import app
from app import db


if __name__ == "__main__":
    """
    Application start
    """
    db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
