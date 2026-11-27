"""Integration checks for the web service (standard library only)."""
import json
import threading
import unittest
from http.cookiejar import CookieJar
from urllib.request import build_opener, HTTPCookieProcessor, Request
from urllib.error import HTTPError
from wsgiref.simple_server import make_server, WSGIRequestHandler
from app import application

class QuietHandler(WSGIRequestHandler):
    def log_message(self, *_): pass

class WebTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = make_server('127.0.0.1', 0, application, handler_class=QuietHandler)
        cls.url = 'http://127.0.0.1:%d' % cls.server.server_port
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join()

    def setUp(self):
        self.client = build_opener(HTTPCookieProcessor(CookieJar()))
        self.get('/api/state')

    def get(self, path):
        with self.client.open(self.url + path) as response:
            return response.status, response.read()

    def act(self, action, **fields):
        req = Request(self.url + '/api/action', data=json.dumps({'action': action, **fields}).encode(), headers={'Content-Type':'application/json'})
        try: response = self.client.open(req)
        except HTTPError as exc: response = exc
        with response: return response.status, json.load(response)

    def add(self, **overrides):
        fields = dict(student_id='S106', name='Alex Morgan', major='Software Engineering', cgpa='3.80')
        fields.update(overrides)
        return self.act('add', **fields)

    def test_static_and_health(self):
        for path, text in [('/',b'Student Management System'),('/style.css',b'.layout'),('/script.js',b'/api/action'),('/health',b'ok')]:
            code, body = self.get(path); self.assertEqual(code,200); self.assertIn(text,body)
    def test_empty(self):
        self.assertEqual(json.loads(self.get('/api/state')[1])['records'],[])
    def test_samples_and_statistics(self):
        code, result = self.act('samples'); self.assertEqual(code,200)
        self.assertEqual(result['statistics'],dict(total=5,average='3.56',highest='3.90',lowest='3.10'))
        self.assertEqual(self.act('samples')[1]['statistics']['total'],5)
    def test_add(self):
        code,result=self.add(); self.assertEqual(code,200);self.assertEqual(result['records'][0]['cgpa'],3.8)
    def test_duplicate(self):
        self.add();code,result=self.add(student_id='s106');self.assertEqual(code,400);self.assertEqual(len(result['records']),1)
    def test_invalid_cgpa(self):
        for value in ('4.5','-1','nan','abc',''):
            code,result=self.add(cgpa=value);self.assertEqual(code,400);self.assertEqual(result['records'],[])
    def test_empty_fields(self):
        for key in ('student_id','name','major'):
            self.assertEqual(self.add(**{key:' '})[0],400)
    def test_search(self):
        self.act('samples'); code,result=self.act('search',student_id='s103');self.assertEqual(code,200);self.assertEqual(result['found']['name'],'Maria Lopez')
        self.assertEqual(self.act('search',student_id='S999')[0],400)
    def test_update(self):
        self.act('samples');code,result=self.act('update',student_id='S104',major='Software Engineering',cgpa='3.20');self.assertEqual(code,200)
        self.assertEqual(result['statistics']['average'],'3.58');self.assertEqual(result['records'][3]['name'],'John Carter')
        code,result=self.act('update',student_id='S104',name='Invalid update',cgpa='8');self.assertEqual(code,400);self.assertEqual(result['records'][3]['name'],'John Carter')
    def test_delete(self):
        self.act('samples');code,result=self.act('delete',student_id='S102');self.assertEqual(code,200);self.assertEqual(len(result['records']),4)
        self.assertEqual(self.act('delete',student_id='S102')[0],400)
    def test_session_isolation(self):
        self.add();self.assertEqual(len(json.loads(self.get('/api/state')[1])['records']),1)
        other=build_opener(HTTPCookieProcessor(CookieJar()));self.assertEqual(json.load(other.open(self.url+'/api/state'))['records'],[])
    def test_unknown_action(self):
        self.assertEqual(self.act('invalid')[0],400)

if __name__ == '__main__': unittest.main(verbosity=2)
