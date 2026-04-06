"""
Question:
Given an array of integers nums and an integer target,
return indices of the two numbers such that they add up to target.

Example:
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
"""

def two_sum(num,target):
    seen = {}
    for i, num in enumerate(num):
        if target - num in seen:
            return [seen[target - num], i]
        seen[num] = i

#test
print(two_sum([2,7,11,15], 9))