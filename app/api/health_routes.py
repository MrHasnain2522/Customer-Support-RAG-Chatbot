"""
Health check routes
"""
from flask import Blueprint, jsonify
from app import db
from datetime import datetime

health_bp = Blueprint('health', __name__)


@health_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint
    Returns API status and database connectivity
    """
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        db_status = 'connected'
    except Exception as e:
        db_status = f'error: {str(e)}'
    
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': db_status,
        'service': 'backend-api'
    }), 200


@health_bp.route('/ping', methods=['GET'])
def ping():
    """
    Simple ping endpoint
    """
    return jsonify({'message': 'pong'}), 200