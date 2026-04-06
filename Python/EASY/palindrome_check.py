"""
Question:
Check if a string is a palindrome.

Example:
Input: "racecar"
Output: True
"""

def is_palindrome(s):
    return s == s[::-1]

# Test
print(is_palindrome("racecar"))
print(is_palindrome("python"))