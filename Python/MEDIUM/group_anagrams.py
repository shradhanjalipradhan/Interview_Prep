"""
Question:
Given an array of strings, group anagrams together.

Example:
Input: ["eat","tea","tan","ate","nat","bat"]
Output: [["eat","tea","ate"],["tan","nat"],["bat"]]
"""

from collections import defaultdict

def group_anagrams(strs):
    anagram_map = defaultdict(list)

    for word in strs:
        key = tuple(sorted(word))
        anagram_map[key].append(word)

    return list(anagram_map.values())

# Test
print(group_anagrams(["eat","tea","tan","ate","nat","bat"]))