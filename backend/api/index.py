"""Vercel Serverless Function Entry Point"""
from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        if self.path == '/api/health' or self.path == '/health':
            response = {"status": "healthy", "app": "勤怠チェック API"}
        else:
            response = {"message": "Kintai Sensei API", "version": "1.0.0"}

        self.wfile.write(json.dumps(response).encode())
        return

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # Simple test response
        response = {"received": True, "path": self.path}
        self.wfile.write(json.dumps(response).encode())
        return
