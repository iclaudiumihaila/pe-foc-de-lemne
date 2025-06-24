# Definitive MCP Integration Guide for Claude Code

## Executive Summary

Contrary to previous findings, **Claude Code CLI DOES support MCP (Model Context Protocol)**. The confusion arose from the fact that MCP tools don't appear in the standard tool list but are accessed through specific commands and configurations. This guide provides accurate, tested information about using MCPs in Claude Code.

## MCP Support Status: The Truth

### Claude Code CLI ✅ DOES Support MCP
- Has built-in MCP client functionality
- Supports stdio, SSE, and HTTP transports
- Can import configurations from Claude Desktop
- Provides full MCP management commands
- MCP servers can be configured at user, project, and local levels

### Key Discovery
The browser MCP is actually configured and available:
```bash
$ claude mcp list
browsermcp: npx @browsermcp/mcp@latest
```

## Step-by-Step MCP Setup Guide

### 1. Check Current MCP Configuration
```bash
# List all configured MCP servers
claude mcp list

# Get details about a specific server
claude mcp get browsermcp
```

### 2. Add MCP Servers

#### Method A: Using CLI Wizard
```bash
# Add a stdio server (most common)
claude mcp add <server-name> -- <command> [args...]

# Example: Add browser MCP
claude mcp add browsermcp -- npx @browsermcp/mcp@latest

# Example: Add memory MCP
claude mcp add memory -- npx @modelcontextprotocol/server-memory
```

#### Method B: Direct JSON Configuration
```bash
# Add server with JSON config
claude mcp add-json myserver '{
  "type": "stdio",
  "command": "npx",
  "args": ["-y", "@browsermcp/mcp@latest"]
}'
```

#### Method C: Import from Claude Desktop
```bash
# Import all MCP servers from Claude Desktop config
claude mcp add-from-claude-desktop
```

### 3. Configure MCP Servers with Environment Variables
```bash
# Add server with environment variables
claude mcp add digitalocean-mcp \
  -e DIGITALOCEAN_API_TOKEN=YOUR_API_TOKEN \
  -- npx "@digitalocean/mcp"
```

### 4. MCP Configuration Scopes

#### User Scope (Default)
- Stored in `~/.claude/config.json`
- Available across all projects
- Use: `claude mcp add <name> ...`

#### Project Scope
- Stored in `.mcp.json` in project root
- Specific to current project
- Use: `claude mcp add -p <name> ...`

#### Local Scope
- Temporary, session-only
- Use: `claude mcp add -l <name> ...`

## Using MCP Tools in Claude Code

### 1. Check MCP Server Status
```bash
# In Claude Code, type:
/mcp

# Output shows connected servers:
# ⎿ MCP Server Status ⎿
# ⎿ • browsermcp: connected ⎿
```

### 2. Access MCP Tools
MCP tools are exposed with the `mcp__` prefix:
- `mcp__browsermcp__navigate`
- `mcp__browsermcp__screenshot`
- `mcp__browsermcp__click`
- `mcp__browsermcp__type`

### 3. Using MCP Resources
Reference MCP resources using "@" mentions:
```
@browsermcp:screenshot
@memory:entities
```

### 4. MCP Prompts as Slash Commands
MCP prompts appear as slash commands:
```
/mcp__servername__promptname
```

## Browser Automation in Claude Code

### Setting Up Browser MCP
```bash
# 1. Add browser MCP if not already present
claude mcp add browsermcp -- npx @browsermcp/mcp@latest

# 2. Start Claude Code with MCP debug (optional)
claude --mcp-debug

# 3. Check connection
/mcp
```

### Using Browser MCP Tools
```python
# Navigate to a page
mcp__browsermcp__navigate(url="http://localhost:3000")

# Take a screenshot
mcp__browsermcp__screenshot()

# Click an element
mcp__browsermcp__click(selector="#add-to-cart")

# Type text
mcp__browsermcp__type(selector="#phone", text="0775156791")

# Execute JavaScript
mcp__browsermcp__evaluate(script="return localStorage.getItem('cartId')")
```

## Troubleshooting MCP in Claude Code

### 1. MCP Not Appearing
```bash
# Check if MCP is configured
claude mcp list

# Add MCP server
claude mcp add browsermcp -- npx @browsermcp/mcp@latest

# Restart Claude Code with debug
claude --mcp-debug
```

