"""Unit checks for fail-closed platform reads; these are NOT integration tests."""
import copy
import unittest
from unittest.mock import Mock

from team.inkai.model import comparison, twin_definitions, twin_states
from team.inkai.server import Platform


class PlatformContractTests(unittest.TestCase):
    def setUp(self):
        self.platform = object.__new__(Platform)
        self.platform.definitions = twin_definitions()
        self.platform.revision = "test-1"
        states = twin_states(comparison(0, 0))
        self.things = [{"thingId": tid, "attributes": definition["attributes"], "features": {
            "run": {"properties": {"revision": "test-1"}},
            "state": {"properties": states[tid]},
        }} for tid, definition in self.platform.definitions.items()]

    def test_reads_are_from_platform(self):
        self.platform.request = Mock(return_value=self.things)
        response = self.platform.read()
        self.platform.request.assert_called_once()
        self.assertTrue(self.platform.request.call_args.args[0].startswith("/api/2/things?ids="))
        self.assertEqual(len(response["twins"]), 18)

    def test_missing_twins_fail_closed(self):
        self.platform.request = Mock(return_value=self.things[:-1])
        with self.assertRaises(RuntimeError):
            self.platform.read()

    def test_mixed_revisions_fail_closed(self):
        things = copy.deepcopy(self.things)
        things[0]["features"]["run"]["properties"]["revision"] = "old"
        self.platform.request = Mock(return_value=things)
        with self.assertRaises(RuntimeError):
            self.platform.read()
