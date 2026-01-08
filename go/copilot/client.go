// Package copilot provides GitHub Copilot integration.
package copilot

import (
	"bytes"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"regexp"
)

// NewClient creates a new HTTP client with a custom transport that adds the
// X-Initiator header based on message history in the request body.
func NewClient(isSubAgent bool) *http.Client {
	return &http.Client{
		Transport: &initiatorTransport{isSubAgent: isSubAgent},
	}
}

type initiatorTransport struct {
	isSubAgent bool
}

func (t *initiatorTransport) RoundTrip(req *http.Request) (*http.Response, error) {
	const (
		xInitiatorHeader = "X-Initiator"
		userInitiator    = "user"
		agentInitiator   = "agent"
	)

	if req == nil {
		return nil, fmt.Errorf("HTTP request is nil")
	}
	if req.Body == http.NoBody {
		// No body to inspect; default to user.
		req.Header.Set(xInitiatorHeader, userInitiator)
		slog.Debug("Setting X-Initiator header to user (no request body)")
		return http.DefaultTransport.RoundTrip(req)
	}

	// Clone request to avoid modifying the original.
	req = req.Clone(req.Context())

	// Read the original body into bytes so we can examine it.
	bodyBytes, err := io.ReadAll(req.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read request body: %w", err)
	}
	defer req.Body.Close()

	// Restore the original body using the preserved bytes.
	req.Body = io.NopCloser(bytes.NewReader(bodyBytes))

	// Check for assistant messages using regex to handle whitespace
	// variations in the JSON while avoiding full unmarshalling overhead.
	initiator := userInitiator
	assistantRolePattern := regexp.MustCompile(`"role"\s*:\s*"assistant"`)
	if assistantRolePattern.Match(bodyBytes) || t.isSubAgent {
		slog.Debug("Setting X-Initiator header to agent (found assistant messages in history)")
		initiator = agentInitiator
	} else {
		slog.Debug("Setting X-Initiator header to user (no assistant messages)")
	}
	req.Header.Set(xInitiatorHeader, initiator)

	return http.DefaultTransport.RoundTrip(req)
}
