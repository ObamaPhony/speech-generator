#!/usr/bin/env python3
# usage: $0 TOPIC [TOPIC...] NUMBER
#
import sys, json, random, re, nltk

# amount of nouns replaced
REPLACEMENT = 0.3
# chance of choosing an unrelated topic word
UNPREDICTABILITY = 0.2

def speechlen(analysis):
    total = 0
    for speech in analysis:
        total += len(speech[1:-1])
    return total

def speechiterator(analysis):
    for speech in analysis:
        for paragraph in speech[1:-1]:
            yield paragraph

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
# command-line arguments
topics = sys.argv[1:-1]
n = int(sys.argv[-1])

# read analysis from stdin 
analysis = json.load(sys.stdin)

# dictionary of 'topic: [paragraph, ]'
indexes = random.sample(range(speechlen(analysis)), len(topics) * n)
sample = []
for i, construct in enumerate(speechiterator(analysis)):
    if i in indexes:
        sample.append(construct)
constructs = dict(zip(topics, chunks(sample, n)))

outputs = {}
for topic, paragraphs in constructs.items():
    tag = nltk.pos_tag([topic])[0][1]
    outputs[topic] = []
    for paragraph in paragraphs:
        output = ""
        for sentence in paragraph:
            others = topics[:]
            if len(others) > 1:
                others.remove(topic)
            nouns = [word[0] for word in sentence["summary"] if word[1] == tag]
            # choose which noun indexes to replace
            indexes = random.sample(range(len(nouns)), len(nouns) and 1)
            for i in indexes:
                # which occurence of nouns[i] is this?
                occurence = nouns[:i].count(nouns[i]) + 1
                # which topic to use
                replacement = random.choice(others) if random.random() < UNPREDICTABILITY else topic
                sentence["sentence"] = replace(sentence["sentence"], nouns[i], replacement, occurence)
            output += sentence["sentence"] + ". "
        outputs[topic].append(output)
print(json.dumps(outputs))
