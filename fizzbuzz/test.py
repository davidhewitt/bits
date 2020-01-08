import unittest

from fizzbuzz import fuzz, is_fibonacci, is_perfect_square


class TestFuzz(unittest.TestCase):

    def test_multiple_threes(self):
        for i in range(0, 1000):
            # Don't bother with product of both here, or flamingoes
            if i % 5 == 0 or is_fibonacci(i * 3):
                continue

            # i * 3 is always a multiple of 3
            self.assertEqual(fuzz(i * 3), "Fizz")

    def test_multiple_fives(self):
        for i in range(0, 1000):
            # Don't bother with product of both here, or flamingoes
            if i % 3 == 0 or is_fibonacci(i * 5):
                continue

            # i * 5 is always a multiple of 5
            self.assertEqual(fuzz(i * 5), "Buzz")

    def test_multiple_boths(self):
        for i in range(0, 1000):
            # Don't bother with flamingoes here
            if is_fibonacci(i * 3 * 5):
                continue

            # Iterate up the sequence of 3 * 5
            self.assertEqual(fuzz(i * 3 * 5), "FizzBuzz")

    def test_flamingoes(self):
        for i in range(0, 1000):
            # Only fibonacci numbers are flamingoes
            if not is_fibonacci(i):
                self.assertNotIn(fuzz(i), "Flamingo")

            # 3 and 5 fibonacci numbers are Pink Flamingoes
            elif i % 3 == 0 and i % 5 == 0:
                self.assertEqual(fuzz(i), "Pink Flamingo")

            else:
                self.assertEqual(fuzz(i), "Flamingo")


class TestIsFibonacci(unittest.TestCase):

    def test_known_numbers(self):
        """Test some hand picked numbers"""
        self.assertEqual(is_fibonacci(0), True)
        self.assertEqual(is_fibonacci(1), True)
        self.assertEqual(is_fibonacci(2), True)
        self.assertEqual(is_fibonacci(3), True)
        self.assertEqual(is_fibonacci(4), False)
        self.assertEqual(is_fibonacci(5), True)

        self.assertEqual(is_fibonacci(10), False)
        self.assertEqual(is_fibonacci(20), False)
        self.assertEqual(is_fibonacci(21), True)
        self.assertEqual(is_fibonacci(30), False)
        self.assertEqual(is_fibonacci(34), True)
        self.assertEqual(is_fibonacci(55), True)

    def test_fibonacci_sequence(self):
        """Generating the fibonacci sequence < 1000 - all should be True"""

        last = 0
        current = 1

        while current < 1000:
            # Perform update in one step
            last, current = current, last + current
            self.assertTrue(is_fibonacci(current))


class TestPerfectSquare(unittest.TestCase):

    def test_known_numbers(self):
        """Test some hand picked numbers"""
        self.assertEqual(is_perfect_square(1), True)
        self.assertEqual(is_perfect_square(2), False)
        self.assertEqual(is_perfect_square(3), False)
        self.assertEqual(is_perfect_square(4), True)

        self.assertEqual(is_perfect_square(9), True)
        self.assertEqual(is_perfect_square(10), False)

    def test_sequence(self):
        """Generating the first 20 perfect squares - all should be True"""

        for i in range(20):
            self.assertTrue(is_perfect_square(i * i))


if __name__ == "__main__":
    unittest.main()
