/**
 * Hyper device flow authentication implementation.
 * 
 * Implements OAuth2 device flow for Hyper service including
 * device authorization, token exchange, and token introspection.
 */

import axios, { AxiosError } from "axios";
import * as os from "os";
import { Token } from "../token";

// Maximum response size (1MB) to prevent memory exhaustion
const MAX_RESPONSE_SIZE = 1024 * 1024;

/**
 * Get the base URL for Hyper API.
 * 
 * In production, this should come from configuration.
 */
function getBaseUrl(): string {
  // This should be configured via environment variable or config file
  return process.env.HYPER_BASE_URL || "https://api.hyper.example.com";
}

/**
 * Device authorization response.
 */
export interface DeviceAuthResponse {
  deviceCode: string;
  userCode: string;
  verificationUrl: string;
  expiresIn: number;
}

/**
 * Token polling response.
 */
export interface TokenResponse {
  refreshToken?: string;
  userId?: string;
  organizationId?: string;
  organizationName?: string;
  error?: string;
  errorDescription?: string;
}

/**
 * Token introspection response (RFC 7662).
 */
export interface IntrospectTokenResponse {
  active: boolean;
  sub?: string;
  org_id?: string;
  exp?: number;
  iat?: number;
  iss?: string;
  jti?: string;
}

/**
 * Get a descriptive device name.
 */
function getDeviceName(): string {
  try {
    const hostname = os.hostname();
    if (hostname) {
      return `Crush (${hostname})`;
    }
  } catch (error) {
    // Ignore error
  }
  return "Crush";
}

/**
 * Initiate the device authorization flow.
 * 
 * @param timeout - Request timeout in milliseconds
 * @returns Device authorization response
 */
export async function initiateDeviceAuth(
  timeout: number = 30000
): Promise<DeviceAuthResponse> {
  const url = `${getBaseUrl()}/device/auth`;

  const payload = {
    device_name: getDeviceName(),
  };

  const headers = {
    "Content-Type": "application/json",
    "User-Agent": "crush",
  };

  const response = await axios.post(url, payload, {
    headers,
    timeout,
  });

  return {
    deviceCode: response.data.device_code,
    userCode: response.data.user_code,
    verificationUrl: response.data.verification_url,
    expiresIn: response.data.expires_in,
  };
}

/**
 * Poll for authorization completion and get refresh token.
 * 
 * @param deviceCode - Device code from initiateDeviceAuth()
 * @param expiresIn - Time in seconds until device code expires
 * @param onSuccess - Optional callback with user_id when authorization succeeds.
 *                    This matches Go's event.Alias() behavior for user tracking.
 * @returns Refresh token
 */
export async function pollForToken(
  deviceCode: string,
  expiresIn: number,
  onSuccess?: (userId: string) => void
): Promise<string> {
  const deadline = Date.now() + expiresIn * 1000;
  const interval = 5000; // Poll every 5 seconds

  while (Date.now() < deadline) {
    const response = await pollOnce(deviceCode);

    if (response.refreshToken) {
      // Call onSuccess callback if provided (matches Go's event.Alias)
      if (onSuccess && response.userId) {
        onSuccess(response.userId);
      }
      return response.refreshToken;
    }

    if (response.error === "authorization_pending") {
      await sleep(interval);
      continue;
    }

    if (response.error) {
      throw new Error(response.errorDescription || response.error);
    }
  }

  throw new Error("Authorization timed out");
}

/**
 * Perform a single polling request.
 */
async function pollOnce(deviceCode: string): Promise<TokenResponse> {
  const url = `${getBaseUrl()}/device/auth/${deviceCode}`;

  const headers = {
    "Content-Type": "application/json",
    "User-Agent": "crush",
  };

  try {
    const response = await axios.get(url, {
      headers,
      timeout: 30000,
      maxContentLength: MAX_RESPONSE_SIZE,
      maxBodyLength: MAX_RESPONSE_SIZE,
    });

    return {
      refreshToken: response.data.refresh_token,
      userId: response.data.user_id,
      organizationId: response.data.organization_id,
      organizationName: response.data.organization_name,
      error: response.data.error,
      errorDescription: response.data.error_description,
    };
  } catch (err) {
    const axiosErr = err as AxiosError;
    if (axiosErr.isAxiosError && axiosErr.response) {
      const data = axiosErr.response.data as Record<string, unknown>;
      return {
        error: data.error as string | undefined,
        errorDescription: data.error_description as string | undefined,
      };
    }
    throw err;
  }
}

/**
 * Exchange refresh token for access token.
 * 
 * @param refreshToken - Refresh token from pollForToken()
 * @param timeout - Request timeout in milliseconds
 * @returns Access token
 */
export async function exchangeToken(
  refreshToken: string,
  timeout: number = 30000
): Promise<Token> {
  const url = `${getBaseUrl()}/token/exchange`;

  const payload = {
    refresh_token: refreshToken,
  };

  const headers = {
    "Content-Type": "application/json",
    "User-Agent": "crush",
  };

  const response = await axios.post(url, payload, {
    headers,
    timeout,
    maxContentLength: MAX_RESPONSE_SIZE,
    maxBodyLength: MAX_RESPONSE_SIZE,
  });

  const token = Token.fromJSON(response.data);
  token.setExpiresAt();

  return token;
}

/**
 * Validate and get information about an access token.
 * 
 * Implements OAuth2 Token Introspection (RFC 7662).
 * 
 * @param accessToken - Access token to introspect
 * @param timeout - Request timeout in milliseconds
 * @returns Token introspection response
 */
export async function introspectToken(
  accessToken: string,
  timeout: number = 30000
): Promise<IntrospectTokenResponse> {
  const url = `${getBaseUrl()}/token/introspect`;

  const payload = {
    token: accessToken,
  };

  const headers = {
    "Content-Type": "application/json",
    "User-Agent": "crush",
  };

  const response = await axios.post(url, payload, {
    headers,
    timeout,
    maxContentLength: MAX_RESPONSE_SIZE,
    maxBodyLength: MAX_RESPONSE_SIZE,
  });

  return response.data;
}

/**
 * Sleep for specified milliseconds.
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
