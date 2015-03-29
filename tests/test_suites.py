#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
import re
import json
from flask import current_app
from helper import init_test_case, create_test_app, clean_builds, clean
from mocks import m
from freezes.scripts import SiteGenerator, SkeletonGenerator


class FreezesTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        test_app = create_test_app()
        siteGen = SkeletonGenerator(test_app)
        siteGen.run()

    def setUp(self):
        init_test_case(self, create_test_app())
        self.site = self.app_context.app.site
        m.prepare().pages().posts()

    def tearDown(self):
        self.app_context.pop()

    @classmethod
    def tearDownClass(cls):
        clean()

    def test_404(self):
        response = self.app.get('/wrong/url')
        self.assertTrue(response.status_code, 404)

    def expect_200(self, rv):
        self.assertTrue(rv.status_code, 200)

    def first_page(self):
        return [p for p in self.site.pages if p.name != 'index'][0]

    def test_recent_layout(self):
        # Test home page for recent layout
        res = self.app.get('/')
        self.expect_200(res)

    def test_page_layout(self):
        # Test about page for page layout
        res = self.app.get('/%s/' % self.first_page().path)
        self.expect_200(res)

    def test_post_layout(self):
        # Test post layout
        res = self.app.get('/%s/' % self.site.posts[0].path)
        self.expect_200(res)

    def test_tags(self):
        res = self.app.get('/tags/')
        self.expect_200(res)

        for tag in self.site.tags:
            res = self.app.get('/tags/%s/' % tag)
            self.expect_200(res)

    def test_archives(self):
        res = self.app.get('/archives/')
        self.expect_200(res)

    def test_in_page_resource(self):
        # res = self.app.get('/%s/' % self.site.posts[0].path)
        # self.expect_200(res)
        pass

    def test_sitemap(self):
        res = self.app.get('/sitemap.xml')
        self.expect_200(res)

    def test_recent_feeds(self):
        res = self.app.get('/feeds/recent.xml')
        self.expect_200(res)

    def test_pages_api(self):
        res = self.app.get('/api/pages/all.json')
        self.expect_200(res)
        self.assertEqual(res.content_type, "application/json")
        post_objects = json.loads(res.data)
        self.assertGreater(len(post_objects['pages']), 0)

        for p in self.site.pages:
            res = self.app.get('/api/pages/%s.json' % p.path)
            self.expect_200(res)
            json_page = json.loads(res.data)
            self.assertEqual(json_page['id'], p._id)
            self.assertEqual(json_page['name'], p.name)
            self.assertEqual(json_page['path'], p.path)
            self.assertEqual(json_page['tags'], p._tags)
            self.assertEqual(json_page['meta']['title'], p.meta['title'])


    def test_posts_api(self):
        res = self.app.get('/api/posts.json')
        self.expect_200(res)
        self.assertEqual(res.content_type, "application/json")
        post_objects = json.loads(res.data)
        self.assertGreater(len(post_objects['posts']), 0)

    def test_localization(self):
        m.page('zh-cn')
        m.page('zh-cn/documents')
        m.page('zh-cn/contacts')
        m.page('zh-cn/about')

        items = self.site.menus('zh-cn')
        self.assertEqual(len(items), 4)

        res = self.app.get('/zh-cn/')
        self.assertTrue(re.search('联系信息',res.data))

    def test_empty_tags(self):
        m.prepare().pages()
        self.assertEqual(self.site.tags, [])

    def test_build(self):
        clean_builds()
        sg = SiteGenerator(self.app_context.app)
        sg.run()


if (__name__ == '__main__'):
    unittest.main()
