const { createProxyMiddleware } = require('http-proxy-middleware');

module.exports = function(app) {
  // In Docker, proxy /api/* requests to the backend container
  // Use the backend container's IP address directly
  const target = 'http://172.18.0.3:8000';
  
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
