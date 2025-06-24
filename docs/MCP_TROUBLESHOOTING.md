# MCP (Model Context Protocol) Troubleshooting Guide

## Understanding MCP Configuration

### MCP Server Scopes

Claude Code supports three configuration scopes:

1. **User Scope** (recommended for browser tools)
   - Available across all projects
   - Private to your user account
   - Perfect for utility servers like browser tools

2. **Local Scope** (default)
   - Stored in project-specific user settings
   - Private to the current project directory
   - Ideal for personal or experimental configurations

3. **Project Scope**
   - Stored in `.mcp.json` at project root
   - Can be committed to version control
   - Requires user approval before use

### Correct Way to Add MCP Servers

Use the Claude Code CLI commands, NOT manual JSON configuration:

```bash
# Add browser tools with user scope (available in all projects)
claude mcp add --scope user browser-tools npx @agentdeskai/browser-tools-mcp@latest
claude mcp add --scope user browsermcp npx -- -y @browsermcp/mcp@0.1.3
claude mcp add --scope user puppeteer npx -- -y @modelcontextprotocol/server-puppeteer

# List configured servers
claude mcp list

# Check server status in Claude Code
/mcp
```

### Important Notes

1. **Manual JSON configuration (`~/.claude-code/mcp.json`) doesn't work reliably**. Use the CLI commands instead.

2. **Use `--` to separate claude options from npx arguments**:
   ```bash
   claude mcp add --scope user browsermcp npx -- -y @browsermcp/mcp@0.1.3
   ```

3. **Start Claude Code with permissions flag for browser tools**:
   ```bash
   claude --dangerously-skip-permissions
   ```

### Verification Steps

1. Check Claude Code version: `claude --version`
2. Verify npx is installed: `which npx && npx --version`
3. List configured servers: `claude mcp list`
4. In Claude Code, run: `/mcp` to see server status

### Troubleshooting

If servers still don't appear:
1. Restart Claude Code with `claude --dangerously-skip-permissions`
2. Check server status with `/mcp` command inside Claude Code
3. For project-scoped servers, reset approvals: `claude mcp reset-project-choices`
4. Set timeout if servers are slow: `export MCP_TIMEOUT=30000`

### Configuration Precedence

Claude Code loads servers in this order: local > project > user scopes. Servers with the same name are resolved by prioritizing local-scoped servers first.