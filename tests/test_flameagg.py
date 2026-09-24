import json
import threading
import unittest
import urllib.error
import urllib.request

from flameagg import FlameAgg
from server import serve

class TestFlameAgg(unittest.TestCase):
    def test_add_counts_samples(self):
        agg = FlameAgg()
        self.assertEqual(agg.add(["main"], 1)["samples"], 1)

    def test_fold_has_top_frame(self):
        agg = FlameAgg()
        agg.add(["main", "parse"], 1)
        agg.add(["main", "io"], 1)
        self.assertEqual(agg.fold()["main"], 2)

    def test_stats_shape(self):
        self.assertIn("truncated", FlameAgg().stats())

    def test_fold_empty(self):
        self.assertEqual(FlameAgg().fold(), {})

    def test_http_add_fold(self):
        server = serve(0)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = "http://127.0.0.1:%d" % server.server_port
        urllib.request.urlopen(base + "/add", data=b'{"stack": ["main"], "weight": 2}', timeout=5).read()
        with urllib.request.urlopen(base + "/", timeout=5) as response:
            self.assertEqual(json.loads(response.read())["tops"], {"main": 2})
        server.shutdown()
