/**
 * HTTP headers for GitHub Copilot API requests.
 * 
 * Provides standard headers that mimic the official client.
 */

// Constants matching official client
const USER_AGENT = "GitHubCopilotChat/0.32.4";
const EDITOR_VERSION = "vscode/1.105.1";
const EDITOR_PLUGIN_VERSION = "copilot-chat/0.32.4";
const INTEGRATION_ID = "vscode-chat";

/**
 * Get standard headers for Copilot API requests.
 * 
 * Returns headers that identify the client as VS Code with Copilot Chat.
 * 
 * @returns Dictionary of HTTP headers
 */
export function getHeaders(): Record<string, string> {
  return {
    "User-Agent": USER_AGENT,
    "Editor-Version": EDITOR_VERSION,
    "Editor-Plugin-Version": EDITOR_PLUGIN_VERSION,
    "Copilot-Integration-Id": INTEGRATION_ID,
  };
}
