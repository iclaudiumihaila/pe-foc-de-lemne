# MCP Tools Research Report

## Executive Summary

MCP (Model Context Protocol) is a protocol that enables Claude to communicate with external tools and services. However, there's a critical distinction between Claude Desktop (which has built-in MCP support) and Claude Code CLI (which does NOT support MCPs).

## Available MCP Tools in Claude Code

### 1. ListMcpResourcesTool
- **Purpose**: Lists available resources from configured MCP servers
- **Parameters**:
  - `server` (optional): Name of a specific MCP server to query. If not provided, returns resources from all servers
- **Returns**: Array of resources with standard MCP resource fields plus a 'server' field
- **Current Status**: Returns empty array `[]` in Claude Code (no MCP servers connected)

### 2. ReadMcpResourceTool
- **Purpose**: Reads a specific resource from an MCP server
- **Parameters**:
  - `server` (required): Name of the MCP server
  - `uri` (required): URI of the resource to read
- **Returns**: Resource content from the specified MCP server
- **Current Status**: Cannot be used as no MCP servers are connected

## How MCPs Actually Work

### Architecture
```
Application (Claude Desktop or Claude Code)
    ↓
MCP Client (built into application)
    ↓
JSON-RPC over stdin/stdout
    ↓
MCP Server (external process)
    ↓
Actual Tool (browser, filesystem, memory, etc.)
```

### MCP Communication Protocol
MCPs communicate using JSON-RPC 2.0 over stdin/stdout:
1. **Initialize**: Establish connection and protocol version
2. **List Tools**: Discover available capabilities
3. **Call Tools**: Execute specific functions
4. **Handle Resources**: Access server-provided resources

## Key Differences: Claude Desktop vs Claude Code

### Claude Desktop
- **Built-in MCP support**: Yes
- **Configuration**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Auto-connect**: MCPs start automatically on app launch
- **Tool naming**: MCP tools appear with `mcp__` prefix (e.g., `mcp__browsermcp__navigate`)
- **Available MCPs**: Browser, Memory, Filesystem, custom servers

### Claude Code (CLI)
- **Built-in MCP support**: No
- **MCP tools available**: Only `ListMcpResourcesTool` and `ReadMcpResourceTool` (but no servers to connect to)
- **Alternative tools**: WebFetch, WebSearch, Bash, file manipulation tools
- **Workaround**: Must use native tools or external scripts

## MCP Tool Naming Conventions

When MCPs are properly connected (in Claude Desktop), tools follow this pattern:
```
mcp__{server_name}__{tool_name}
```

Examples:
- `mcp__browsermcp__navigate`
- `mcp__browsermcp__screenshot`
- `mcp__memory__store`
- `mcp__memory__retrieve`

## Common MCP Servers

### 1. Browser MCP
Provides browser automation capabilities:
- `navigate`: Go to URL
- `screenshot`: Capture page
- `click`: Click elements
- `type`: Enter text
- `evaluate`: Run JavaScript
- `snapshot`: Get accessibility tree
- `get_console_logs`: Retrieve console output

### 2. Memory MCP
Persistent storage across sessions:
- `store`: Save key-value pairs
- `retrieve`: Get stored values
- `list`: Show all stored items
- `delete`: Remove items

### 3. Filesystem MCP
Enhanced file operations beyond Claude's built-in tools

## Why MCP Tools Don't Work in Claude Code

1. **No MCP Client**: Claude Code lacks the MCP client implementation present in Claude Desktop
2. **No Configuration**: No way to configure MCP servers in Claude Code
3. **Design Philosophy**: Claude Code is designed for direct system interaction, not extended capabilities
4. **Security Model**: Different security boundaries between desktop app and CLI

## Alternative Approaches in Claude Code

Since MCPs aren't available in Claude Code, use these alternatives:

### 1. For Browser Automation
```bash
# Use curl for API testing
curl -X POST http://localhost:8000/api/endpoint

# Open browser manually
open http://localhost:3000

# Use Python with Selenium/Playwright
python browser_test.py
```

### 2. For Persistent Storage
```python
# Use file system
with open('storage.json', 'w') as f:
    json.dump(data, f)

# Use database
python store_data.py
```

### 3. For Web Content
```python
# Use WebFetch tool (built into Claude Code)
WebFetch(url="https://example.com", prompt="Extract main content")

# Use WebSearch tool
WebSearch(query="search terms")
```

## Best Practices for MCP Usage

### In Claude Desktop
1. Check MCP configuration file for proper setup
2. Restart Claude to reload MCP connections
3. Use `mcp__` prefix for all MCP tools
4. Handle connection failures gracefully

### In Claude Code
1. Don't attempt to use MCP tools (except List/Read which show no servers)
2. Use native tools: Bash, Read, Write, Edit, WebFetch, WebSearch
3. Create Python scripts for complex automation
4. Use APIs and command-line tools as alternatives

## Testing MCP Connections

### Check if MCPs are available:
```python
# In Claude Code, this will return []
ListMcpResourcesTool()

# In Claude Desktop with MCPs configured, returns server list
ListMcpResourcesTool()  # Returns: [{"server": "browsermcp", ...}]
```

### Manual MCP Testing (for debugging):
```bash
# Start MCP server manually
npx -y @browsermcp/mcp@latest

# Or for memory MCP
npx -y @modelcontextprotocol/server-memory
```

## Conclusion

MCP tools provide powerful extensions to Claude's capabilities, but they're only available in Claude Desktop, not Claude Code. In Claude Code, we must rely on built-in tools and external scripts to achieve similar functionality. The `ListMcpResourcesTool` and `ReadMcpResourceTool` exist in Claude Code but are effectively non-functional without connected MCP servers.

For the cart/order debugging task at hand, we should use:
- Direct API calls with curl
- Database inspection scripts
- Manual browser testing with DevTools
- Log analysis
- Python test scripts

These alternatives provide the same debugging capabilities without requiring MCP support.