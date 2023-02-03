import sys

with open(sys.argv[1], 'r') as f:
    lines = f.read().splitlines()

declared_tags = set()

for line in lines:
    if '#tag' not in line:
        continue
    for word in line.split():
        if word.startswith('#'):
            declared_tags.add(word)

undeclared_tags = set()

for line in lines:
    for word in line.split():
        if not word.startswith('#'):
            continue
        if word not in declared_tags:
            undeclared_tags.add(word)

for undeclared_tag in sorted(list(undeclared_tags)):
    print(undeclared_tag)
