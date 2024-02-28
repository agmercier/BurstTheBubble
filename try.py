import random

start = 10
end = 20
not_arr = [10, 12, 13, 14, 16, 17, 18]

ans = list(set(range(start, end)).difference(set(not_arr)))

skip_rows = (
    list(range(1, start))
    + random.sample(ans, (end - start) - 1 - len(not_arr))
    + not_arr
    + list(range(end, 25))
)
print(ans)

# [19, 11, 15]
