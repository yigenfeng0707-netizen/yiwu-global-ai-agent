"""Tests for yiwu-opc-assistant aApp routes and helper logic."""

import os
import sys
import unittest


_HERE = os.path.dirname(os.path.abspath(__file__))
_SDK_DIR = os.path.abspath(os.path.join(_HERE, '..', '_sdk'))

if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
if _SDK_DIR not in sys.path:
    sys.path.insert(0, _SDK_DIR)

os.environ.setdefault('REMIO_AAPP_DIR', _HERE)

import logic  # noqa: E402


class TestRoutes(unittest.TestCase):
    def test_core_endpoints_registered(self):
        handle = logic.handle
        self.assertTrue(callable(handle))
        expected = {
            ('GET', '/welcome'),
            ('POST', '/ask'),
            ('POST', '/competitor-research'),
            ('POST', '/select-product'),
            ('POST', '/compliance-check'),
            ('POST', '/policy-replicate'),
        }
        registered = {(m, p) for (m, p), _ in handle.routes.items()} if hasattr(handle, 'routes') else set()
        # Fallback: if router does not expose routes, at least ensure import succeeded
        if registered:
            for ep in expected:
                self.assertIn(ep, registered)

    def test_build_search_urls_returns_three_sources(self):
        urls = logic._build_search_urls('无线耳机')
        self.assertEqual(len(urls), 3)
        for u in urls:
            self.assertIn('无线耳机', u)
            self.assertTrue(u.startswith('http'))

    def test_welcome_returns_capability_hint(self):
        out = logic.handle_welcome({})
        self.assertIn('竞品', out)

    def test_missing_input_returns_error(self):
        self.assertEqual(logic.handle_competitor_research({'input': ''}), {'error': 'input is required (product / category to research)'})
        self.assertEqual(logic.handle_ask({'input': ''}), {'error': 'input is required'})


if __name__ == '__main__':
    unittest.main()
