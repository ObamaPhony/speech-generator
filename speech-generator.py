#!/usr/bin/env python3
# usage: $0 TOPIC [TOPIC...] NUMBER
#
import sys, json, random, re

# amount of nouns replaced
REPLACEMENT = 0.2
# chance of choosing an unrelated topic word
UNPREDICTABILITY = 0.2
# chance of joining two sentences with a connective
JOINABILITY = 0.4
# connectives
CONNECTIVES = ("and", "but", "so")

def speechiterator(analysis):
    for speech in analysis:
        for paragraph in speech[1:-1]:
            for sentence in paragraph:
                yield sentence

# replace the nth occurence of needle in haystack
def replace(haystack, needle, replacement, n):
    escaped = re.escape(needle)
    if n > 1:
        regex = r'^((.*?\b%s\b.*?){%d})\b%s\b' % (escaped, n - 1, escaped)
    else:
        regex = r'^(.*?)\b%s\b' % escaped
    return re.sub(regex, r'\1%s' % replacement, haystack)

# slice the sliceable into chunks of size size
def chunks(sliceable, size):
    return [sliceable[i:i + size] for i in range(0, len(sliceable), size)]

# read analysis from stdin 
analysis = json.load(sys.stdin)

# command-line arguments
topics = sys.argv[1:-1]
n = int(sys.argv[-1])

# random sample
sample = dict(zip(topics, chunks(random.sample(list(speechiterator(analysis)), len(topics) * n), n)))

outputs = []
for topic, sentences in sample.items():
    output = ""
    others = topics[:]
    if len(others) > 1:
        others.remove(topic)
    connected = False
    for sentence in sentences:
        nouns = [word[0] for word in sentence["summary"] if word[1].startswith("NN")]
        if len(nouns):
            indexes = random.sample(range(len(nouns)), int(len(nouns) * REPLACEMENT + 0.5))
            line = sentence["sentence"]
            last = -2
            for index in indexes:
                if index - last <= 1:
                    continue
                occurence = nouns[:index].count(nouns[index]) + 1
                replacement = random.choice(others) if random.random() < UNPREDICTABILITY else topic
                line = replace(line, nouns[index], replacement, occurence)

        else:
            line = sentence["sentence"] + ". "

        if random.random() < JOINABILITY:
            # add a connective
            line += " " + random.choice(CONNECTIVES) + ", "
            connected = True
        else:
            line += ". "
            connected = False

        output += line
    outputs.append(output)
print(json.dumps(outputs))
