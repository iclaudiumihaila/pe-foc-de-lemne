# Complete MCP (Model Context Protocol) Guide

## What is MCP?

MCP is a protocol that allows Claude to communicate with external tools and services. Think of it as a bridge between Claude and specialized capabilities like:
- Browser automation
- File system access
- Memory/knowledge storage
- Web search
- Custom tools

## How MCPs Work

### 1. Architecture
```
Claude Desktop App
    ↓
MCP Client (built into Claude)
    ↓
JSON-RPC over stdin/stdout
    ↓
MCP Server (external process)
    ↓
Actual Tool (browser, filesystem, etc.)
```

### 2. Configuration Location
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### 3. MCP Server Types

#### NPX-based MCPs (most common)
```json
{
  "browsermcp": {
    "command": "npx",
    "args": ["-y", "@browsermcp/mcp@0.1.3"]
  }
}
```

#### Python-based MCPs
```json
{
  "developer-assistant": {
    "command": "python3",
    "args": ["/path/to/server.py"],
    "env": {}
  }
}
```

#### Binary MCPs
```json
{
  "custom-tool": {
    "command": "/usr/local/bin/custom-mcp",
    "args": ["--mode", "server"]
  }
}
```

## Starting MCPs

### 1. Automatic Start (Claude Desktop)
- MCPs start automatically when Claude Desktop launches
- They're managed by the Claude app
- Restart Claude to reload MCP configuration

### 2. Manual Start (for testing)
```bash
# Browser MCP
npx -y @browsermcp/mcp@0.1.3

# Memory MCP
npx -y @modelcontextprotocol/server-memory

# Custom Python MCP
python3 /path/to/mcp_server.py
```

### 3. Checking MCP Status
```bash
# See all running MCP processes
ps aux | grep mcp

# Check specific MCP
ps aux | grep browsermcp

# Check MCP logs (if available)
# MCPs usually log to stderr, which Claude captures
```

## Using MCPs in Claude

### 1. Tool Discovery
When MCPs are connected, their tools appear with the `mcp__` prefix:
- `mcp__browsermcp__navigate`
- `mcp__browsermcp__screenshot`
- `mcp__memory__store`
- `mcp__memory__retrieve`

### 2. Browser MCP Example
```python
# Navigate to a page
mcp__browsermcp__navigate(url="https://example.com")

# Take a screenshot
mcp__browsermcp__screenshot()

# Click an element
mcp__browsermcp__click(selector="#submit-button")

# Type text
mcp__browsermcp__type(selector="#email", text="user@example.com")

# Execute JavaScript
mcp__browsermcp__evaluate(script="return document.title")
```

### 3. Memory MCP Example
```python
# Store information
mcp__memory__store(key="user_preferences", value={"theme": "dark"})

# Retrieve information
mcp__memory__retrieve(key="user_preferences")

# List all stored items
mcp__memory__list()
```

## Troubleshooting MCPs

### 1. MCP Not Showing Up
**Check configuration:**
```bash
# Verify config file exists and is valid JSON
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | jq .
```

**Restart Claude:**
- Completely quit Claude (Cmd+Q on Mac)
- Start Claude again
- MCPs should reconnect

### 2. MCP Crashes
**Check logs:**
```bash
# Claude logs (Mac)
tail -f ~/Library/Logs/Claude/mcp.log

# Or check Console app for Claude-related logs
```

**Test manually:**
```bash
# Run the MCP command directly to see errors
npx -y @browsermcp/mcp@0.1.3
```

### 3. Connection Issues
**Common causes:**
- Invalid JSON in config
- Wrong command path
- Missing dependencies
- Port conflicts

**Debug steps:**
1. Validate JSON config
2. Test command manually
3. Check for port conflicts
4. Review Claude logs

## Creating Custom MCPs

### 1. Basic Python MCP Server
```python
#!/usr/bin/env python3
import json
import sys

def handle_request(request):
    if request["method"] == "tools/list":
        return {
            "tools": [{
                "name": "hello",
                "description": "Says hello",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"}
                    }
                }
            }]
        }
    elif request["method"] == "tools/call":
        if request["params"]["name"] == "hello":
            name = request["params"]["arguments"].get("name", "World")
            return {"content": f"Hello, {name}!"}

# Main loop
while True:
    line = sys.stdin.readline()
    if not line:
        break
    request = json.loads(line)
    response = handle_request(request)
    sys.stdout.write(json.dumps(response) + "\n")
    sys.stdout.flush()
```

### 2. Add to Config
```json
{
  "mcpServers": {
    "my-custom-mcp": {
      "command": "python3",
      "args": ["/path/to/my_mcp_server.py"]
    }
  }
}
```

## Important Notes

1. **Claude Code vs Claude Desktop**
   - Only Claude Desktop supports MCPs
   - Claude Code (CLI) cannot use MCPs
   - This is a fundamental limitation

2. **Security**
   - MCPs have access to your system
   - Only install trusted MCPs
   - Review MCP code before using

3. **Performance**
   - MCPs run as separate processes
   - They add some latency
   - Keep MCPs lightweight

4. **Debugging**
   - Use Console app (Mac) or Event Viewer (Windows)
   - Run MCPs manually to see errors
   - Check Claude's logs for connection issues