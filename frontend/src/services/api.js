/**
 * API Client for Vector Backend
 * Handles all communication with the LangGraph pipeline
 */

const API_BASE_URL = 'http://localhost:8000';

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
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error triggering test run:', error);
    throw error;
  }
}

/**
 * Get all executions
 */
export async function getExecutions() {
  try {
    const response = await fetch(`${API_BASE_URL}/pipeline/executions`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching executions:', error);
    throw error;
  }
}

/**
 * Get execution details by webhook ID
 */
export async function getExecution(webhookId) {
  try {
    const response = await fetch(`${API_BASE_URL}/pipeline/executions/${webhookId}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching execution:', error);
    throw error;
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
