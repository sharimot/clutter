import sys

with open(sys.argv[1], 'r') as f:
    lines = f.read().splitlines()

taglines = [line for line in lines if '#tag' in line]

tags = set()

for line in lines:
    for word in line.split():
        if word.startswith('#'):
            if not any(word in tagline.split() for tagline in taglines):
                tags.add(word)

for tag in sorted(list(tags)):
    print(tag)
