/**
 * User-friendly error handler for API responses
 * Maps backend error codes to user-friendly messages
 */

// Common error messages matching backend
export const ERROR_MESSAGES: Record<string, string> = {
  // Network/Connection errors
  NETWORK_ERROR: "Connection issue. Please check your internet and try again.",
  TIMEOUT_ERROR: "The request took too long. Please try again.",
  
  // Auth errors
  AUTH_REQUIRED: "Please log in to continue.",
  AUTH_EXPIRED: "Your session has expired. Please log in again.",
  AUTH_INVALID: "Invalid credentials. Please check your email and password.",
  AUTH_FORBIDDEN: "You don't have permission to access this resource.",
  
  // Payment errors
  PAYMENT_FAILED: "Payment could not be processed. Please try again.",
  PAYMENT_PENDING: "Your payment is still being processed. Please wait.",
  INSUFFICIENT_BALANCE: "Insufficient wallet balance. Please top up.",
  
  // Rate limiting
  RATE_LIMITED: "Too many requests. Please wait a moment and try again.",
  DUPLICATE_ACTION: "This action has already been performed.",
  
  // General errors
  SERVER_ERROR: "Something went wrong. Please try again later.",
  NOT_FOUND: "The requested resource was not found.",
};

/**
 * Get a user-friendly error message from an axios error
 */
export function getErrorMessage(error: any): string {
  // Network error (no response from server)
  if (!error.response) {
    if (error.code === "ECONNABORTED") {
      return ERROR_MESSAGES.TIMEOUT_ERROR;
    }
    return ERROR_MESSAGES.NETWORK_ERROR;
  }
  
  const status = error.response.status;
  const detail = error.response.data?.detail;
  const errorKey = error.response.data?.error;
  
  // If backend sends a specific error message, use it
  if (errorKey && ERROR_MESSAGES[errorKey]) {
    return ERROR_MESSAGES[errorKey];
  }
  
  // If backend sends a detail message, use it
  if (typeof detail === "string" && detail.length < 100) {
    return detail;
  }
  
  // Map HTTP status codes to messages
  switch (status) {
    case 401:
      return ERROR_MESSAGES.AUTH_REQUIRED;
    case 402:
      return ERROR_MESSAGES.INSUFFICIENT_BALANCE;
    case 403:
      return ERROR_MESSAGES.AUTH_FORBIDDEN;
    case 404:
      return ERROR_MESSAGES.NOT_FOUND;
    case 409:
      return ERROR_MESSAGES.DUPLICATE_ACTION;
    case 429:
      return ERROR_MESSAGES.RATE_LIMITED;
    case 500:
    case 502:
    case 503:
      return ERROR_MESSAGES.SERVER_ERROR;
    default:
      return ERROR_MESSAGES.SERVER_ERROR;
  }
}

/**
 * Check if an error is a payment-related error (402)
 */
export function isPaymentError(error: any): boolean {
  return error.response?.status === 402;
}

/**
 * Check if an error is an authentication error (401 or 403)
 */
export function isAuthError(error: any): boolean {
  const status = error.response?.status;
  return status === 401 || status === 403;
}

/**
 * Check if an error is a rate limit error (429)
 */
export function isRateLimitError(error: any): boolean {
  return error.response?.status === 429;
}
