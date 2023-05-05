import random
import string


def generate_random_string(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))


def fake_ed2k(j,n):

    with open(f"ed2k/测试数据_{j}.txt", "w") as f:
        for i in range(n):
            extension = random.choice([".rar", ".mp4", ".avi", ".mkv"])
            filename = generate_random_string(10) + extension
            size = random.randint(1000000, 10000000)
            hash_value = generate_random_string(32)
            f.write(f"ed2k://|file|{filename}|{size}|{hash_value}|/\n")

n=100
for j in range(20):
    fake_ed2k(j,n)
    n+=100



