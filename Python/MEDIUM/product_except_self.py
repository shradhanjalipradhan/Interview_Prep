"""
Question:
Return an array output such that output[i] is the product of all elements in nums except nums[i].

Example:
Input: [1,2,3,4]
Output: [24,12,8,6]
"""

def product_except_self(nums):
    n = len(nums)
    left, right, res = [1]*n, [1]*n, [1]*n

    for i in range(1, n):
        left[i] = left[i-1] * nums[i-1]

    for i in range(n-2, -1, -1):
        right[i] = right[i+1] * nums[i+1]

    for i in range(n):
        res[i] = left[i] * right[i]

    return res

# Test
print(product_except_self([1,2,3,4]))