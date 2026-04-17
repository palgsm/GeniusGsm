#!/usr/bin/env python3
import sys

# Lightweight parser for Django-like tags
PATH = '/root/GeniusGsm/src/templates/iplookup/lookup.html'
START_TAGS = {'if', 'for', 'with', 'block'}
END_MAP = {'endif': 'if', 'endfor': 'for', 'endwith': 'with', 'endblock': 'block'}

stack = []
errors = []

with open(PATH, 'r', encoding='utf-8') as f:
    for lineno, line in enumerate(f, 1):
        pos = 0
        while True:
            idx = line.find('{%', pos)
            if idx == -1:
                break
            end = line.find('%}', idx+2)
            if end == -1:
                break
            inner = line[idx+2:end].strip()
            parts = inner.split()
            tag = parts[0] if parts else None
            if not tag:
                pos = end+2
                continue
            if tag in START_TAGS:
                stack.append((tag, lineno))
            elif tag in ('else', 'elif'):
                if not stack or stack[-1][0] != 'if':
                    errors.append((lineno, f"'{tag}' without matching 'if'"))
            elif tag in END_MAP:
                expected = END_MAP[tag]
                if not stack:
                    errors.append((lineno, f"'{tag}' has no opening tag"))
                else:
                    top, top_ln = stack.pop()
                    if top != expected:
                        errors.append((lineno, f"Mismatched end tag '{tag}' (expected to close '{top}' opened at line {top_ln})"))
            pos = end+2

if stack:
    for t, ln in stack:
        errors.append((ln, f"Unclosed tag '{t}' opened at line {ln}"))

if not errors:
    print('No nesting errors detected')
    sys.exit(0)

for e in errors:
    print(f"Line {e[0]}: {e[1]}")

sys.exit(2)
