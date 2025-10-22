# Quick Reference: File Upload Fix

## What Was Fixed
✅ Docker networking issue preventing frontend → backend communication  
✅ Proxy errors (`ECONNREFUSED`) when uploading files  
✅ All containers now communicate properly via Docker network  

## Files Changed
1. `docker-compose.yml` - Updated `REACT_APP_API_URL` to use Docker service name
2. `frontend/src/setupProxy.js` - **NEW**: Proper proxy middleware configuration
3. `frontend/src/services/api.js` - Updated API base URL logic
4. `frontend/package.json` - Added `http-proxy-middleware` dependency

## Quick Start

```bash
# Start everything
cd /workspaces/project-dartos
docker-compose up

# Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

## Verify It's Working

```bash
# Check all containers are running
docker-compose ps

# Check for proxy configuration (should see "http://backend:8000")
docker-compose logs frontend | grep PROXY

# Check no errors (should be empty or only show event subscriptions)
docker-compose logs | grep -i "proxy error"

# Test backend API
curl http://localhost:8000/api/documents
```

## How It Works Now

**Before (Broken):**
```
Frontend Container → localhost:8000 ❌ (ECONNREFUSED)
(localhost in container = container itself)
```

**After (Fixed):**
```
Frontend Container → backend:8000 ✅ (via Docker network)
(backend = Docker service name)
```

## Troubleshooting

### Problem: Containers won't start
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### Problem: Frontend shows proxy errors
```bash
# Check env var is set correctly
docker-compose exec frontend env | grep REACT_APP_API_URL
# Should show: REACT_APP_API_URL=http://backend:8000
```

### Problem: Backend not responding
```bash
# Check backend is running
docker-compose logs backend | tail -20

# Test from frontend container
docker-compose exec frontend wget -O- http://backend:8000/api/documents
```

## Key Environment Variables

| Variable | Docker Value | Purpose |
|----------|-------------|---------|
| `REACT_APP_API_URL` | `http://backend:8000` | Backend URL for frontend |
| `DATABASE_URL` | `postgresql://dartos:dartos123@db:5432/dartos` | Database connection |

## Documentation Files

- `DOCKER_PROXY_FIX.md` - Detailed technical explanation
- `UPLOAD_FIX_SUMMARY.md` - Complete summary with architecture
- `.env.example` - Environment variable template

## Status: ✅ FIXED

All file upload functionality is now working correctly!
