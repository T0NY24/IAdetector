"""
API Route: History
Retrieve forensic analysis history from database.
"""
import logging
from flask import Blueprint, jsonify, request

from backend import database

logger = logging.getLogger(__name__)
bp = Blueprint('history', __name__)


@bp.route('/history', methods=['GET'])
def get_history():
    """
    Get analysis history.
    
    Query Parameters:
        limit: Maximum number of records to return (default: 50)
        
    Returns:
        JSON with total count and results array
    """
    try:
        # Get limit parameter
        limit = request.args.get('limit', 50, type=int)
        
        # Validate limit
        if limit < 1 or limit > 200:
            return jsonify({"error": "Limit must be between 1 and 200"}), 400
        
        # Get history from database
        history = database.get_history(limit=limit)
        
        # Get stats
        stats = database.get_stats()
        
        return jsonify({
            "total": stats['total'],
            "returned": len(history),
            "stats": stats['by_type'],
            "results": history
        })
        
    except Exception as e:
        logger.error(f"Error retrieving history: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@bp.route('/history/stats', methods=['GET'])
def get_stats():
    """
    Get database statistics.
    
    Returns:
        JSON with count statistics by media type
    """
    try:
        stats = database.get_stats()
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Error retrieving stats: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
