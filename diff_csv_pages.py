import csv
import sys
from difflib import unified_diff


csv.field_size_limit(200000)


with open(sys.argv[1]) as csv_file:
    csv_reader = csv.DictReader(csv_file)
    csv_rows = list(csv_reader)
    
    first = 0
    second = 1

    while True:
        row1 = csv_rows[first]
        row2 = csv_rows[second]

        s1 = [f'{ s }\n' for s in row1["html"].split("\n")]
        s2 = [f'{ s }\n' for s in row2["html"].split("\n")]
        diff =  unified_diff(s1, s2, row1["created_at"], row2["created_at"], lineterm="")

        print("\n\n\n")
        sys.stdout.writelines(diff)

        direction = input()

        if direction == "n":
            first += 1
            second += 1
        elif direction == "p":
            first -= 1
            second -= 1
        