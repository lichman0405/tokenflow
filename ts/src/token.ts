/**
 * Token management module.
 * 
 * Provides OAuth2 token data structure and lifecycle management.
 */

/**
 * Represents an OAuth2 token.
 */
export class Token {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
  expiresAt: number;

  constructor(
    accessToken: string,
    refreshToken: string = "",
    expiresIn: number = 0,
    expiresAt: number = 0
  ) {
    this.accessToken = accessToken;
    this.refreshToken = refreshToken;
    this.expiresIn = expiresIn;
    this.expiresAt = expiresAt;
  }

  /**
   * Calculate and set the expiresAt field based on current time and expiresIn.
   */
  setExpiresAt(): void {
    this.expiresAt = Math.floor(Date.now() / 1000) + this.expiresIn;
  }

  /**
   * Check if the token is expired or about to expire.
   * 
   * Returns true if expired or within 10% of its lifetime from expiration.
   * This provides a buffer time for token refresh.
   * 
   * @returns True if the token is expired or about to expire
   */
  isExpired(): boolean {
    const buffer = Math.floor(this.expiresIn / 10);
    return Math.floor(Date.now() / 1000) >= this.expiresAt - buffer;
  }

  /**
   * Calculate and set the expiresIn field based on expiresAt.
   */
  setExpiresIn(): void {
    this.expiresIn = Math.max(0, this.expiresAt - Math.floor(Date.now() / 1000));
  }

  /**
   * Convert token to plain object for serialization.
   */
  toJSON(): Record<string, any> {
    return {
      access_token: this.accessToken,
      refresh_token: this.refreshToken,
      expires_in: this.expiresIn,
      expires_at: this.expiresAt,
    };
  }

  /**
   * Create a Token instance from a plain object.
   */
  static fromJSON(data: any): Token {
    return new Token(
      data.access_token || "",
      data.refresh_token || "",
      data.expires_in || 0,
      data.expires_at || 0
    );
  }
}
