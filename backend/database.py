"""
Database Module - UIDE Forense AI
Polymorphic SQLite database for analysis history (IMAGE, VIDEO, AUDIO)

Schema Design:
- Single table with flexible meta_1/meta_2 columns
- Full JSON backup for data integrity
- Type-specific mapping logic
"""

import os
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Database path (relative to backend directory)
DB_DIR = Path(__file__).parent / "data"
DB_PATH = DB_DIR / "forensics.db"


def init_db():
    """
    Initialize database and create analysis_history table if it doesn't exist.
    
    Schema:
        - id: Primary key
        - filename: Original file name
        - media_type: 'IMAGE', 'VIDEO', or 'AUDIO'
        - timestamp: ISO format timestamp
        - verdict: Text verdict from analysis
        - ai_probability: Float (0-100) AI confidence
        - meta_1: Polymorphic field (type-dependent)
        - meta_2: Polymorphic field (type-dependent)
        - notes: Additional notes/reasoning
        - full_report_json: Complete result as JSON string
    """
    # Ensure data directory exists
    DB_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                media_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                verdict TEXT NOT NULL,
                ai_probability REAL,
                meta_1 REAL,
                meta_2 REAL,
                notes TEXT,
                full_report_json TEXT NOT NULL
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON analysis_history(timestamp DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_media_type 
            ON analysis_history(media_type)
        """)
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Database initialized: {DB_PATH}")
        
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise


def insert_analysis(filename: str, media_type: str, result: Dict[str, Any]) -> Optional[int]:
    """
    Insert analysis result into database with polymorphic field mapping.
    
    Mapping Logic:
        IMAGE:  meta_1 = MultiLID score, meta_2 = UFD score
        VIDEO:  meta_1 = duration (seconds), meta_2 = frames_analyzed
        AUDIO:  meta_1 = duration (seconds), meta_2 = confidence score
    
    Args:
        filename: Original file name
        media_type: 'IMAGE', 'VIDEO', or 'AUDIO'
        result: Result dictionary from detector
        
    Returns:
        Inserted row ID or None if error
    """
    try:
        # Extract common fields
        verdict = result.get('verdict', 'UNKNOWN')
        notes = result.get('notes', '')
        
        # Type-specific field mapping
        ai_probability = None
        meta_1 = None
        meta_2 = None
        
        if media_type == 'IMAGE':
            # For images: extract from ForensicResult
            scores = result.get('scores', {})
            ai_probability = scores.get('ai_probability', scores.get('unified', 0.0)) * 100
            meta_1 = scores.get('MultiLID', 0.0)  # MultiLID score
            meta_2 = scores.get('UFD', 0.0)  # UFD score
            
            # If notes is empty, use evidence
            if not notes and 'evidence' in result:
                notes = ' | '.join(result['evidence'])
        
        elif media_type == 'VIDEO':
            # For videos: probability, duration, frames
            ai_probability = result.get('probability', 0.0)
            meta_1 = result.get('duration', 0.0)  # Duration in seconds
            meta_2 = float(result.get('frames_analyzed', 0))  # Frames analyzed
            
        elif media_type == 'AUDIO':
            # For audio: score, duration, confidence
            ai_probability = result.get('score', 0.0)
            meta_1 = result.get('duration_analyzed', 0.0)  # Duration in seconds
            meta_2 = result.get('confidence', 0.0)  # Confidence score
        
        # Generate timestamp
        timestamp = datetime.utcnow().isoformat()
        
        # Serialize full report
        full_report_json = json.dumps(result, ensure_ascii=False)
        
        # Insert into database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO analysis_history 
            (filename, media_type, timestamp, verdict, ai_probability, meta_1, meta_2, notes, full_report_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            filename,
            media_type,
            timestamp,
            verdict,
            ai_probability,
            meta_1,
            meta_2,
            notes,
            full_report_json
        ))
        
        row_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Analysis saved to DB: {filename} ({media_type}) - ID: {row_id}")
        return row_id
        
    except Exception as e:
        logger.error(f"❌ Error inserting analysis: {e}", exc_info=True)
        return None


def get_history(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Retrieve analysis history with formatted details.
    
    Args:
        limit: Maximum number of records to return (default: 50)
        
    Returns:
        List of formatted history records
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, filename, media_type, timestamp, verdict, 
                   ai_probability, meta_1, meta_2, notes, full_report_json
            FROM analysis_history
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        # Format results
        results = []
        for row in rows:
            # Parse full report for additional context if needed
            try:
                full_report = json.loads(row['full_report_json'])
            except:
                full_report = {}
            
            # Format details based on media type
            details = ""
            media_type = row['media_type']
            
            if media_type == 'IMAGE':
                details = f"MultiLID: {row['meta_1']:.3f}, UFD: {row['meta_2']:.3f}"
            elif media_type == 'VIDEO':
                details = f"Duración: {row['meta_1']:.1f}s, Frames: {int(row['meta_2'])}"
            elif media_type == 'AUDIO':
                details = f"Duración: {row['meta_1']:.1f}s, Confianza: {row['meta_2']:.1f}%"
            
            results.append({
                'id': row['id'],
                'filename': row['filename'],
                'type': media_type,
                'timestamp': row['timestamp'],
                'verdict': row['verdict'],
                'ai_probability': round(row['ai_probability'], 1) if row['ai_probability'] else 0.0,
                'details': details,
                'notes': row['notes'] or '',
                'full_report': full_report
            })
        
        logger.info(f"📋 Retrieved {len(results)} history records")
        return results
        
    except Exception as e:
        logger.error(f"❌ Error retrieving history: {e}", exc_info=True)
        return []


def get_stats() -> Dict[str, Any]:
    """
    Get database statistics.
    
    Returns:
        Dictionary with count statistics by media type
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Total count
        cursor.execute("SELECT COUNT(*) FROM analysis_history")
        total = cursor.fetchone()[0]
        
        # Count by type
        cursor.execute("""
            SELECT media_type, COUNT(*) 
            FROM analysis_history 
            GROUP BY media_type
        """)
        type_counts = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'total': total,
            'by_type': type_counts
        }
        
    except Exception as e:
        logger.error(f"❌ Error getting stats: {e}")
        return {'total': 0, 'by_type': {}}
