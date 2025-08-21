import socket, threading
def udp_server(host, port, callback, parser_name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    def loop():
        while True:
            data, addr = sock.recvfrom(8192)
            line = data.decode(errors='ignore').strip()
            callback(parser_name, line)
    threading.Thread(target=loop, daemon=True).start()
def tcp_server(host, port, callback, parser_name):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port)); sock.listen(5)
    def handle(conn):
        with conn:
            buf=b""
            while True:
                chunk = conn.recv(8192)
                if not chunk: break
                buf+=chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n",1)
                    callback(parser_name, line.decode(errors='ignore').strip())
    def loop():
        while True:
            c,_=sock.accept()
            threading.Thread(target=handle, args=(c,), daemon=True).start()
    threading.Thread(target=loop, daemon=True).start()
