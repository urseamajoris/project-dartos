const VERBOSE =
  (typeof process !== "undefined" && process.env && process.env.REACT_APP_VERBOSE_LOGS === "true") ||
  (typeof window !== "undefined" && window.DARTOS_VERBOSE === true);

function safeSerialize(v) {
  try {
    return JSON.parse(JSON.stringify(v));
  } catch {
    try {
      return String(v);
    } catch {
      return "<unserializable>";
    }
  }
}

async function sendLog(level, message, data) {
  try {
    await fetch('/api/log', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        level,
        message,
        data: safeSerialize(data),
        timestamp: new Date().toISOString(),
      }),
    });
  } catch (err) {
    // Fallback to console if sending fails
    console.error('[DARTOS] Failed to send log to backend:', err);
  }
}

export function debug(...args) {
  if (!VERBOSE) return;
  const message = args.join(' ');
  console.debug("[DARTOS][DEBUG]", ...args);
  sendLog('debug', message, args);
}

export function info(...args) {
  const message = args.join(' ');
  console.info("[DARTOS][INFO]", ...args);
  sendLog('info', message, args);
}

export function warn(...args) {
  const message = args.join(' ');
  console.warn("[DARTOS][WARN]", ...args);
  sendLog('warn', message, args);
}

export function error(...args) {
  const message = args.join(' ');
  console.error("[DARTOS][ERROR]", ...args);
  sendLog('error', message, args);
}

export function initGlobalLogging({ verbose = false } = {}) {
  if (typeof window !== "undefined") {
    if (verbose) window.DARTOS_VERBOSE = true;
    window.addEventListener("error", (ev) => {
      error("Uncaught error", {
        message: ev.message,
        filename: ev.filename,
        lineno: ev.lineno,
        colno: ev.colno,
        error: ev.error,
      });
    });
    window.addEventListener("unhandledrejection", (ev) => {
      error("Unhandled promise rejection", { reason: ev.reason });
    });

    // Prefix native console methods for easier filtering
    ["log", "debug", "info", "warn", "error"].forEach((m) => {
      const orig = console[m].bind(console);
      console[m] = (...args) => {
        orig(`[DARTOS][${m.toUpperCase()}]`, ...args);
        // Also send to backend
        sendLog(m, args.join(' '), args);
      };
    });
  }
}