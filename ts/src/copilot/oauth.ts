/**
 * GitHub Copilot OAuth device flow implementation.
 * 
 * Implements the OAuth2 device authorization flow for GitHub Copilot.
 */

import axios, { AxiosError } from "axios";
import { Token } from "../token";
import { getHeaders } from "./http";

// GitHub OAuth endpoints
const CLIENT_ID = "Iv1.b507a08c87ecfe98";
const DEVICE_CODE_URL = "https://github.com/login/device/code";
const ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token";
const COPILOT_TOKEN_URL = "https://api.github.com/copilot_internal/v2/token";

// Maximum response size (1MB) to prevent memory exhaustion
const MAX_RESPONSE_SIZE = 1024 * 1024;

/**
 * Custom error thrown when GitHub Copilot is not available.
 */
export class NotAvailableError extends Error {
  constructor(message: string = "GitHub Copilot is not available") {
    super(message);
    this.name = "NotAvailableError";
  }
}

/**
 * Device code response from GitHub.
 */
export interface DeviceCode {
  deviceCode: string;
  userCode: string;
  verificationUri: string;
  expiresIn: number;
  interval: number;
}

/**
 * Initiate the device code flow with GitHub.
 * 
 * @param timeout - Request timeout in milliseconds
 * @returns Device code information
 */
export async function requestDeviceCode(timeout: number = 30000): Promise<DeviceCode> {
  const params = new URLSearchParams({
    client_id: CLIENT_ID,
    scope: "read:user",
  });

  const headers = {
    Accept: "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": getHeaders()["User-Agent"],
  };

  const response = await axios.post(DEVICE_CODE_URL, params.toString(), {
    headers,
    timeout,
  });

  return {
    deviceCode: response.data.device_code,
    userCode: response.data.user_code,
    verificationUri: response.data.verification_uri,
    expiresIn: response.data.expires_in,
    interval: response.data.interval || 5,
  };
}

/**
 * Poll GitHub for the access token after user authorization.
 * 
 * @param deviceCode - Device code from requestDeviceCode()
 * @param timeout - Maximum time to poll in milliseconds (defaults to deviceCode.expiresIn)
 * @returns Copilot token
 */
export async function pollForToken(
  deviceCode: DeviceCode,
  timeout?: number
): Promise<Token> {
  // Use let to allow interval accumulation on slow_down
  let currentInterval = Math.max(deviceCode.interval, 5) * 1000;
  const deadline = Date.now() + (timeout || deviceCode.expiresIn * 1000);

  while (Date.now() < deadline) {
    try {
      const token = await tryGetToken(deviceCode.deviceCode);
      if (token) {
        return token;
      }
    } catch (error) {
      if (error instanceof PendingError) {
        await sleep(currentInterval);
        continue;
      } else if (error instanceof SlowDownError) {
        // Accumulate interval on slow_down (matches Go behavior)
        currentInterval += 5000;
        await sleep(currentInterval);
        continue;
      }
      throw error;
    }
  }

  throw new Error("Authorization timed out");
}

/**
 * Pending authorization error.
 */
class PendingError extends Error {
  constructor() {
    super("Authorization pending");
    this.name = "PendingError";
  }
}

/**
 * Slow down polling error.
 */
class SlowDownError extends Error {
  constructor() {
    super("Slow down");
    this.name = "SlowDownError";
  }
}

/**
 * Try to get the access token from GitHub.
 */
async function tryGetToken(deviceCode: string): Promise<Token | null> {
  const params = new URLSearchParams({
    client_id: CLIENT_ID,
    device_code: deviceCode,
    grant_type: "urn:ietf:params:oauth:grant-type:device_code",
  });

  const headers = {
    Accept: "application/json",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": getHeaders()["User-Agent"],
  };

  const response = await axios.post(ACCESS_TOKEN_URL, params.toString(), {
    headers,
    timeout: 30000,
  });

  const result = response.data;
  const error = result.error || "";

  if (error === "authorization_pending") {
    throw new PendingError();
  } else if (error === "slow_down") {
    throw new SlowDownError();
  } else if (error) {
    throw new Error(`Authorization failed: ${error}`);
  }

  const accessToken = result.access_token || "";
  if (!accessToken) {
    throw new PendingError();
  }

  return getCopilotToken(accessToken);
}

/**
 * Exchange GitHub token for Copilot token.
 */
async function getCopilotToken(githubToken: string): Promise<Token> {
  const headers = {
    Accept: "application/json",
    Authorization: `Bearer ${githubToken}`,
    ...getHeaders(),
  };

  try {
    const response = await axios.get(COPILOT_TOKEN_URL, {
      headers,
      timeout: 30000,
      maxContentLength: MAX_RESPONSE_SIZE,
      maxBodyLength: MAX_RESPONSE_SIZE,
    });

    const token = new Token(
      response.data.token,
      githubToken,
      0,
      response.data.expires_at
    );
    token.setExpiresIn();

    return token;
  } catch (err) {
    const axiosErr = err as AxiosError;
    if (axiosErr.isAxiosError && axiosErr.response?.status === 403) {
      throw new NotAvailableError("GitHub Copilot is not available for this account");
    }
    throw err;
  }
}

/**
 * Refresh the Copilot token using the GitHub token.
 * 
 * @param githubToken - GitHub OAuth token (stored as refresh_token)
 * @returns New Copilot token
 */
export async function refreshToken(githubToken: string): Promise<Token> {
  return getCopilotToken(githubToken);
}

/**
 * Sleep for specified milliseconds.
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
