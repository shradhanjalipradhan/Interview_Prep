import heapq

def kSmallestPairs(list1, list2, k):
    if not list1 or not list2 or k == 0:
        return []
    
    min_heap = []
    res = []
    
    # Step 1: Initialize the heap with the first element of list1 combined with elements of list2
    # We only need min(len(list1), k) elements to start
    for i in range(min(len(list1), k)):
        # Push tuple format: (sum, index_in_list1, index_in_list2)
        heapq.heappush(min_heap, (list1[i] + list2[0], i, 0))
        
    # Step 2: Extract the smallest sum and push the next viable candidate pair
    while min_heap and len(res) < k:
        current_sum, i, j = heapq.heappop(min_heap)
        res.append([list1[i], list2[j]])
        
        # If there is a next element in list2 for the current list1[i], push it
        if j + 1 < len(list2):
            heapq.heappush(min_heap, (list1[i] + list2[j + 1], i, j + 1))
            
    return res
