"""FRAME 초안 미리보기 전용 서버 — 저장소 루트를 서빙하고 「/」는 미리보기로 보낸다."""
import http.server, functools, pathlib, socketserver
R = pathlib.Path(__file__).resolve().parents[3]
class H(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ('/', '/index.html'):
            self.send_response(302); self.send_header('Location', '/tmp/frame/view/live_deck.html'); self.end_headers(); return
        return super().do_GET()
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store'); super().end_headers()
    def log_message(self, *a): pass
socketserver.ThreadingTCPServer.allow_reuse_address = True
with socketserver.ThreadingTCPServer(('127.0.0.1', 8810), functools.partial(H, directory=str(R))) as s:
    s.serve_forever()
