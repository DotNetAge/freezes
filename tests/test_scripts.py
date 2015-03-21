import unittest
import re
import json

from flask import current_app
from helper import init_test_case
from mocks import m
from freezes.scripts import SkeletonGenerator


class ScriptTestCase(unittest.TestCase):
    def setUp(self):
        init_test_case(self)

    def tearDown(self):
        pass

    def test_new_site(self):
        skeleton = SkeletonGenerator(self.app)
        skeleton.run()