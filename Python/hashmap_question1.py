#Statement: Given an array of integers nums and an integer k, determine the total number of subarrays whose sum is exactly equal to k.

def subarraySum(nums, k):
    prefixSumCount = {0: 1}
    currentSum = 0
    result = 0
    
    for num in nums:
        currentSum += num
        complement = currentSum - k
        if complement in prefixSumCount:
            result += prefixSumCount[complement]
        prefixSumCount[currentSum] = prefixSumCount.get(currentSum, 0) + 1
    
    return result

def main():
    testCases = [
        ([3, 4, 7, 2, -3, 1, 4, 2], 7),
        ([1, -1, 0], 0),
        ([0, 0, 0, 0], 0),
        ([-1, -1, 1], 0),
        ([5, 3, -2, 4, -1, 2, -3, 1], 5),
    ]
    
    for i, (nums, k) in enumerate(testCases, 1):
        result = subarraySum(nums, k)
        print(f"{i}.\tInput array: {nums}")
        print(f"\tTarget: {k}")
        print(f"\tResult: {result}")
        print("-" * 100)

if __name__ == "__main__":
    main()
