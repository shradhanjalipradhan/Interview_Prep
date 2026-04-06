"""
Question:
Given a sorted array, find indices of two numbers that sum up to a target.

Example:
Input: numbers = [2, 7, 11, 15], target = 9
Output: [0, 1]
"""

def two_sum_sorted(numbers, target):
    left, right = 0, len(numbers) - 1

    while left < right:
        total = numbers[left] + numbers[right]
        if total == target:
            return [left, right]
        elif total < target:
            left += 1
        else:
            right -= 1

# Test
print(two_sum_sorted([2,7,11,15], 9))