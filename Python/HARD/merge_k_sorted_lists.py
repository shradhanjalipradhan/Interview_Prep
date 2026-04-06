"""
Question:
Merge k sorted linked lists and return it as one sorted list.

Example:
Input: [[1,4,5],[1,3,4],[2,6]]
Output: [1,1,2,3,4,4,5,6]
"""

import heapq

def merge_k_lists(lists):
    heap = []

    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(heap, (lst[0], i, 0))

    result = []

    while heap:
        val, list_idx, elem_idx = heapq.heappop(heap)
        result.append(val)

        if elem_idx + 1 < len(lists[list_idx]):
            next_tuple = (
                lists[list_idx][elem_idx + 1],
                list_idx,
                elem_idx + 1
            )
            heapq.heappush(heap, next_tuple)

    return result

# Test
print(merge_k_lists([[1,4,5],[1,3,4],[2,6]]))