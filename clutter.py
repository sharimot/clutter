from flask import Flask, render_template, request
from html import escape
from urllib.parse import quote
import os

assert 'CLUTTER' in os.environ
assert os.path.exists(os.environ['CLUTTER'])
path = os.environ['CLUTTER']

def read():
    with open(path, 'r') as f:
        lines = [None] + f.read().splitlines()
    return lines

def write(lines):
    with open(path, 'w') as f:
        f.write('\n'.join(lines[1:]))

app = Flask(__name__)

@app.route('/')
def index():
    if request.args.get('entry'):
        write(read() + [request.args.get('entry')])
    q = request.args.get('q').strip() if request.args.get('q') else ''
    until, words, lines = request.args.get('until'), q.split(), read()
    limit = int(until) + 1 if until and until.isdigit() else len(lines)
    desc = reversed(range(1, limit))
    ok = lambda w, l: w[1:] not in l if w[0] == '-' else w in l
    fine = lambda words, L: all(ok(W.lower(), L.lower()) for W in words)
    items = [(i, lines[i]) for i in desc if fine(words, lines[i])]
    return render_template('index.html', items=items[:1000], q=q)

@app.route('/update', methods=['POST'])
def update():
    item_id, content = request.data.decode('utf-8').split(' ', 1)
    items = read()
    items[int(item_id)] = content
    write(items)
    return 'ok'

@app.template_filter('link')
def link(item):
    parts = []
    for word in item[1].split(' '):
        if word.startswith('http'):
            part = f'<a href="{escape(word)}">{escape(word)}</a>'
        elif word.startswith('#'):
            part = f'<a href="/?q={quote(word)}">{escape(word)}</a>'
        else:
            part = escape(word)
        parts.append(part)
    return ' '.join(parts)
