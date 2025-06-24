# MCP (Model Context Protocol) Usage Guide

## Understanding MCPs

MCP servers are external tools that extend Claude's capabilities. They run as separate processes and communicate with Claude through a standardized protocol.

## Common MCP Issues and Solutions

### 1. Connection Issues
- **Problem**: "Server not connected" errors
- **Cause**: MCP servers need to be properly registered with Claude
- **Solution**: Restart Claude Code or check MCP configuration

### 2. Tool Discovery
The correct way to use MCPs:

```python
# First, list available MCP servers
ListMcpResourcesTool(server="")  # Lists all servers

# Then, list resources for a specific server
ListMcpResourcesTool(server="browsermcp")  # Lists browsermcp resources

# Finally, use the specific tool
# Note: MCP tools are exposed as regular tools with "mcp__" prefix
```

### 3. Browser MCP Specific Usage

The browser MCP typically provides tools like:
- `mcp__browsermcp__navigate` - Navigate to a URL
- `mcp__browsermcp__screenshot` - Take a screenshot
- `mcp__browsermcp__click` - Click an element
- `mcp__browsermcp__type` - Type text
- `mcp__browsermcp__evaluate` - Run JavaScript

### 4. Common Mistakes
1. **Wrong tool names**: Using `ReadMcpResourceTool` instead of the actual tool
2. **Missing prefix**: Not using the `mcp__` prefix
3. **Server not started**: MCP server process not running
4. **Configuration issues**: MCP not properly configured in Claude

## Testing Without Browser MCP

When browser MCP isn't working, we can still test using:

1. **API Testing with curl**
```bash
# Create a cart
curl -X POST http://localhost:8000/api/cart/ \
  -H "Content-Type: application/json" \
  -d '{"product_id": "...", "quantity": 1, "session_id": "cart_123"}'

# Check cart
curl http://localhost:8000/api/cart/?session_id=cart_123
```

2. **Browser Console Testing**
```javascript
// Check localStorage
localStorage.getItem('cartId')
localStorage.getItem('cartItems')

// Monitor network requests
// Open DevTools > Network tab
// Watch for cart_session_id in requests
```

3. **Manual Testing Steps**
1. Open browser to http://localhost:3000
2. Open DevTools (F12)
3. Go to Application > Local Storage
4. Add items to cart
5. Note the cartId value
6. Go to checkout
7. Watch Network tab for the cart_session_id sent
8. Compare if they match

## Alternative Testing Approach

Since browser MCP is having issues, let's use a combination of:
1. Direct API calls to simulate the flow
2. Database queries to check state
3. Log analysis to trace the issue
4. Manual browser testing with console commands