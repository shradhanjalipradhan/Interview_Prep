"""
Question:
Find the maximum and minimum value in a list.

Example:
Input: [3, 1, 7, 0, 5]
Output: Max = 7, Min = 0
"""

def find_max_min(lst):
    return max(lst), min(lst)

# Test
print(find_max_min([3, 1, 7, 0, 5]))