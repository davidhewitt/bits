"""FizzBuzz with a twist

Write a program that prints the numbers from 0 to 100. But for multiples of
three print “Fizz” instead of the number and for multiples of five prints
“Buzz”. For numbers which are multiples of both three and five print
“FizzBuzz”. Then extend the program to say “Flamingo” when a number is a
member of the Fibonacci sequence, and “Pink Flamingo” when it is a multiple
of 3 and 5 and a member of the Fibonacci sequence.

Hint: A number is Fibonacci if and only if one or both of (5*n2 + 4) or
(5*n2 – 4) is a perfect square (i.e. A number made by squaring a whole number).
"""

import math


def is_perfect_square(x: int) -> bool:
    """Check if a number is a perfect square (square of an integer)"""
    # Not possible for negative numbers to be square of an integer
    if x < 0:
        return False

    root = math.sqrt(x)

    # This will only be true if the root is integer
    return int(root) == root


def is_fibonacci(x: int) -> bool:
    """Check if a number is a Fibonacci number"""
    x2 = x * x
    return is_perfect_square((5 * x2) - 4) or is_perfect_square((5 * x2) + 4)


def fuzz(x: int) -> str:
    """The fizzbuzz main function.

    Returns:
        - "Flamingo" if the number is a Fibonacci number
        - "Fizz" if the integer is a multiple of 3
        - "Buzz" if the integer is a multiple of 5
        - "FizzBuzz" if it is a multiple of both
        - "Pink Flamingo" if it is a multiple of both and Fibonacci
        - Otherwise, the string representation of the integer
    """
    is_m3 = x % 3 == 0
    is_m5 = x % 5 == 0
    is_flamingo = is_fibonacci(x)

    if is_flamingo:
        if is_m3 and is_m5:
            return "Pink Flamingo"
        else:
            return "Flamingo"

    elif is_m3 and is_m5:
        return "FizzBuzz"

    elif is_m5:
        return "Buzz"

    elif is_m3:
        return "Fizz"

    return str(x)


def main():
    for i in range(101):
        print(fuzz(i))

if __name__ == "__main__":
    main()
