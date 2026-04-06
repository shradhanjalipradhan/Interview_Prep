"""
Question:
Find the k most frequent elements in a list.

Example:
Input: nums = [1,1,1,2,2,3], k = 2
Output: [1,2]
"""

from collections import Counter
import heapq

def top_k_frequent(nums, k):
    count = Counter(nums)
    return [item for item, freq in count.most_common(k)]

# Test
print(top_k_frequent([1,1,1,2,2,3], 2))