# MCP Protocol Analysis
Date: 2025-06-23
Agent: Agent 3 - MCP Protocol Analyzer

## Executive Summary

The Model Context Protocol (MCP) is an open standard developed by Anthropic that enables secure, two-way connections between AI systems and external data sources/tools. It provides a standardized way to connect LLMs with the context they need, replacing fragmented integrations with a single protocol.

## Key Findings

### 1. MCP Protocol Basics

#### Foundation
- Built on JSON-RPC 2.0 specification for message exchange
- Adapted from Language Server Protocol (LSP) proven foundations
- Open source and actively maintained on GitHub

#### Core Components
1. **Tools (Model-controlled)**: Actions the AI decides to take
2. **Resources (Application-controlled)**: Context provided to the AI
3. **Prompts (User-controlled)**: Specific user-invoked interactions

#### Transport Mechanisms
1. **stdio**: Communication through standard input/output streams
2. **WebSocket**: Community implementations for real-time bidirectional communication
3. **HTTP/SSE**: HTTP POST with Server-Sent Events for responses
4. **UNIX sockets**: For local inter-process communication

### 2. How MCP Servers and Clients Communicate

#### Message Types (JSON-RPC 2.0)
1. **Requests**: Messages sent to initiate an operation (must include ID)
2. **Responses**: Reply to requests containing result or error
3. **Notifications**: One-way messages with no response expected

#### Communication Flow
1. Client launches MCP server as subprocess (stdio) or connects to remote server
2. Messages exchanged in JSON-RPC format
3. Server processes requests and sends responses
4. Notifications can be sent in either direction

### 3. MCP Configuration in Claude Ecosystem

#### Claude Desktop Configuration
Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

Example structure:
```json
{
  "mcpServers": {
    "server-name": {
      "command": "npx",
      "args": ["@package/mcp-server"],
      "env": {
        "API_KEY": "value"
      }
    }
  }
}
```

#### Claude Code Configuration
Locations:
- `~/.config/claude-code/mcp.json`
- `~/.claude-code/mcp.json`

### 4. MCP Tool Naming Conventions

#### Standard MCP Servers
MCP servers are configured with descriptive names in the configuration:
- `server-filesystem`
- `brave-search`
- `puppeteer`
- `memory`
- `browsermcp`

#### The mcp__ Prefix Pattern
Based on the WebFetch tool description in the environment:
> "IMPORTANT: If an MCP-provided web fetch tool is available, prefer using that tool instead of this one, as it may have fewer restrictions. All MCP-provided tools start with 'mcp__'."

This indicates:
1. **MCP-provided tools use the `mcp__` prefix** when exposed to the AI
2. This prefix distinguishes MCP tools from built-in tools
3. MCP tools may have fewer restrictions than built-in equivalents

### 5. Differences Between Claude Desktop and Claude Code

#### Claude Desktop
- Desktop application with GUI
- Configuration in `~/Library/Application Support/Claude/`
- Supports local MCP servers via subprocess
- Native OAuth support for authentication

#### Claude Code
- Terminal-based CLI tool
- Configuration in `~/.config/claude-code/` or `~/.claude-code/`
- Supports both local and remote MCP servers
- Remote MCP support with OAuth authentication
- Zero marginal cost for agent actions with Claude Pro subscription

### 6. How to Properly Invoke MCP Tools

#### Direct Tool Invocation
When an MCP server exposes tools, they appear with the `mcp__` prefix:
- Example: `mcp__brave_search` instead of built-in `WebSearch`
- Example: `mcp__filesystem_read` instead of built-in `Read`

#### Tool Selection Priority
1. Check if MCP-provided tool exists (with `mcp__` prefix)
2. If available, prefer MCP tool over built-in equivalent
3. MCP tools may have fewer restrictions or additional capabilities

#### Configuration Methods
1. **CLI Wizard**: `claude mcp add` (official method)
2. **Direct Configuration**: Edit JSON config files (more control)
3. **Remote Servers**: Add vendor URL, no manual setup required

## Observed Environment

### Current Claude Code Instance
- No MCP resources currently available (`ListMcpResourcesTool` returns empty)
- Configuration exists at standard locations
- MCP servers configured but not active in this session

### MCP Servers Found in Local Configuration
1. `browser-tools` (Claude Code)
2. `developer-assistant` (Claude Desktop)
3. `browsermcp` (Claude Desktop)
4. `puppeteer` (Claude Desktop)
5. `memory` (Claude Desktop)
6. `brave-search` (Claude Desktop)
7. `mcp-installer` (Claude Desktop)
8. `server-filesystem` (Claude Desktop)
9. `mcp-pandoc` (Claude Desktop)

## Technical Implementation Details

### Transport Interface
```typescript
interface Transport {
  start(): Promise<void>;
  send(message: JSONRPCMessage): Promise<void>;
  close(): Promise<void>;
  onclose?: () => void;
  onerror?: (error: Error) => void;
  onmessage?: (message: JSONRPCMessage) => void;
}
```

### Recent Protocol Updates (2025-03-26)
1. OAuth 2.1 framework mandated for remote HTTP server authentication
2. Streamable HTTP transport replacing HTTP+SSE
3. Support for JSON-RPC batching
4. Improved security, scalability, and usability

## Practical Implications

1. **Tool Availability**: MCP tools are only available when servers are running
2. **Tool Naming**: Look for `mcp__` prefix to identify MCP-provided tools
3. **Configuration**: Both Claude Desktop and Claude Code use JSON configuration
4. **Remote vs Local**: Remote MCP servers offer lower maintenance with automatic updates
5. **Authentication**: OAuth support ensures secure connections without managing API keys

## Conclusion

MCP provides a standardized protocol for AI-tool integration, using JSON-RPC 2.0 over various transports. In the Claude ecosystem, MCP tools are distinguished by the `mcp__` prefix and should be preferred over built-in equivalents when available. The protocol supports both local subprocess servers and remote OAuth-authenticated servers, with configuration managed through JSON files in platform-specific locations.