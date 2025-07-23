import { getInitData } from "../telegram/init";
import { API_URL } from "./common";

/**
 * Calls the backend to create a session cookie based on the Telegram initData.
 * This should be called once when the application loads.
 */
export async function createSession(): Promise<Response> {
  const response = await fetch(`${API_URL}/auth/session`, {
    method: 'POST',
    headers: {
      'Authorization': `tma ${getInitData()}`,
    },
  });

  if (!response.ok) {
    throw new Error('Failed to create session');
  }

  return response;
} 