"""Servidor HTTP local (stdlib); adaptador web que delega al caso de uso."""
import json
import mimetypes
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse
from application.use_cases import compare, simulate
from domain.models import Config

STATIC = Path(__file__).parent / 'static'


class Handler(BaseHTTPRequestHandler):
    def json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False, allow_nan=False).encode('utf8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if urlparse(self.path).path != '/api/simulate':
            return self.json({'error': 'Ruta no encontrada'}, 404)
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if size <= 0 or size > 65536:
                raise ValueError('Tamaño de solicitud inválido')
            data = json.loads(self.rfile.read(size))
            cfg = Config(float(data['arrival_rate']), float(data['service_rate']),
                         float(data['duration']), int(data['seed']))
            return self.json(simulate(cfg))
        except (KeyError, ValueError, TypeError) as exc:
            return self.json({'error': str(exc)}, 400)

    def do_GET(self):
        route = urlparse(self.path).path
        if route == '/api/scenarios':
            return self.json(compare())
        if route == '/':
            route = '/index.html'
        path = (STATIC / route.lstrip('/')).resolve()
        if not path.is_relative_to(STATIC.resolve()) or not path.is_file():
            self.send_error(404)
            return
        data = path.read_bytes()
        self.send_response(200)
        self.send_header('Content-Type', mimetypes.guess_type(path.name)[0] or 'application/octet-stream')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def serve(host='127.0.0.1', port=8501):
    print(f'Simulador disponible en http://{host}:{port}')
    ThreadingHTTPServer((host, port), Handler).serve_forever()
