/**
 * Shared API client for the whole frontend.
 *
 * Production-grade features, all opt-in:
 *   • Base URL pulled from EXPO_PUBLIC_BACKEND_URL (no silent fallbacks).
 *   • 20-second request timeout so slow networks fail fast and surface UX feedback.
 *   • Auth token injector — reads the current Firebase user on every request.
 *   • 401 auto-refresh: on a single 401 response, fetches a fresh Firebase
 *     token (`getIdToken(true)`) and retries the request exactly once.
 *   • Network-level retry with exponential backoff (2 retries, 400ms → 900ms)
 *     for ECONNABORTED / ERR_NETWORK / 5xx. User-triggered mutations (POST/PUT/
 *     DELETE) are NOT retried to avoid duplicate side-effects.
 *   • Normalised error shape: `{ status, message, detail, isNetworkError }`.
 *
 * Existing code that already uses raw `axios.get(...)` keeps working — this
 * is a new, opt-in module.  New code should prefer `api.get/post/put/del`.
 */
import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios';
import { getAuth } from 'firebase/auth';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export interface ApiError {
  status: number;
  message: string;
  detail?: string;
  isNetworkError: boolean;
  original?: unknown;
}

const TIMEOUT_MS = 20000;
const MAX_RETRIES = 2;
const RETRY_BASE_MS = 400;

const client: AxiosInstance = axios.create({
  baseURL: BACKEND_URL,
  timeout: TIMEOUT_MS,
});

// ---- Inject Firebase ID token on every request ----
client.interceptors.request.use(async (config) => {
  try {
    const user = getAuth().currentUser;
    if (user) {
      const token = await user.getIdToken(/* forceRefresh */ false);
      config.headers = config.headers || {};
      if (token && !config.headers.Authorization) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
  } catch {
    /* no-op: let the call proceed unauthenticated */
  }
  return config;
});

// ---- 401 auto-refresh + normalise errors ----
client.interceptors.response.use(
  (res) => res,
  async (error: AxiosError) => {
    const cfg: any = error.config || {};
    const status = error.response?.status;

    // One-shot 401 refresh: force a new Firebase token, replay request.
    if (status === 401 && !cfg.__retriedWithFreshToken) {
      try {
        const user = getAuth().currentUser;
        if (user) {
          const fresh = await user.getIdToken(true);
          cfg.__retriedWithFreshToken = true;
          cfg.headers = { ...(cfg.headers || {}), Authorization: `Bearer ${fresh}` };
          return client.request(cfg);
        }
      } catch {
        /* fall through to normalised error */
      }
    }

    // Retry on network/5xx for idempotent verbs only.
    const method = String(cfg.method || 'get').toLowerCase();
    const isRetriable =
      ['get', 'head', 'options'].includes(method) &&
      (error.code === 'ECONNABORTED' ||
        error.code === 'ERR_NETWORK' ||
        !error.response ||
        (status !== undefined && status >= 500));

    const attempts = cfg.__attempts || 0;
    if (isRetriable && attempts < MAX_RETRIES) {
      cfg.__attempts = attempts + 1;
      const delay = RETRY_BASE_MS * Math.pow(2, attempts) + Math.random() * 150;
      await new Promise((r) => setTimeout(r, delay));
      return client.request(cfg);
    }

    const normalised: ApiError = {
      status: status ?? 0,
      message: friendlyMessage(error, status),
      detail: (error.response?.data as any)?.detail,
      isNetworkError: !error.response,
      original: error,
    };
    return Promise.reject(normalised);
  }
);

function friendlyMessage(error: AxiosError, status?: number): string {
  if (!error.response) {
    return error.code === 'ECONNABORTED'
      ? 'The request took too long. Please check your connection and try again.'
      : 'Could not reach the server. Please check your connection and try again.';
  }
  const d = (error.response.data as any) || {};
  if (d.detail) return String(d.detail);
  if (d.error) return String(d.error);
  if (status === 401) return 'Your session has expired. Please sign in again.';
  if (status === 403) return 'You do not have permission to perform this action.';
  if (status === 404) return 'The requested resource was not found.';
  if (status && status >= 500) return 'The server is having trouble. Please try again shortly.';
  return error.message || 'An unexpected error occurred.';
}

export const api = {
  get: <T = unknown>(url: string, cfg?: AxiosRequestConfig) =>
    client.get<T>(url, cfg).then((r) => r.data),
  post: <T = unknown>(url: string, body?: unknown, cfg?: AxiosRequestConfig) =>
    client.post<T>(url, body, cfg).then((r) => r.data),
  put: <T = unknown>(url: string, body?: unknown, cfg?: AxiosRequestConfig) =>
    client.put<T>(url, body, cfg).then((r) => r.data),
  del: <T = unknown>(url: string, cfg?: AxiosRequestConfig) =>
    client.delete<T>(url, cfg).then((r) => r.data),
  raw: client, // escape hatch for callers that need full control
};
