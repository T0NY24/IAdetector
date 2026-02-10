# 🚀 Quick Reference: Database & Deployment

## Database Module Usage

```python
from backend import database

# Initialize (auto-called on Flask startup)
database.init_db()

# Save analysis (auto-called after each analysis)
database.insert_analysis(filename, media_type, result_dict)
# media_type: 'IMAGE', 'VIDEO', or 'AUDIO'

# Retrieve history
history = database.get_history(limit=50)

# Get stats
stats = database.get_stats()
```

## API Endpoints

### GET `/api/history`
Query params: `limit` (default: 50)

### GET `/api/history/stats`
Returns total count and breakdown by type

## Docker Commands

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Restart a service
docker-compose restart backend

# Stop all services
docker-compose down

# First-time: Pull DeepSeek model
docker exec -it uide_ollama ollama pull deepseek-r1:7b
```

## Database Location

Local: `backend/data/forensics.db`
Docker: `/app/backend/data/forensics.db` (persisted via volume)

## Field Mapping

| Type  | meta_1      | meta_2          |
|-------|-------------|-----------------|
| IMAGE | MultiLID    | UFD             |
| VIDEO | Duration(s) | Frames analyzed |
| AUDIO | Duration(s) | Confidence      |
