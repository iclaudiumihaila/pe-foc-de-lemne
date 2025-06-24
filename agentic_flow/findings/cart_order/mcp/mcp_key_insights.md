# Key Insights About MCPs

## 1. MCP Communication Protocol

MCPs use JSON-RPC 2.0 over stdin/stdout:
```json
// Request format
{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "id": 1
}

// Response format
{
  "jsonrpc": "2.0",
  "result": { ... },
  "id": 1
}
```

## 2. MCP Lifecycle

1. **Initialize**: Establish protocol version and capabilities
2. **Tools/List**: Discover available tools
3. **Tools/Call**: Execute specific tools with arguments
4. **Shutdown**: Clean termination

## 3. Why MCPs Don't Work in Claude Code

**Claude Desktop has an MCP client that:**
- Manages MCP process lifecycle
- Translates tool calls to JSON-RPC
- Handles responses and errors
- Exposes tools with `mcp__` prefix

**Claude Code lacks this MCP client**, so even though MCP servers are running, Claude Code can't communicate with them.

## 4. MCP Tools in Claude Desktop

When you use Claude Desktop, you see tools like:
- `mcp__browsermcp__navigate`
- `mcp__browsermcp__click`
- `mcp__memory__create_entities`

These are NOT available in Claude Code because there's no MCP client.

## 5. Testing Without MCPs in Claude Code

Since we're in Claude Code, we need alternative approaches:

### For Browser Testing:
```bash
# Use curl for API testing
curl -X POST http://localhost:8000/api/cart/ \
  -H "Content-Type: application/json" \
  -d '{"product_id": "123", "quantity": 1, "session_id": "cart_123"}'

# Create Python test scripts
python3 test_checkout_flow.py

# Use browser console manually
# Open http://localhost:3000 in browser
# Press F12 for DevTools
# Run: localStorage.getItem('cartId')
```

### For File Operations:
```bash
# Claude Code has built-in file tools
# Use Read, Write, Edit, MultiEdit tools
```

### For Web Search:
```bash
# Use WebSearch tool (built into Claude Code)
# Or use curl with APIs
```

## 6. Running MCPs Manually (for learning)

You can interact with MCPs directly to understand them:

```python
import subprocess
import json

# Start an MCP
proc = subprocess.Popen(
    ['npx', '-y', '@browsermcp/mcp@latest'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True
)

# Send initialize
request = {
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
        "protocolVersion": "0.1.0",
        "clientInfo": {
            "name": "test-client",
            "version": "1.0.0"
        }
    },
    "id": 1
}

proc.stdin.write(json.dumps(request) + '\n')
proc.stdin.flush()
response = proc.stdout.readline()
print(json.loads(response))
```

## 7. The Bottom Line

- **MCPs are amazing in Claude Desktop** - they extend Claude's capabilities
- **MCPs don't work in Claude Code** - this is by design
- **Claude Code has its own tools** - file operations, bash, web search, etc.
- **For testing, use alternative methods** - scripts, curl, manual browser testing

## 8. When to Use What

### Use Claude Desktop (with MCPs) for:
- Browser automation testing
- Visual web scraping
- Interactive debugging
- Complex browser interactions

### Use Claude Code for:
- Code generation and editing
- File operations
- Running commands
- API testing with curl
- Writing test scripts

The key is choosing the right tool for the job!