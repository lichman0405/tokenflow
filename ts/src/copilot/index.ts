/**
 * GitHub Copilot integration module.
 * 
 * Provides device flow authentication for GitHub Copilot.
 */

export {
  DeviceCode,
  requestDeviceCode,
  pollForToken,
  refreshToken,
  NotAvailableError,
} from "./oauth";
export { refreshTokenFromDisk } from "./disk";
export { createClient } from "./client";
export { SIGNUP_URL, FREE_URL } from "./urls";
