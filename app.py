"""Browser interface for the original Student Management System.
Each browser receives its own temporary list of student dictionaries.
"""
import json
import os
import secrets
import threading
import time
from http.cookies import SimpleCookie
from pathlib import Path
from wsgiref.simple_server import make_server
import student_logic as sl

ROOT = Path(__file__).resolve().parent / 'static'
SESSIONS = {}
LOCK = threading.RLock()
SESSION_TTL = 3600
MAX_SESSIONS = 500
MAX_RECORDS = 200


def state(records):
    total, average, highest, lowest = sl.show_statistics(records)
    return {'records': records, 'statistics': {'total': total,
            'average': sl.format_cgpa(average), 'highest': sl.format_cgpa(highest),
            'lowest': sl.format_cgpa(lowest)}}


def application(environ, start_response):
    path, method = environ.get('PATH_INFO', '/'), environ['REQUEST_METHOD']
    headers = [('Cache-Control', 'no-store'), ('X-Content-Type-Options', 'nosniff'),
               ('Referrer-Policy', 'no-referrer'), ('X-Frame-Options', 'DENY'),
               ('Content-Security-Policy', "default-src 'self'; style-src 'self'; script-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")]

    def reply(status, data, content_type='application/json; charset=utf-8'):
        raw = data if isinstance(data, bytes) else json.dumps(data).encode('utf-8')
        start_response(status, headers + [('Content-Type', content_type), ('Content-Length', str(len(raw)))])
        return [raw]

    files = {'/': ('index.html', 'text/html; charset=utf-8'),
             '/style.css': ('style.css', 'text/css; charset=utf-8'),
             '/script.js': ('script.js', 'application/javascript; charset=utf-8')}
    if method == 'GET' and path in files:
        name, mime = files[path]
        return reply('200 OK', (ROOT / name).read_bytes(), mime)
    if method == 'GET' and path == '/health':
        return reply('200 OK', {'status': 'ok'})
    if not (path == '/api/state' and method == 'GET' or path == '/api/action' and method == 'POST'):
        return reply('404 Not Found', {'message': 'Not found.'})
    cookie = SimpleCookie()
    try:
        cookie.load(environ.get('HTTP_COOKIE', ''))
    except Exception:
        pass
    sid = cookie['sms_session'].value if 'sms_session' in cookie else ''
    with LOCK:
        now = time.monotonic()
        for key in list(SESSIONS):
            if now - SESSIONS[key]['seen'] > SESSION_TTL:
                del SESSIONS[key]
        if sid not in SESSIONS:
            if len(SESSIONS) >= MAX_SESSIONS:
                del SESSIONS[min(SESSIONS, key=lambda k: SESSIONS[k]['seen'])]
            sid = secrets.token_urlsafe(32)
            SESSIONS[sid] = {'records': [], 'seen': now}
            secure = '; Secure' if os.environ.get('RENDER') or environ.get('wsgi.url_scheme') == 'https' else ''
            headers.append(('Set-Cookie', f'sms_session={sid}; Path=/; HttpOnly; SameSite=Strict{secure}'))
        session = SESSIONS[sid]
        session['seen'] = now
        records = session['records']
        if method == 'GET':
            return reply('200 OK', state(records))
        try:
            if environ.get('CONTENT_TYPE', '').split(';')[0] != 'application/json':
                return reply('415 Unsupported Media Type', {'message': 'JSON required.'})
            length = int(environ.get('CONTENT_LENGTH') or 0)
            if not 0 < length <= 8192:
                raise ValueError('Invalid request size.')
            payload = json.loads(environ['wsgi.input'].read(length))
            if not isinstance(payload, dict):
                raise ValueError('Invalid request.')
            action = payload.get('action')
            values = []
            for field in ('student_id', 'name', 'major', 'cgpa'):
                value = payload.get(field, '')
                if not isinstance(value, str) or len(value) > (30 if field in ('student_id','cgpa') else 100):
                    raise ValueError('Invalid or overly long field.')
                values.append(value)
            student_id, name, major, cgpa = values
            found = None
            if action == 'add':
                if len(records) >= MAX_RECORDS:
                    raise ValueError('Demo record limit reached (200).')
                result = sl.add_student(records, student_id, name, major, cgpa)
                message = f"Student {result['student_id']} added successfully."
            elif action == 'search':
                sl.validate_text(student_id, 'Student ID')
                found = sl.search_student(records, student_id)
                if found is None:
                    raise ValueError(f"Student ID '{student_id.strip()}' was not found.")
                message = f"Student {found['student_id']} found."
            elif action == 'update':
                result = sl.update_student(records, student_id, name, major, cgpa)
                message = f"Student {result['student_id']} updated successfully."
            elif action == 'delete':
                result = sl.delete_student(records, student_id)
                message = f"Student {result['student_id']} deleted successfully."
            elif action == 'samples':
                missing = sum(sl.find_index(records, s['student_id']) == -1 for s in sl.SAMPLE_DATA)
                if len(records) + missing > MAX_RECORDS:
                    raise ValueError('Demo record limit reached (200).')
                added = sl.load_sample_data(records)
                message = f'{added} sample record(s) added.'
            else:
                raise ValueError('Unknown action.')
            return reply('200 OK', {**state(records), 'message': message, 'found': found})
        except (ValueError, UnicodeError, TypeError) as exc:
            return reply('400 Bad Request', {**state(records), 'message': str(exc)})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8000'))
    host = '0.0.0.0' if os.environ.get('PORT') else '127.0.0.1'
    print(f'Student Management System running on http://{host}:{port}', flush=True)
    with make_server(host, port, application) as server:
        server.serve_forever()
