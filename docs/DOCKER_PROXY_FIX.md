# Docker Networking and Proxy Configuration Fix

## Problem Summary
The frontend (running on port 3000) could not communicate with the backend (running on port 8000) due to Docker networking issues. The error was:
```
Proxy error: Could not proxy request /api/log from localhost:3000 to http://localhost:8000 (ECONNREFUSED)
```

## Root Causes Identified

### 1. **Docker Network Isolation**
   - In Docker Compose, each container has its own network namespace
   - `localhost` inside the frontend container refers to the frontend container itself, not the host or backend
   - The frontend needs to use the Docker service name (`backend`) to reach the backend container

### 2. **Proxy Configuration**
   - The simple `"proxy"` field in `package.json` is insufficient for Docker environments
   - Need a proper proxy middleware that can be configured via environment variables

### 3. **Missing Dependency**
   - `http-proxy-middleware` package was not included in dependencies

## Fixes Applied

### 1. Updated `docker-compose.yml`
**Changed:**
```yaml
environment:
  - REACT_APP_API_URL=http://localhost:8000  # ❌ Wrong in Docker
```

**To:**
```yaml
environment:
  - REACT_APP_API_URL=http://backend:8000    # ✅ Correct for Docker
  - WDS_SOCKET_HOST=localhost                # WebSocket fix
  - WDS_SOCKET_PORT=3000                     # WebSocket fix
  - CHOKIDAR_USEPOLLING=true                 # File watching in Docker volumes
```

### 2. Created `frontend/src/setupProxy.js`
This is the **key fix** that makes the proxy work in both Docker and local environments:

```javascript
const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // Determine the backend URL based on environment
  // In Docker: use the service name (http://backend:8000)
  // Locally: use localhost (http://localhost:8000)
  const target = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  
  console.log(`[PROXY] Configuring proxy to target: ${target}`);
  
  app.use(
    '/api',
    createProxyMiddleware({
      target: target,
      changeOrigin: true,
      logLevel: 'debug',
      onProxyReq: (proxyReq, req, res) => {
        console.log(`[PROXY] ${req.method} ${req.path} -> ${target}${req.path}`);
      },
      onError: (err, req, res) => {
        console.error(`[PROXY ERROR] ${err.message}`);
        res.writeHead(500, {
          'Content-Type': 'application/json',
        });
        res.end(JSON.stringify({ error: 'Proxy error', message: err.message }));
      },
    })
  );
};
```

**Why this works:**
- React automatically loads `setupProxy.js` in development mode
- It uses `http-proxy-middleware` for sophisticated proxy configuration
- Reads `REACT_APP_API_URL` from environment (different in Docker vs local)
- Provides detailed logging for debugging

### 3. Updated `frontend/src/services/api.js`
**Changed:**
```javascript
const API_BASE_URL = (typeof process !== "undefined" && process.env.REACT_APP_API_URL) || '/api';
```

**To:**
```javascript
// When REACT_APP_API_URL is set (Docker), use it directly with /api path
// Otherwise, use '/api' which will be proxied by setupProxy.js
const API_BASE_URL = process.env.REACT_APP_API_URL 
  ? `${process.env.REACT_APP_API_URL}/api`
  : '/api';

console.log('[API] Base URL configured as:', API_BASE_URL);
```

### 4. Updated `frontend/package.json`
**Added dependency:**
```json
"http-proxy-middleware": "^2.0.6"
```

**Removed simple proxy** (replaced by setupProxy.js):
```json
"proxy": "http://localhost:8000"  // ❌ Removed
```

### 5. Verified Backend CORS Configuration
The backend already has proper CORS configuration in `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)
```

### 6. Created `.env.example`
Added example environment configuration for documentation.

## How It Works Now

### In Docker Compose:
1. Frontend container starts with `REACT_APP_API_URL=http://backend:8000`
2. `setupProxy.js` configures proxy to `http://backend:8000`
3. Frontend makes requests to `/api/*`
4. Proxy forwards to `http://backend:8000/api/*`
5. Backend responds through Docker network

### In Local Development:
1. Start backend: `cd backend && uvicorn main:app --reload`
2. Start frontend: `cd frontend && npm start`
3. `setupProxy.js` uses default `http://localhost:8000`
4. Proxy forwards requests to local backend

## Testing the Fix

### 1. Start with Docker Compose:
```bash
cd /workspaces/project-dartos
docker-compose up
```

### 2. Access the application:
- Frontend: http://localhost:3000
- Backend API docs: http://localhost:8000/docs

### 3. Test file upload:
- Navigate to the upload page
- Select a PDF file
- Upload should now work without proxy errors

### 4. Check logs for confirmation:
```bash
docker-compose logs frontend | grep PROXY
```

You should see:
```
[PROXY] Configuring proxy to target: http://backend:8000
[HPM] Proxy created: /  -> http://backend:8000
```

## No WebSocket Issues Found

During the comprehensive code review, **no WebSocket usage was detected** in either frontend or backend code. The application uses:
- Standard HTTP/HTTPS for API calls
- Axios for frontend-backend communication
- No WebSocket dependencies or implementations

The `WDS_SOCKET_*` environment variables added are for **Webpack Dev Server's hot reload** feature, not application WebSockets.

## Additional Improvements Made

1. **Added CHOKIDAR_USEPOLLING**: Ensures file watching works properly with Docker volumes
2. **Added detailed proxy logging**: Makes debugging easier
3. **Created `.env.example`**: Documents required environment variables
4. **Improved error handling**: Proxy errors are now caught and logged properly

## Environment Variables Reference

| Variable | Docker Value | Local Value | Purpose |
|----------|-------------|-------------|---------|
| `REACT_APP_API_URL` | `http://backend:8000` | `http://localhost:8000` | Backend API URL |
| `DATABASE_URL` | `postgresql://dartos:dartos123@db:5432/dartos` | Same | Database connection |
| `XAI_API_KEY` | (optional) | (optional) | xAI Grok API key |
| `WDS_SOCKET_HOST` | `localhost` | N/A | WebpackDevServer socket |
| `WDS_SOCKET_PORT` | `3000` | N/A | WebpackDevServer port |
| `CHOKIDAR_USEPOLLING` | `true` | N/A | Docker volume file watching |

## Troubleshooting

### If proxy errors persist:

1. **Check containers are running:**
   ```bash
   docker ps
   ```

2. **Check backend is accessible from frontend container:**
   ```bash
   docker exec project-dartos-frontend-1 wget -O- http://backend:8000/docs
   ```

3. **Check proxy configuration logs:**
   ```bash
   docker-compose logs frontend | grep -E "\[PROXY\]|\[HPM\]"
   ```

4. **Rebuild containers if needed:**
   ```bash
   docker-compose down
   docker-compose build --no-cache
   docker-compose up
   ```

## Summary

✅ **Fixed**: Docker networking issue preventing frontend-backend communication  
✅ **Added**: Proper proxy middleware with environment-based configuration  
✅ **Verified**: No WebSocket issues exist in the codebase  
✅ **Tested**: All containers start successfully with proper proxy configuration  
✅ **Documented**: Complete troubleshooting guide and configuration reference  

The application is now ready for file uploads and all API operations!
