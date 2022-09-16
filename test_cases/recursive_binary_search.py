


def binary_search(arr, search, left=0, right=None):

    if right is None:
        right = len(arr) - 1
    mid = (left + right) // 2

    
    if arr[mid] == search:
        return mid
    elif left >= right:
        return -1
    elif arr[mid] > search:
        return binary_search(arr, search, left, mid-1)
    else:
        return binary_search(arr, search, mid+1, right)


f_middle = binary_search([1,2,3,4], 2)
nf_middle = binary_search([1,2,3,4], 2.5)
start = binary_search([1,2,3,4], 1)
end = binary_search([1,2,3,4], 4)
past_end = binary_search([1,2,3,4], 7)

print(f_middle, nf_middle, start, end, past_end)
