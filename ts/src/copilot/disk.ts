/**
 * Disk cache management for GitHub Copilot tokens.
 * 
 * Reads tokens from the official GitHub Copilot client's cache.
 */

import * as fs from "fs";
import * as path from "path";
import * as os from "os";

/**
 * Read refresh token from GitHub Copilot's disk cache.
 * 
 * Reads the token from the official GitHub Copilot client's local storage.
 * This allows reusing existing authentication without re-login.
 * 
 * @returns OAuth token if found, null otherwise
 */
export function refreshTokenFromDisk(): string | null {
  const tokenPath = getTokenFilePath();

  if (!fs.existsSync(tokenPath)) {
    return null;
  }

  try {
    const content = fs.readFileSync(tokenPath, "utf-8");
    const data = JSON.parse(content);

    // Look for the specific GitHub App ID
    const appId = "github.com:Iv1.b507a08c87ecfe98";
    if (data[appId] && data[appId].oauth_token) {
      return data[appId].oauth_token;
    }

    return null;
  } catch (error) {
    return null;
  }
}

/**
 * Get the platform-specific path to the token file.
 */
function getTokenFilePath(): string {
  const platform = os.platform();

  if (platform === "win32") {
    const localAppData = process.env.LOCALAPPDATA || path.join(os.homedir(), "AppData", "Local");
    return path.join(localAppData, "github-copilot", "apps.json");
  } else {
    // Unix-like systems (Linux, macOS)
    return path.join(os.homedir(), ".config", "github-copilot", "apps.json");
  }
}
