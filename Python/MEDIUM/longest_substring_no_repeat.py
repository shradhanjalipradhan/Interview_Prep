"""
Question:
Given a string, find the length of the longest substring without repeating characters.

Example:
Input: "abcabcbb"
Output: 3
"""

def length_of_longest_substring(s):
    char_set = set()
    left = 0
    max_length = 0

    for right in range(len(s)):
        while s[right] in char_set:
            char_set.remove(s[left])
            left += 1
        char_set.add(s[right])
        max_length = max(max_length, right - left + 1)

    return max_length

# Test
print(length_of_longest_substring("abcabcbb"))