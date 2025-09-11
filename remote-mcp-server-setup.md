# Complete Guide: Running MCP Servers Over SSH Connections

**Note by Christina: The setup did not work (404 message of the server), but I feel like with more time and knowledge, one could make it work.**

## Table of Contents
1. [Problem Overview](#problem-overview)
2. [Solution Architecture](#solution-architecture)
3. [Prerequisites](#prerequisites)
4. [Method 1: HTTP/SSE with SSH Tunneling (Recommended)](#method-1-httpsse-with-ssh-tunneling-recommended)
5. [Method 2: Using Dedicated SSH-MCP Servers](#method-2-using-dedicated-ssh-mcp-servers)
6. [Security Configuration](#security-configuration)
7. [Troubleshooting](#troubleshooting)
8. [Production Considerations](#production-considerations)

## Problem Overview

### Why MCP Servers Fail in SSH Remote Environments

MCP servers encounter fundamental issues when VS Code connects to remote hosts via SSH because:

- **Execution Context Mismatch**: MCP servers defined in user settings always execute locally, even when VS Code is connected to a remote SSH host
- **Path Resolution Failures**: Local configurations reference remote paths that don't exist on the local machine
- **Environment Variable Issues**: Remote SSH sessions provide minimal environment variables, missing critical PATH extensions for Node.js, NPM, and development tools
- **Transport Assumptions**: STDIO transport assumes shared filesystem and environment contexts that don't exist across network boundaries

### Core Issue
The MCP specification assumes client and server share the same execution context, which breaks completely in remote SSH scenarios where workspace files exist remotely but MCP servers execute locally.

## Solution Architecture

This guide covers two primary approaches:

1. **HTTP/SSE Transport with SSH Tunneling** (Recommended)
   - Run MCP server as HTTP service on remote machine
   - Create SSH tunnel to forward traffic
   - VS Code connects to local port, traffic routes to remote server

2. **Dedicated SSH-MCP Servers**
   - Use community-built MCP servers designed for SSH operations
   - Execute SSH commands through MCP tools
   - Maintain local execution with remote command capabilities

## Prerequisites

### Local Machine Requirements
- VS Code with Remote-SSH extension
- SSH client (OpenSSH recommended)
- MCP-compatible client (VS Code with GitHub Copilot, Claude Desktop, etc.)
- Python 3.8+ or Node.js 18+ (depending on your MCP server)

### Remote Machine Requirements
- SSH server running and accessible
- Python 3.8+ or Node.js 18+ (for MCP server)
- Network connectivity on chosen ports
- Appropriate firewall configuration

### SSH Key Setup
```bash
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "your-email@example.com"

# Copy public key to remote server
ssh-copy-id user@remote-host

# Test connection
ssh user@remote-host "echo 'SSH connection working'"
```

## Method 1: HTTP/SSE with SSH Tunneling (Recommended)

### Step 1: Create MCP Server for HTTP Transport

Create a basic HTTP/SSE MCP server on your remote machine:

```python
# remote-mcp-server.py
import json
import sys
import jwt
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

# Configuration
SERVER_PORT = 8080
JWT_SECRET = "your-super-secure-secret-key-here"  # Change this!
JWT_ALGORITHM = "HS256"

def generate_token(user_id="default-user", scopes=["read", "write"]):
    """Generate a JWT token for authentication"""
    payload = {
        "sub": user_id,
        "iss": "mcp-remote-server",
        "aud": "mcp-client", 
        "exp": datetime.utcnow() + timedelta(hours=4),
        "iat": datetime.utcnow(),
        "scope": " ".join(scopes)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def validate_token(token):
    """Validate JWT token"""
    try:
        payload = jwt.decode(
            token, 
            JWT_SECRET, 
            algorithms=[JWT_ALGORITHM],
            audience="mcp-client",
            issuer="mcp-remote-server"
        )
        return payload
    except jwt.InvalidTokenError as e:
        print(f"Token validation failed: {e}")
        return None

class MCPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        """Custom logging"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

    def _check_auth(self):
        """Check authorization header"""
        auth_header = self.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            self.send_response(401)
            self.send_header('WWW-Authenticate', 'Bearer realm="MCP Server"')
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "Authentication required",
                "message": "Include 'Authorization: Bearer <token>' header"
            }).encode())
            return None
        
        token = auth_header[7:]  # Remove "Bearer " prefix
        payload = validate_token(token)
        if not payload:
            self.send_response(401)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "error": "Invalid token",
                "message": "Token is invalid or expired"
            }).encode())
            return None
        
        return payload

    def do_GET(self):
        if self.path == "/sse":
            # Authenticate request
            payload = self._check_auth()
            if not payload:
                return
            
            # Set up SSE response
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            # Send MCP initialization
            init_msg = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "remote-ssh-server",
                        "version": "1.0.0"
                    }
                }
            }
            
            self.wfile.write(f"data: {json.dumps(init_msg)}\n\n".encode())
            self.wfile.flush()
            
            # Keep connection alive
            try:
                while True:
                    time.sleep(30)
                    self.wfile.write(b"data: {\"type\":\"heartbeat\"}\n\n")
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                print("Client disconnected")
                
        elif self.path == "/health":
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path.startswith("/mcp/"):
            # Authenticate request
            payload = self._check_auth()
            if not payload:
                return
            
            # Handle MCP JSON-RPC requests
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                try:
                    request = json.loads(post_data.decode())
                    response = self._handle_mcp_request(request, payload)
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response).encode())
                except Exception as e:
                    print(f"Error handling request: {e}")
                    self.send_response(500)
                    self.end_headers()
            else:
                self.send_response(400)
                self.end_headers()
        else:
            self.send_response(404)
            self.end_headers()

    def _handle_mcp_request(self, request, user_payload):
        """Handle MCP JSON-RPC requests"""
        method = request.get("method")
        request_id = request.get("id")
        
        if method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "remote-ssh-server",
                        "version": "1.0.0"
                    }
                }
            }
        elif method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {
                    "tools": [
                        {
                            "name": "execute_command",
                            "description": "Execute a command on the remote server",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "command": {
                                        "type": "string",
                                        "description": "Command to execute"
                                    }
                                },
                                "required": ["command"]
                            }
                        }
                    ]
                }
            }
        elif method == "tools/call":
            tool_name = request.get("params", {}).get("name")
            if tool_name == "execute_command":
                command = request.get("params", {}).get("arguments", {}).get("command")
                if command:
                    import subprocess
                    try:
                        result = subprocess.run(
                            command, 
                            shell=True, 
                            capture_output=True, 
                            text=True,
                            timeout=30
                        )
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": f"Exit code: {result.returncode}\nStdout: {result.stdout}\nStderr: {result.stderr}"
                                    }
                                ]
                            }
                        }
                    except subprocess.TimeoutExpired:
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32000,
                                "message": "Command timed out"
                            }
                        }
                    except Exception as e:
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32000,
                                "message": f"Command failed: {str(e)}"
                            }
                        }
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": "Method not found"
            }
        }

def main():
    # Generate test token
    test_token = generate_token()
    
    print("=" * 60)
    print("MCP Remote Server Starting")
    print("=" * 60)
    print(f"Server: http://localhost:{SERVER_PORT}")
    print(f"Health: http://localhost:{SERVER_PORT}/health")
    print(f"SSE Endpoint: http://localhost:{SERVER_PORT}/sse")
    print(f"Test Token: {test_token}")
    print("=" * 60)
    print("Use this token in your VS Code MCP configuration")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    server = HTTPServer(('0.0.0.0', SERVER_PORT), MCPHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()

if __name__ == "__main__":
    main()
```

### Step 2: Install Dependencies on Remote Machine

```bash
# On remote machine
pip install PyJWT

# Make the script executable
chmod +x remote-mcp-server.py

# Test the server
python3 remote-mcp-server.py
```

### Step 3: Set Up SSH Tunnel

From your local machine, create an SSH tunnel:

```bash
# Basic tunnel (blocks terminal)
ssh -L 8080:localhost:8080 user@remote-host

# Background tunnel (persistent)
ssh -L 8080:localhost:8080 -N -f user@remote-host

# Tunnel with connection keep-alive
ssh -L 8080:localhost:8080 -N -o ServerAliveInterval=60 -o ServerAliveCountMax=3 user@remote-host

# To kill background tunnel later:
# ps aux | grep "ssh.*8080"
# kill <process_id>
```

### Step 4: Configure VS Code MCP Settings

Create or update your MCP configuration:

**Location**: `.vscode/mcp.json` (workspace) or use `MCP: Open Remote User Configuration`

```json
{
  "mcpServers": {
    "remote-ssh-server": {
      "type": "sse",
      "url": "http://localhost:8080/sse",
      "headers": {
        "Authorization": "Bearer YOUR_TOKEN_FROM_SERVER_OUTPUT"
      }
    }
  }
}
```

### Step 5: Test the Connection

1. Start the MCP server on remote machine
2. Establish SSH tunnel from local machine  
3. Copy the token from server output
4. Update VS Code configuration with the token
5. Restart VS Code or reload the MCP configuration
6. Open VS Code chat and verify the remote tools are available

## Method 2: Using Dedicated SSH-MCP Servers

### Option A: SSH-MCP by tufantunc

```bash
# Install globally
npm install -g ssh-mcp

# Or use npx (no installation required)
npx ssh-mcp --help
```

**VS Code Configuration:**
```json
{
  "mcpServers": {
    "ssh-remote": {
      "command": "npx",
      "args": [
        "ssh-mcp", 
        "--host=your-server-ip",
        "--port=22",
        "--user=username", 
        "--key=/path/to/private/key",
        "--timeout=30000"
      ]
    }
  }
}
```

### Option B: MCP Remote Machine Control

```bash
# Clone the repository
git clone https://github.com/frednov/mcp-remote-machine.git
cd mcp-remote-machine

# Install dependencies
pip install -r requirements.txt

# Run the server
python3 remote_machine_server.py --transport stdio
```

**VS Code Configuration:**
```json
{
  "mcpServers": {
    "remote-machine": {
      "command": "python3",
      "args": ["/path/to/remote_machine_server.py", "--transport", "stdio"],
      "env": {
        "PYTHONPATH": "/path/to/server"
      }
    }
  }
}
```

## Security Configuration

### Token Generation Best Practices

**For Development:**
```bash
# Generate random token
openssl rand -hex 32

# Or using Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

**For Production (JWT):**
```python
import jwt
from datetime import datetime, timedelta

def generate_production_token():
    secret = "your-256-bit-secret-key"  # Use environment variable
    payload = {
        "sub": "user-id",
        "iss": "your-mcp-server",
        "aud": "mcp-client",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
        "scope": "read write"
    }
    return jwt.encode(payload, secret, algorithm="HS256")
```

### Environment Variables

Create a `.env` file on your remote server:

```bash
# .env (never commit to version control)
MCP_JWT_SECRET=your-super-secure-secret-key-256-bits-long
MCP_TOKEN_EXPIRY=3600
MCP_SERVER_PORT=8080
MCP_ALLOWED_ORIGINS=*
MCP_LOG_LEVEL=INFO
```

Load in your server:
```python
import os
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv('MCP_JWT_SECRET', 'default-secret')
SERVER_PORT = int(os.getenv('MCP_SERVER_PORT', 8080))
```

### Security Classification Guidelines

| Classification | Use Case | Token Type | Expiration | Storage |
|---------------|----------|------------|------------|---------|
| **Development** | Local testing | Random string | 4-24 hours | Plain text OK |
| **Staging** | Pre-production | JWT | 1-4 hours | Encrypted config |
| **Production** | Live systems | OAuth 2.1 | 15-60 minutes | Secure vault |

### Firewall Configuration

**On remote server:**
```bash
# Allow SSH (if not already configured)
sudo ufw allow 22/tcp

# Allow MCP server port (adjust as needed)
sudo ufw allow 8080/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

## Troubleshooting

### Common Issues and Solutions

#### 1. "Connection Refused" Error
```bash
# Check if SSH tunnel is active
netstat -ln | grep 8080

# Verify remote server is running
ssh user@remote-host "curl -I http://localhost:8080/health"

# Check for port conflicts
lsof -i :8080
```

#### 2. Authentication Failures
```bash
# Test token manually
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8080/health

# Verify token hasn't expired
# Check server logs for specific error messages
```

#### 3. MCP Server Not Found in VS Code
- Ensure VS Code is restarted after configuration changes
- Check MCP configuration syntax in JSON file
- Use `MCP: List Servers` command to verify server registration
- Check VS Code Developer Tools Console for errors

#### 4. SSH Connection Issues
```bash
# Test basic SSH connectivity
ssh -v user@remote-host

# Test with tunnel verbosity
ssh -v -L 8080:localhost:8080 user@remote-host

# Check SSH configuration
cat ~/.ssh/config
```

#### 5. Environment Variable Problems
```bash
# Test environment on remote server
ssh user@remote-host "env | grep PATH"

# Create wrapper script if needed
cat > /usr/local/bin/node-wrapper << 'EOF'
#!/bin/bash
export PATH="/home/user/.nvm/versions/node/v18.17.0/bin:$PATH"
exec node "$@"
EOF
chmod +x /usr/local/bin/node-wrapper
```

### Debug Mode

Enable verbose logging in your MCP server:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# In your handler methods:
logging.debug(f"Received request: {self.path}")
logging.debug(f"Headers: {dict(self.headers)}")
```

### Testing Tools

**Test MCP Server Manually:**
```bash
# Health check
curl http://localhost:8080/health

# Test SSE endpoint (should require auth)
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8080/sse

# Test with MCP Inspector
npx @modelcontextprotocol/inspector http://localhost:8080/sse
```

## Production Considerations

### Process Management

Use systemd to manage your MCP server:

```ini
# /etc/systemd/system/mcp-server.service
[Unit]
Description=MCP Remote Server
After=network.target

[Service]
Type=simple
User=mcpuser
WorkingDirectory=/opt/mcp-server
ExecStart=/usr/bin/python3 /opt/mcp-server/remote-mcp-server.py
Restart=always
RestartSec=10
Environment=PATH=/usr/bin:/usr/local/bin
EnvironmentFile=/opt/mcp-server/.env

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable mcp-server
sudo systemctl start mcp-server
sudo systemctl status mcp-server
```

### Load Balancing and High Availability

For production deployments:

```nginx
# /etc/nginx/sites-available/mcp-server
upstream mcp_backend {
    server 127.0.0.1:8080;
    server 127.0.0.1:8081;  # Additional instances
}

server {
    listen 443 ssl;
    server_name mcp.yourdomain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /sse {
        proxy_pass http://mcp_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }
    
    location / {
        proxy_pass http://mcp_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Monitoring and Logging

```python
# Add to your MCP server
import psutil
import logging.handlers

# Set up rotating logs
handler = logging.handlers.RotatingFileHandler(
    '/var/log/mcp-server/server.log',
    maxBytes=10485760,  # 10MB
    backupCount=5
)

# Health metrics endpoint
def do_GET(self):
    if self.path == "/metrics":
        metrics = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "active_connections": len(active_connections),
            "uptime": time.time() - start_time
        }
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(metrics).encode())
```

### Backup and Recovery

```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/mcp-server"

# Backup configuration
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" /opt/mcp-server/*.json /opt/mcp-server/.env

# Backup logs (last 7 days)
find /var/log/mcp-server -name "*.log*" -mtime -7 -exec tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" {} +

# Clean old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
```

---

## Conclusion

This guide provides comprehensive solutions for running MCP servers over SSH connections. The HTTP/SSE with SSH tunneling approach is recommended for most use cases as it:

- Provides proper security through token authentication
- Maintains compatibility with MCP specification  
- Allows for flexible deployment options
- Supports production-ready configurations

Choose the method that best fits your security requirements and deployment constraints. For development and testing, simple bearer tokens are sufficient. For production deployments, implement full OAuth 2.1 compliance with proper token management and monitoring.

Remember to always prioritize security by using HTTPS in production, implementing proper token validation, and following OAuth best practices for token storage and handling.