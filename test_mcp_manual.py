#!/usr/bin/env python3
"""
Manual MCP interaction test
This shows how Claude Desktop communicates with MCPs
"""

import subprocess
import json
import sys

def send_to_mcp(process, request):
    """Send a request to MCP and get response"""
    request_str = json.dumps(request) + '\n'
    process.stdin.write(request_str.encode())
    process.stdin.flush()
    
    response_line = process.stdout.readline()
    return json.loads(response_line)

def test_memory_mcp():
    """Test the memory MCP server"""
    print("Starting Memory MCP server...")
    
    # Start the MCP process
    process = subprocess.Popen(
        ['npx', '-y', '@modelcontextprotocol/server-memory'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False
    )
    
    try:
        # Initialize connection
        print("\n1. Sending initialize request...")
        init_request = {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "0.1.0",
                "capabilities": {}
            },
            "id": 1
        }
        
        response = send_to_mcp(process, init_request)
        print(f"Response: {json.dumps(response, indent=2)}")
        
        # List available tools
        print("\n2. Listing available tools...")
        tools_request = {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "id": 2
        }
        
        response = send_to_mcp(process, tools_request)
        print(f"Available tools: {json.dumps(response, indent=2)}")
        
        # Call a tool (store something)
        print("\n3. Storing a value...")
        store_request = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "store",
                "arguments": {
                    "key": "test_key",
                    "value": "Hello from manual test!"
                }
            },
            "id": 3
        }
        
        response = send_to_mcp(process, store_request)
        print(f"Store response: {json.dumps(response, indent=2)}")
        
    finally:
        process.terminate()

if __name__ == "__main__":
    test_memory_mcp()