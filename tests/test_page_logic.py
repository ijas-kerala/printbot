import unittest
from core.printing.page_utils import parse_page_range

class TestPageUtils(unittest.TestCase):
    
    def test_basic_single_pages(self):
        # "1,3,5" -> [0, 2, 4]
        res = parse_page_range("1,3,5", 10)
        self.assertEqual(res, [0, 2, 4])

    def test_basic_range(self):
        # "1-3" -> [0, 1, 2]
        res = parse_page_range("1-3", 10)
        self.assertEqual(res, [0, 1, 2])
        
    def test_mixed_input(self):
        # "1, 3-5, 8" -> [0, 2, 3, 4, 7]
        res = parse_page_range("1, 3-5, 8", 10)
        self.assertEqual(res, [0, 2, 3, 4, 7])

    def test_out_of_bounds(self):
        # "1, 15" with 10 pages -> [0]
        res = parse_page_range("1, 15", 10)
        self.assertEqual(res, [0])
        
    def test_range_clipping(self):
        # "8-12" with 10 pages -> [7, 8, 9] (Pages 8, 9, 10)
        res = parse_page_range("8-12", 10)
        self.assertEqual(res, [7, 8, 9])
        
    def test_invalid_syntax_ignored(self):
        # "1, abc, 5" -> [0, 4]
        res = parse_page_range("1, abc, 5", 10)
        self.assertEqual(res, [0, 4])
        
    def test_empty_or_all(self):
        self.assertEqual(parse_page_range("", 5), [0, 1, 2, 3, 4])
        self.assertEqual(parse_page_range("all", 5), [0, 1, 2, 3, 4])
        self.assertEqual(parse_page_range("ALL", 5), [0, 1, 2, 3, 4])

    def test_overlap_and_ordering(self):
        # "3-5, 4" -> [2, 3, 4] (Unique, sorted)
        res = parse_page_range("3-5, 4", 10)
        self.assertEqual(res, [2, 3, 4])

    def test_single_page_doc(self):
        res = parse_page_range("1", 1)
        self.assertEqual(res, [0])
        
    def test_reverse_input(self):
        # "5-1" -> "1-5" -> [0,1,2,3,4]
        res = parse_page_range("5-1", 10)
        self.assertEqual(res, [0, 1, 2, 3, 4])

if __name__ == '__main__':
    unittest.main()
