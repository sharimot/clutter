from flask import Flask, render_template, request
from html import escape
from urllib.parse import quote
import datetime
import os

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
        header = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S ')
        write([header + request.args.get('entry')] + read())
    q = request.args.get('q') if request.args.get('q') else ''
    lines, items, sort = read(), [], None
    n = len(lines)
    for i, line in enumerate(lines):
        line_ = line.lower()
        for phrase in q.split('  '):
            for word in phrase.split(' '):
                if len(word) == 0:
                    continue
                if not sort and word[0] in ['A', 'D']:
                    sort = word
                prefixed = word[0] in ['N', 'A', 'D']
                word_ = word[int(prefixed):].replace('[space]', ' ').lower()
                if (word[0] == 'N') == (word_ in line_):
                    break
            else:
                items.append((n - i, line))
                break
    if sort and '  ' not in q:
        if len(sort) > 1:
            key = lambda item: item[1].lower().split(sort[1:].lower(), 1)[1]
        else:
            key = lambda item: item[1]
        items = sorted(items, key=key, reverse=(sort[0] == 'D'))
    return render_template('index.html', items=items, q=q)

@app.route('/add', methods=['POST'])
def add():
    header = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S ')
    write([header + request.data.decode('utf-8')] + read())
    return 'ok'

@app.route('/update', methods=['POST'])
def update():
    item_id, content = request.data.decode('utf-8').split(' ', 1)
    items = read()
    items[len(items) - int(item_id)] = content
    write(items)
    return 'ok'

@app.template_filter('link')
def link(item):
    parts = []
    for word in item[1].split(' '):
        if word.startswith('http'):
            part = f'<a href="{escape(word)}">{escape(word)}</a>'
        elif word.startswith('#'):
            part = f'<span class="tag">{escape(word)}</span>'
        else:
            part = escape(word)
        parts.append(part)
    return ' '.join(parts)
