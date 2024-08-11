from mctools import PINGClient
from PIL import Image, ImageDraw, ImageFont
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
from urllib.parse import urlparse, parse_qs

def draw_text_image(text):
    width, height = 140, 20
    image = Image.new('RGB', (width, height), color = 'black')

    draw = ImageDraw.Draw(image)

    font = ImageFont.load_default()

    draw.text((0, 0), text, font=font, fill='white')

    image_bytes = BytesIO()
    image.save(image_bytes, "JPEG")

    return image_bytes


def query_server(host, port):
    ping = PINGClient(host, port=port, timeout=3)
    try:
        stats = ping.get_stats()
        players = stats['players']
        max = players['max']
        online = players['online']
        text = f"{online}/{max}"
    except Exception as e:
        text = f"Error: {e}"

    return text


class SimpleRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            print(parsed)
            params = parse_qs(parsed.query)
            ip = params['ip'][0]
        except Exception as e:
            print(e)
            return

        parts = ip.split(':')
        host = parts[0]

        port = 25565
        if len(parts) > 1:
            port = parts[1]

        print("Host: ", host)
        print("Port: ", port)

        text = query_server(host, port)

        with draw_text_image(text) as image_bytes:
            self.send_response(200)
            self.send_header('Content-type', 'image/jpeg')
            self.end_headers()
            self.wfile.write(image_bytes.getvalue())

def run(server_class=HTTPServer, handler_class=SimpleRequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()
