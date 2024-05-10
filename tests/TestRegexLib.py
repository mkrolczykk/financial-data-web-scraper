"""
Tests for regex_lib.py
"""
import unittest
from dependencies.regex_lib import match


class TestRegexLib(unittest.TestCase):
    def test_literal_matching(self):
        self.assertTrue(match("abc", "abcdef")[0])
        self.assertTrue(match("abc", "xyzabc")[0])
        self.assertTrue(match("abc", "123abc456")[0])
        self.assertFalse(match("abc", "xbyzc")[0])

    def test_set_matching(self):
        self.assertTrue(match("[a-z]", "m")[0])
        self.assertFalse(match("[a-z]", "5")[0])
        self.assertFalse(match("[a-z]", "!")[0])

    def test_star_operator(self):
        self.assertTrue(match("a*b", "b")[0])
        self.assertTrue(match("a*b", "aaab")[0])
        self.assertFalse(match("a*b", "c")[0])

    def test_plus_operator(self):
        self.assertFalse(match("a+b", "b")[0])
        self.assertTrue(match("a+b", "aaab")[0])
        self.assertFalse(match("a+b", "c")[0])

    def test_question_operator(self):
        self.assertTrue(match("a?b", "b")[0])
        self.assertTrue(match("a?b", "ab")[0])

    def test_alternate(self):
        self.assertTrue(match("(abc|def)", "abc")[0])
        self.assertTrue(match("(abc|def)", "def")[0])
        self.assertFalse(match("(abc|def)", "xyz")[0])

    def test_start_and_end(self):
        self.assertTrue(match("^abc", "abcdef")[0])
        self.assertTrue(match("def$", "abcdef")[0])
        self.assertFalse(match("^def$", "abcdef")[0])

    def test_escape_sequence(self):
        self.assertTrue(match("\\d+", "123")[0])
        self.assertFalse(match("\\d+", "abc")[0])

    def test_dot_operator(self):
        self.assertTrue(match("a.c", "abc")[0])
        self.assertTrue(match("a.c", "axc")[0])
        self.assertFalse(match("a.c", "ac")[0])

    def test_matching_in_middle(self):
        self.assertTrue(match("abc", "xyzabcdefxyz")[0])
        self.assertFalse(match("abc", "xyzxyz")[0])

    def test_link_domain_matching(self):
        expr = '^http://(\\a|\\d)+.(com|net|org)'
        string = 'http://testpage123computer.com/pl/test'
        [matched, match_pos, match_length] = match(expr, string)
        self.assertTrue(matched)
        if matched:
            matched_string = string[match_pos:match_pos + match_length]
            self.assertEqual(matched_string, 'http://testpage123computer.com')

    def test_matching_without_subdomain(self):
        expr = '^http://(\\a|\\d)+.(com|net|org)'
        string = 'http://computer.com'
        [matched, match_pos, match_length] = match(expr, string)
        self.assertTrue(matched)
        if matched:
            matched_string = string[match_pos:match_pos + match_length]
            self.assertEqual(matched_string, 'http://computer.com')

    def test_matching_with_https(self):
        expr = '^https://(\\a|\\d)+.(com|net|org)'
        string = 'https://secure123site.org'
        [matched, match_pos, match_length] = match(expr, string)
        self.assertTrue(matched)
        if matched:
            matched_string = string[match_pos:match_pos + match_length]
            self.assertEqual(matched_string, 'https://secure123site.org')

    def test_no_matching(self):
        expr = '^http://(\\a|\\d)+.(com|net|org)'
        string = 'ftp://example.org'
        [matched, _, _] = match(expr, string)
        self.assertFalse(matched)


if __name__ == '__main__':
    unittest.main()
