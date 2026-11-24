"""Ejemplo minimo. Requiere server.py iniciado en otra terminal.
Ejecutar: python3 -m unittest -v test_smoke.py
"""
import unittest
import json
from urllib.request import Request, urlopen

def req(method,path):
    r = Request("http://127.0.0.1:8765"+path,method=method)
    with urlopen(r,timeout=3) as x:
        return x.status, json.load(x)

class SmokeTest(unittest.TestCase):
    def setUp(self):
        req("DELETE","/_test/reset")

    def test_health(self):
        status, data = req("GET","/health")
        self.assertEqual(status,200)
        self.assertEqual(data["status"],"ok")

if __name__ == "__main__":
    unittest.main()
