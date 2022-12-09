from flask import Flask, render_template, request
from html import escape
import datetime
import os
import re

assert 'CLUTTER' in os.environ
assert os.path.exists(os.environ['CLUTTER'])
path = os.environ['CLUTTER']

def read():
    with open(path, 'r') as f:
        lines = f.read().splitlines()
    return lines

def write(lines):
    with open(path, 'w') as f:
        while lines[0] == '':
            lines = lines[1:]
        f.write('\n'.join(lines) + '\n')

app = Flask(__name__)

@app.route('/')
def index():
    if request.args.get('entry'):
        header = datetime.datetime.now().strftime('%Y%m%d%H%M%S ')
        write([header + request.args.get('entry')] + read())
    lines, items, words = read(), [], []
    q, n = request.args.get('q') if request.args.get('q') else '', len(lines)
    for word in q.split():
        prefix = word[0] if word[0] in {'A', 'D', 'N'} and len(word) > 1 else None
        words.append((prefix, word[int(bool(prefix)):].replace('[space]', ' ').lower()))
    for i, line in enumerate(lines):
        line_ = line.lower()
        if all((word[0] != 'N') == (word[1] in line_) for word in words):
            items.append((n - i, line))
    sort = [word for word in words if word[0] in {'A', 'D'}]
    if sort:
        reverse, splitter = sort[0][0] == 'D', sort[0][1]
        key = lambda item: item[1].lower().split(splitter, 1)[1]
        items = sorted(items, key=key, reverse=reverse)
    count = '&nbsp;' * (14 - len(str(len(items)))) + str(len(items)) + '&nbsp;'
    return render_template('index.html', items=items, q=q, count=count)

@app.route('/add', methods=['POST'])
def add():
    header = datetime.datetime.now().strftime('%Y%m%d%H%M%S ')
    write([header + request.data.decode('utf-8')] + read())
    return 'ok'

@app.route('/update', methods=['POST'])
def update():
    item_id, original, content = request.data.decode('utf-8').split('\n')
    items = read()
    index = len(items) - int(item_id)
    if items[index] != original:
        return 'no'
    items[index] = content
    write(items)
    return 'ok'

@app.template_filter('link')
def link(item):
    parts = []
    tag = {'#': 'hash', '$': 'dollar', '^': 'caret'}
    for word in item[1].split(' '):
        if word.startswith('http'):
            parts.append(f'<a href="{escape(word)}">{escape(word)}</a>')
        elif word and word[0] in tag:
            parts.append(f'<span class="{tag[word[0]]}">{escape(word)}</span>')
        else:
            parts.append(escape(word))
    line = ' '.join(parts)
    if re.match(r'\d{14}', line):
        line = f'{line[:4]}<a href="/?q={line[:8]}">{line[4:8]}</a>{line[8:]}'
    return line
