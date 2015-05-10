import unittest
import re
import json
from flask import current_app
from helper import init_test_case
from mocks import m
from freezes.scripts import SkeletonGenerator,LanguageGenerator


class ScriptTestCase(unittest.TestCase):
    def setUp(self):
        init_test_case(self)

    def tearDown(self):
        pass

    def test_new_site(self):
        skeleton = SkeletonGenerator(self.app)
        skeleton.run()

    def test_lang_command(self):
        from os import path

        lang_cmd = LanguageGenerator(self.app)

        lang_cmd.run(code='de')
        self.assertTrue(path.exists(path.join(self.app.path, 'translations', 'de')))

        lang_cmd.run(action='compile')
        self.assertTrue(
            path.exists(path.join(self.app.path, 'translations', 'de', 'LC_MESSAGES', 'messages.mo')))

        lang_cmd.run(action='update')