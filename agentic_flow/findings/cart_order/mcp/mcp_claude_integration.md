# Understanding MCP Integration: Claude Desktop vs Claude Code

## The Key Difference

### Claude Desktop App
- Has built-in MCP support
- MCPs are configured in `~/Library/Application Support/Claude/claude_desktop_config.json`
- Automatically connects to MCP servers on startup
- Shows MCP tools in the UI

### Claude Code (CLI)
- **Does NOT have built-in MCP support**
- Cannot directly use MCP tools
- This is why you see "Server not connected" errors
- MCP processes are running but Claude Code can't connect to them

## How MCPs Actually Work

1. **MCP Server Process**
   - Runs as a separate process (you can see them with `ps aux | grep mcp`)
   - Listens on a local port or pipe
   - Implements the Model Context Protocol

2. **Client Connection**
   - Claude Desktop: Has MCP client built-in
   - Claude Code: NO MCP client implementation

3. **Configuration**
   ```json
   // ~/Library/Application Support/Claude/claude_desktop_config.json
   {
     "mcpServers": {
       "browsermcp": {
         "command": "npx",
         "args": ["@browsermcp/mcp@latest"],
         "disabled": false
       }
     }
   }
   ```

## Why This Matters

**Claude Code is designed for:**
- File manipulation
- Code generation
- Running commands
- Direct system interaction

**Claude Desktop is designed for:**
- Web browsing (via browser MCP)
- Extended capabilities through MCPs
- More interactive workflows

## Solutions for Testing in Claude Code

Since we can't use browser MCP in Claude Code, here are alternatives:

### 1. Use Direct Commands
```bash
# Open browser manually
open http://localhost:3000

# Use curl for API testing
curl -X POST http://localhost:8000/api/cart/

# Check browser console manually
# Then report findings back
```

### 2. Create Test Scripts
```python
# Create automated test scripts
# Run them with bash
python test_checkout_flow.py
```

### 3. Use Browser DevTools
1. Open browser manually
2. Open DevTools (F12)
3. Run JavaScript in console:
```javascript
// Check cart state
console.log('Cart ID:', localStorage.getItem('cartId'));
console.log('Cart Items:', localStorage.getItem('cartItems'));

// Monitor network
fetch('/api/checkout/send-code', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ phone: '0775156791' })
}).then(r => r.json()).then(console.log);
```

### 4. Database Inspection
```bash
# Check what's in the database
python check_cart.py
python check_checkout_session.py
```

## The Bottom Line

**In Claude Code**, we need to:
1. Test manually in the browser
2. Use API calls with curl
3. Write test scripts
4. Inspect logs and databases

**MCP tools only work in Claude Desktop app**, not in Claude Code CLI.

This is why your browser MCP works in the desktop app but shows as "failed" or "not connected" in Claude Code.