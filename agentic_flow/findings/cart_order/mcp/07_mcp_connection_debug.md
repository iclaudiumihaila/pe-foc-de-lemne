# MCP Connection Debugging Guide

## Overview

Model Context Protocol (MCP) servers provide external capabilities to Claude through a standardized interface. This guide documents how MCP connections work, common issues, and troubleshooting steps.

## System Architecture

### 1. MCP Server Communication

MCP servers communicate with Claude clients through:
- **Standard I/O streams** (stdin/stdout) for command-based servers
- **JSON-RPC protocol** for message passing
- **Process spawning** by the Claude desktop app or Claude Code

### 2. Configuration Locations

MCP configurations can be found in multiple locations:

#### Claude Desktop App
- **Primary config**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Contains `mcpServers` object with server definitions

#### Claude Code CLI
- **Primary config**: `~/.claude-code/mcp.json`
- **Secondary config**: `~/.config/claude-code/mcp.json`
- Both use the same format as Claude Desktop

### 3. Server Process Management

MCP servers are spawned as child processes:
- Each server runs in its own process
- Communication happens through pipes
- Servers remain running while Claude app is active

## Common Connection Issues

### Issue 1: MCP Tools Not Available in Claude Code

**Symptoms**:
- `ListMcpResourcesTool` returns empty results or "Server not found"
- MCP tools work in Claude Desktop but not Claude Code

**Root Cause**:
Claude Code CLI currently has limited MCP support compared to Claude Desktop. The MCP servers configured in Claude Desktop (`claude_desktop_config.json`) are not automatically available to Claude Code.

**Solution**:
1. Configure servers specifically for Claude Code in `~/.claude-code/mcp.json`
2. Ensure the server command and args are correct
3. Restart Claude Code after configuration changes

### Issue 2: Server Process Not Starting

**Symptoms**:
- No server process visible in `ps aux`
- Connection timeouts

**Debugging Steps**:
```bash
# Check if server process is running
ps aux | grep -E "(mcp|modelcontextprotocol)" | grep -v grep

# Check for error logs
tail -f ~/Library/Logs/Claude/*.log

# Test server command manually
npx @modelcontextprotocol/server-memory
```

### Issue 3: Configuration Not Loading

**Symptoms**:
- Servers defined in config but not available
- Changes to config not taking effect

**Solutions**:
1. Verify JSON syntax in configuration files
2. Check file permissions: `chmod 644 ~/.claude-code/mcp.json`
3. Ensure correct nesting of `mcpServers` object
4. Restart Claude Code completely

## Step-by-Step Troubleshooting Process

### 1. Verify Configuration

```bash
# Check Claude Desktop config
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | jq .

# Check Claude Code config
cat ~/.claude-code/mcp.json | jq .
```

### 2. Check Running Processes

```bash
# List all MCP-related processes
ps aux | grep -E "(mcp|modelcontextprotocol|claude)" | grep -v grep

# Check specific process connections
lsof -p <PID> | grep -E "(TCP|PIPE|UNIX)"
```

### 3. Test Server Availability

```bash
# In Claude Code, try listing resources
# This will show if servers are properly connected
```

### 4. Verify Network Connectivity

```bash
# Check Claude Code SSE port
lsof -i :$CLAUDE_CODE_SSE_PORT

# Check for any firewall rules blocking local connections
sudo pfctl -s rules | grep -i local
```

### 5. Enable Debug Logging

Set environment variables for more verbose output:
```bash
export DEBUG=mcp:*
export NODE_ENV=development
claude
```

## Test Commands

### Basic Connectivity Test

1. Create a minimal test configuration:
```json
{
  "mcpServers": {
    "test-server": {
      "command": "echo",
      "args": ["MCP server test"]
    }
  }
}
```

2. Save to `~/.claude-code/mcp.json`

3. Restart Claude Code and check if server appears

### Server Health Check

For npm-based servers:
```bash
# Test server can be installed and run
npx <server-package> --version

# Check npm cache for issues
npm cache verify
```

For Python servers:
```bash
# Test Python environment
python3 --version
which python3

# Test server module
python3 -m <server_module> --help
```

## Configuration Examples

### Working Claude Desktop Configuration
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "@modelcontextprotocol/server-filesystem",
        "/Users/username/Documents"
      ]
    },
    "memory": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-memory"]
    }
  }
}
```

### Environment Variables for Servers
```json
{
  "mcpServers": {
    "api-server": {
      "command": "node",
      "args": ["./api-server.js"],
      "env": {
        "API_KEY": "your-key-here",
        "PATH": "/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}
```

## Current Limitations

### Claude Code vs Claude Desktop

1. **Configuration Independence**: Claude Code does not automatically use Claude Desktop's MCP configuration
2. **Limited MCP Support**: Not all MCP features available in Claude Desktop work in Claude Code
3. **No UI for Configuration**: Must manually edit JSON files for Claude Code

### Known Issues

1. **Server Discovery**: Claude Code may not discover all configured servers
2. **Resource Listing**: `ListMcpResourcesTool` may return empty results even with servers running
3. **Connection Persistence**: Servers may need to be restarted if Claude Code is restarted

## Recommendations

1. **Use Claude Desktop** for full MCP functionality when possible
2. **Keep Configurations Simple** in Claude Code - start with basic servers
3. **Monitor Processes** to ensure servers are running correctly
4. **Check Logs** regularly for error messages
5. **Test Incrementally** - add one server at a time and verify it works

## Future Improvements

Based on current architecture, potential improvements could include:
1. Unified configuration between Claude Desktop and Claude Code
2. Better error reporting for MCP connection failures
3. Built-in health checks for MCP servers
4. Automatic server restart on failure
5. GUI configuration tools for Claude Code

## Conclusion

MCP connections in Claude Code are currently limited compared to Claude Desktop. While the infrastructure exists (configuration files, process management), the integration is not complete. For reliable MCP usage, Claude Desktop remains the recommended platform until Claude Code's MCP support is enhanced.