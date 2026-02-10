"""
Quick test script for database functionality.
Tests insertion for all 3 media types (IMAGE, VIDEO, AUDIO).
"""
import sys
sys.path.insert(0, 'c:/Users/anper/Downloads/ProyectoForenseUIDE')

from backend import database

# Test IMAGE insertion
print("🧪 Testing IMAGE insertion...")
image_result = {
    'verdict': 'GENERADA POR IA',
    'confidence': 'ALTA',
    'scores': {
        'unified': 0.85,
        'ai_probability': 0.85,
        'MultiLID': 0.23,
        'UFD': 0.87,
        'Semantic': 0.92
    },
    'evidence': ['MultiLID anomaly detected', 'UFD score high'],
    'notes': 'Strong AI signatures detected in geometry and noise patterns'
}
img_id = database.insert_analysis('test_image.jpg', 'IMAGE', image_result)
print(f"✅ IMAGE inserted with ID: {img_id}")

# Test VIDEO insertion
print("\n🧪 Testing VIDEO insertion...")
video_result = {
    'verdict': 'DEEPFAKE',
    'is_deepfake': True,
    'probability': 78.5,
    'duration': 63.2,
    'frames_total': 1896,
    'frames_analyzed': 45,
    'max_probability': 92.3
}
vid_id = database.insert_analysis('test_video.mp4', 'VIDEO', video_result)
print(f"✅ VIDEO inserted with ID: {vid_id}")

# Test AUDIO insertion
print("\n🧪 Testing AUDIO insertion...")
audio_result = {
    'verdict': 'AUDIO SINTÉTICO',
    'score': 72.1,
    'confidence': 80.0,
    'duration_analyzed': 12.5,
    'sample_rate': 16000,
    'detection_reasons': ['MFCCs muy uniformes', 'ZCR muy regular']
}
aud_id = database.insert_analysis('test_audio.wav', 'AUDIO', audio_result)
print(f"✅ AUDIO inserted with ID: {aud_id}")

# Test retrieval
print("\n📋 Testing get_history()...")
history = database.get_history(limit=10)
print(f"✅ Retrieved {len(history)} records")

# Display results
for record in history:
    print(f"\n  ID: {record['id']}")
    print(f"  File: {record['filename']}")
    print(f"  Type: {record['type']}")
    print(f"  Verdict: {record['verdict']}")
    print(f"  AI Probability: {record['ai_probability']}%")
    print(f"  Details: {record['details']}")

# Test stats
print("\n📊 Testing get_stats()...")
stats = database.get_stats()
print(f"✅ Total records: {stats['total']}")
print(f"  By type: {stats['by_type']}")

print("\n✅ All tests passed successfully!")
