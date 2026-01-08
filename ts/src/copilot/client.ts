/**
 * HTTP client with custom request interceptor.
 * 
 * Provides HTTP client that automatically adds X-Initiator header
 * based on request body content.
 */

import axios, { AxiosInstance, InternalAxiosRequestConfig } from "axios";

/**
 * Create a new HTTP client with custom interceptor.
 * 
 * The client automatically adds X-Initiator header based on request body:
 * - "agent" if assistant messages are found or isSubAgent is true
 * - "user" otherwise
 * 
 * @param isSubAgent - If true, always set X-Initiator to "agent"
 * @param debug - Enable debug logging
 * @returns Configured Axios instance
 */
export function createClient(isSubAgent: boolean = false, debug: boolean = false): AxiosInstance {
  const client = axios.create();

  // Request interceptor to add X-Initiator header
  client.interceptors.request.use((config: InternalAxiosRequestConfig) => {
    let initiator = "user";

    // Check if request has a body
    if (config.data) {
      try {
        // Convert data to string for pattern matching
        let bodyStr: string;
        if (typeof config.data === "string") {
          bodyStr = config.data;
        } else if (config.data instanceof URLSearchParams) {
          bodyStr = config.data.toString();
        } else {
          bodyStr = JSON.stringify(config.data);
        }

        // Check for assistant messages using regex
        const assistantPattern = /"role"\s*:\s*"assistant"/;
        if (assistantPattern.test(bodyStr) || isSubAgent) {
          initiator = "agent";
        }
      } catch (error) {
        // Ignore errors in pattern matching
      }
    }

    config.headers["X-Initiator"] = initiator;

    if (debug) {
      console.log(`Setting X-Initiator header to: ${initiator}`);
    }

    return config;
  });

  return client;
}
