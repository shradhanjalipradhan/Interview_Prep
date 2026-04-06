"""
Question:
Count the number of vowels in a string.

Example:
Input: "hello world"
Output: 3
"""

def count_vowels(s):
    vowels = "aeiouAEIOU"
    return sum(1 for char in s if char in vowels)

# Test
print(count_vowels("hello world"))