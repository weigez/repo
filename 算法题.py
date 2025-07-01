def twoSum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []  # 根据题目约束，此情况不会发生
print(twoSum(nums = [2, 7, 11, 15],target = 18))