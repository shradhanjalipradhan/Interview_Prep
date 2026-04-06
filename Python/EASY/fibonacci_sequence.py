"""
Question:
Generate the first n Fibonacci numbers.

Example:
Input: n = 5
Output: [0, 1, 1, 2, 3]
"""

def fibonacci(n):
    fib = [0, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib[:n]

# Test
print(fibonacci(5))