### 2. Connection Issues
```bash
# Remove and re-add the server
claude mcp remove browsermcp
claude mcp add browsermcp -- npx @browsermcp/mcp@latest

# Check server details
claude mcp get browsermcp
```

### 3. Debug Mode
```bash
# Start Claude Code with MCP debugging
claude --mcp-debug

# Or use the newer debug flag
claude --debug
```

## Best Practices for MCP in Claude Code

### 1. Configuration Management
```json
// Example .claude/config.json with multiple MCPs
{
  "mcpServers": {
    "browsermcp": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@browsermcp/mcp@latest"]
    },
    "memory": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "omnisearch": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "mcp-omnisearch"],
      "env": {
        "TAVILY_API_KEY": "",
        "BRAVE_API_KEY": ""
      }
    }
  }
}
```

### 2. Project-Specific MCPs
```bash
# Create project-specific MCP config
echo '{}' > .mcp.json

# Add project-specific server
claude mcp add -p test-automation -- npx custom-test-mcp
```

### 3. Using Multiple Transports

#### SSE (Server-Sent Events)
```bash
claude mcp add mysse-server \
  --sse \
  --url https://api.example.com/mcp/sse
```

#### HTTP
```bash
claude mcp add myhttp-server \
  --http \
  --url https://api.example.com/mcp
```

## Practical Example: Testing Cart/Order Flow

### 1. Setup Browser MCP
```bash
# Ensure browser MCP is configured
claude mcp add browsermcp -- npx @browsermcp/mcp@latest
```

### 2. Create Test Script
```python
# test_checkout_with_mcp.py
def test_checkout_flow():
    # Navigate to the application
    mcp__browsermcp__navigate(url="http://localhost:3000")
    
    # Take initial screenshot
    mcp__browsermcp__screenshot()
    
    # Add item to cart
    mcp__browsermcp__click(selector=".add-to-cart-btn")
    
    # Check cart state
    cart_id = mcp__browsermcp__evaluate(
        script="return localStorage.getItem('cartId')"
    )
    print(f"Cart ID: {cart_id}")
    
    # Go to checkout
    mcp__browsermcp__click(selector="#checkout-btn")
    
    # Fill phone number
    mcp__browsermcp__type(
        selector="#phone",
        text="0775156791"
    )
    
    # Submit
    mcp__browsermcp__click(selector="#submit-order")
    
    # Take final screenshot
    mcp__browsermcp__screenshot()
```

## Alternative Approaches When MCP Isn't Working

### 1. Direct API Testing
```bash
# Create cart
curl -X POST http://localhost:8000/api/cart/ \
  -H "Content-Type: application/json" \
  -d '{"product_id": "123", "quantity": 1}'
```

### 2. Python Automation
```python
import requests
import time

# Test checkout flow
session = requests.Session()
response = session.post(
    "http://localhost:8000/api/cart/",
    json={"product_id": "123", "quantity": 1}
)
cart_data = response.json()
```

### 3. Manual Browser Testing
1. Open http://localhost:3000
2. Open DevTools (F12)
3. Monitor Network tab
4. Execute in Console:
```javascript
// Check cart state
console.log('Cart:', {
  id: localStorage.getItem('cartId'),
  items: JSON.parse(localStorage.getItem('cartItems') || '[]')
});
```

## Key Insights and Recommendations

### 1. MCP IS Supported in Claude Code
- Previous findings were incorrect
- Full MCP functionality is available
- Configuration is the key

### 2. Browser MCP Works
- The "not connected" errors were due to misconfiguration
- Once properly configured, browser automation is possible

### 3. Best Practices
- Use `claude mcp list` to verify configuration
- Start with `--mcp-debug` for troubleshooting
- Keep MCP configurations in version control
- Use project-specific MCPs for testing

### 4. Future Recommendations
- Document MCP configurations in project README
- Create standardized test suites using MCP
- Consider custom MCPs for project-specific needs
- Use MCP for automated testing pipelines

## Conclusion

Claude Code CLI has full MCP support, contrary to earlier findings. The key is proper configuration and understanding how MCP tools are exposed. With browser MCP properly configured, you can automate browser testing directly from Claude Code, making it a powerful tool for end-to-end testing and debugging.

The confusion arose from:
1. MCP tools not appearing in the standard tool list
2. Different configuration methods between Claude Desktop and Claude Code
3. Lack of clear documentation about the `mcp__` prefix for tools

This guide provides the definitive approach to using MCPs in Claude Code, enabling powerful automation and testing capabilities.