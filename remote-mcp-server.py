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