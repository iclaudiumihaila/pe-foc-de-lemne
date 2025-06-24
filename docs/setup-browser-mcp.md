# Setting Up Browser MCPs for Claude Code

## Configuration Locations

Claude Code looks for MCP configurations in these locations:
1. `~/.config/claude-code/mcp.json` - Primary configuration for Claude Code
2. `~/Library/Application Support/Claude/claude_desktop_config.json` - Claude Desktop app config

## Steps to Enable Browser MCPs

### 1. Update Claude Code MCP Configuration

Edit `~/.config/claude-code/mcp.json`:

```json
{
  "mcpServers": {
    "browser-tools": {
      "command": "npx",
      "args": ["@agentdeskai/browser-tools-mcp@latest"]
    },
    "browsermcp": {
      "command": "npx",
      "args": [
        "-y",
        "@browsermcp/mcp@0.1.3"
      ]
    },
    "puppeteer": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-puppeteer"
      ]
    }
  }
}
```

### 2. Restart Claude Code

After updating the configuration:
1. Close all Claude Code sessions
2. Restart Claude Code with: `claude --dangerously-skip-permissions`
3. The browser MCP tools should now be available

### 3. Available Browser MCP Servers

1. **@agentdeskai/browser-tools-mcp** - Browser automation tools
2. **@browsermcp/mcp** - Browser control MCP
3. **@modelcontextprotocol/server-puppeteer** - Puppeteer-based browser automation

### 4. Verifying Installation

Once configured, browser MCP tools should appear with prefixes like:
- `mcp__browser-tools__*`
- `mcp__browsermcp__*`
- `mcp__puppeteer__*`

## Troubleshooting

If browser MCPs don't appear:
1. Check that npx is installed: `which npx`
2. Verify the MCP packages can be installed: `npx -y @browsermcp/mcp@0.1.3 --help`
3. Check Claude Code logs for MCP initialization errors
4. Ensure the configuration file has proper JSON syntax

## Security Note

Browser MCPs have access to control web browsers on your system. Only use trusted MCP packages and be aware of the permissions they require.