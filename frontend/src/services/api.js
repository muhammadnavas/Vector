/**
 * API Client for Vector Backend
 * Handles all communication with the LangGraph pipeline
 */

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/$/, '');

async function parseError(response) {
  const body = await response.json().catch(() => ({}));
  return body.detail || body.message || `HTTP error! status: ${response.status}`;
}

function normalizeNetworkError(error) {
  if (error instanceof TypeError && String(error.message || '').includes('Failed to fetch')) {
    const offlineError = new Error(
      `Backend API is not reachable at ${API_BASE_URL}. ` +
      'Start backend with: python Agents/main.py or set VITE_API_BASE_URL in frontend/.env'
    );
    offlineError.status = 0;
    return offlineError;
  }
  return error;
}

/**
 * Trigger a new test run
 */
export async function triggerTestRun(payload) {
  try {
    const response = await fetch(`${API_BASE_URL}/pipeline/test-run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const error = new Error(await parseError(response));
      error.status = response.status;
      throw error;
    }

    return await response.json();
  } catch (error) {
    const normalizedError = normalizeNetworkError(error);
    console.error('Error triggering test run:', normalizedError);
    throw normalizedError;
  }
}

/**
 * Trigger endpoint discovery for a GitHub repository
 */
export async function discoverEndpoints(payload) {
  try {
    const response = await fetch(`${API_BASE_URL}/pipeline/discover-endpoints`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      const error = new Error(await parseError(response));
      error.status = response.status;
      throw error;
    }

    return await response.json();
  } catch (error) {
    const normalizedError = normalizeNetworkError(error);
    console.error('Error triggering endpoint discovery:', normalizedError);
    throw normalizedError;
  }
}

/**
 * Get all executions
 */
export async function getExecutions() {
  try {
    const response = await fetch(`${API_BASE_URL}/pipeline/executions`);

    if (!response.ok) {
      throw new Error(await parseError(response));
    }

    return await response.json();
  } catch (error) {
    const normalizedError = normalizeNetworkError(error);
    console.error('Error fetching executions:', normalizedError);
    throw normalizedError;
  }
}

/**
 * Get execution details by webhook ID
 */
export async function getExecution(webhookId) {
  try {
    const response = await fetch(`${API_BASE_URL}/pipeline/executions/${webhookId}`);

    if (!response.ok) {
      const error = new Error(await parseError(response));
      error.status = response.status;
      throw error;
    }

    return await response.json();
  } catch (error) {
    const normalizedError = normalizeNetworkError(error);
    console.error('Error fetching execution:', normalizedError);
    throw normalizedError;
  }
}

/**
 * Health check
 */
export async function healthCheck() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}
