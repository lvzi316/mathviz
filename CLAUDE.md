# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**MathViz** is a web application that converts Chinese math word problems (particularly travel/kinematics problems) into visualization charts. Users input text descriptions of math problems, and the system automatically parses and generates clear visual diagrams.

## Architecture

### Core Components
- **Backend**: FastAPI Python server (`api_server.py`) with async task processing
- **Visualization Engine**: `text_to_visual.py` - parses problems and generates matplotlib charts
- **Frontend**: Single HTML file (`frontend/index.html`) with vanilla JavaScript
- **Deployment**: Docker + Docker Compose with nginx reverse proxy

### Key Technologies
- **Backend**: FastAPI, Python 3.11, matplotlib, numpy, PIL
- **Frontend**: HTML5, CSS3, vanilla JavaScript (no frameworks)
- **Deployment**: Docker, nginx, Redis (for future queue system)

## Development Commands

### Local Development
```bash
# Start the application
./start.sh

# Or manually
source visual_env/bin/activate
pip install -r requirements.txt
python api_server.py
```

### Docker Development
```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### API Testing
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Submit problem
curl -X POST http://localhost:8000/api/v1/problems/generate \
  -H "Content-Type: application/json" \
  -d '{"text": "甲、乙两地相距480公里，小张开车从甲地出发前往乙地，速度为60公里/小时；同时小李开车从乙地出发前往甲地，速度为80公里/小时。问他们出发后多长时间相遇？"}'
```

## File Structure

```
mathapp/
├── api_server.py           # FastAPI backend with async processing
├── text_to_visual.py       # Core visualization engine
├── frontend/index.html     # Single-page frontend
├── output/                 # Generated images storage
├── docker-compose.yml      # Docker orchestration
├── Dockerfile             # Backend container
├── nginx.conf             # Frontend nginx config
└── requirements.txt       # Python dependencies
```

## Key Classes & Methods

### MathProblemVisualizer (text_to_visual.py)
- `create_meeting_visualization(text, output_path)` - Generates meeting problem charts
- `create_chase_visualization(text, output_path)` - Generates chase problem charts
- `parse_meeting_problem(text)` - Extracts parameters from Chinese text

### API Endpoints (api_server.py)
- `POST /api/v1/problems/generate` - Submit problem for visualization
- `GET /api/v1/problems/status/{task_id}` - Check async task status
- `GET /api/v1/images/{image_id}` - Retrieve generated image
- `GET /api/v1/health` - Health check endpoint

## Problem Types Supported

1. **Meeting Problems** (相遇问题) - Two objects moving toward each other
2. **Chase Problems** (追及问题) - One object chasing another
3. **Auto-detection** from Chinese text keywords

## Development Tips

### Adding New Problem Types
1. Add parsing method in `text_to_visual.py`
2. Add visualization method in `text_to_visual.py`
3. Update `detect_problem_type()` in `api_server.py`
4. Add new endpoint handler in `api_server.py`

### Frontend Development
- Edit `frontend/index.html` directly
- Open file in browser for immediate preview
- No build process required

### Testing
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests (if test directory exists)
pytest tests/
```

### Environment Setup
- Python 3.11+ with virtual environment
- Install dependencies: `pip install -r requirements.txt`
- Ensure `output/` directory exists for image storage

## Deployment

### Local
- Backend: `python api_server.py` (port 8000)
- Frontend: Open `frontend/index.html` directly
- API docs: http://localhost:8000/docs

### Production
- Use Docker Compose for full stack
- Frontend served on port 3000 via nginx
- Backend served on port 8000
- Redis included for future queue system