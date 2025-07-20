def binary_search(arr, target):
    """
    Performs binary search on a sorted array.
    Returns the index of target if found, -1 otherwise.
    """
    left = 0
    right = len(arr) - 1
    
    while left <= right:
        # Find the middle point
        mid = (left + right) // 2
        
        # Check if target is at mid
        if arr[mid] == target:
            return mid
        
        # If target is smaller, search left half
        elif arr[mid] > target:
            right = mid - 1
        
        # If target is larger, search right half
        else:
            left = mid + 1
    
    return -1  # Target not found

# Test the binary search function
sorted_numbers = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
target = 7

result = binary_search(sorted_numbers, target)

if result != -1:
    print(f"Target {target} found at index {result}")
else:
    print(f"Target {target} not found in the array")

# Additional test cases
test_cases = [
    (sorted_numbers, 1),   # First element
    (sorted_numbers, 19),  # Last element
    (sorted_numbers, 10),  # Element not in array
    (sorted_numbers, 13),  # Middle element
]

print("\nRunning test cases:")
for arr, target in test_cases:
    result = binary_search(arr, target)
    status = "Found" if result != -1 else "Not found"
    print(f"Target {target}: {status} at index {result if result != -1 else 'N/A'}") 