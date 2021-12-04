from flask import Flask, render_template, request
from html import escape
from urllib.parse import quote
import os

if 'CLUTTER' in os.environ:
    path = os.environ['CLUTTER']
    os.makedirs(os.path.dirname(path), exist_ok=True)
else:
    path = 'clutter.txt'

if not os.path.exists(path):
    with open(path, 'w') as f:
        f.write('')

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
    q = request.args.get('q').strip() if request.args.get('q') else ''
    until, words, lines = request.args.get('until'), q.split(), read()
    limit = int(until) + 1 if until and until.isdigit() else len(lines)
    desc = reversed(range(1, limit))
    ok = lambda w, l: w[1:] not in l if w[0] == '-' else w in l
    fine = lambda words, L: all(ok(W.lower(), L.lower()) for W in words)
    items = [(i, lines[i]) for i in desc if fine(words, lines[i])]
    q_param = [f'q={quote(q)}'] if words else []
    until_param = [f'until={items[1000][0]}'] if len(items) > 1000 else []
    url = '/?' + '&'.join(q_param + until_param) if until_param else None
    return render_template('index.html', items=items[:1000], q=q, url=url)

@app.route('/add', methods=['POST'])
def add():
    content = request.data.decode('utf-8')
    write(read() + [content])
    return 'ok'

@app.route('/edit/<int:item_id>')
def edit(item_id):
    items = read()
    if not 0 < item_id < len(items):
        return f'Item {item_id} does not exist.'
    return render_template('edit.html', item_id=item_id, content=items[item_id])

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
