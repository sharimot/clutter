from flask import Flask, render_template, request
from html import escape
from urllib.parse import quote
import datetime
import json
import logging
import os
import re
import sys

logging.getLogger('werkzeug').disabled = True
path = None

def read():
    with open(path, 'r') as f:
        lines = f.read().split('\n')
    return lines, len(lines)

def write(lines):
    with open(path, 'w') as f:
        f.write('\n'.join(lines))

def push(content):
    header = datetime.datetime.now().strftime('%Y%m%d%H%M%S ')
    write([header + content] + read()[0])

def parse(q):
    query = {'q': q, 'units': [], 'sort': None, 'swap': None}
    for word in q.split():
        head, tail = word[0], word[1:]
        convert = lambda word: word.replace('[space]', ' ').lower()
        if head == 'S' and len(word) >= 4 and word[1] == word[-1]:
            chunks = word.split(word[1])
            if len(chunks) != 4:
                continue
            source = chunks[1].replace('[space]', ' ')
            target = chunks[2].replace('[space]', ' ')
            query['swap'] = {'source': source, 'target': target}
            query['units'].append({'match': True, 'word': source.lower()})
        elif len(word) > 1 and head in {'A', 'D'}:
            query['sort'] = {'reverse': head == 'D', 'by': convert(tail)}
            query['units'].append({'match': True, 'word': convert(tail)})
        elif len(word) > 1 and head == 'N':
            query['units'].append({'match': False, 'word': convert(tail)})
        else:
            query['units'].append({'match': True, 'word': convert(word)})
    return query

def process(query):
    (lines, n), data, items = read(), {}, []
    units, sort, swap = query['units'], query['sort'], query['swap']
    for i, line in enumerate(lines):
        if line == '':
            continue
        line_ = line.lower()
        if all(unit['match'] == (unit['word'] in line_) for unit in units):
            items.append({'id': n - i, 'line': line})
    if sort:
        key = lambda item: item['line'].lower().split(sort['by'], 1)[1]
        items = sorted(items, key=key, reverse=sort['reverse'])
    if swap:
        check_case = lambda item: swap['source'] in item['line']
        items = list(filter(check_case, items))
        source, target = swap['source'], swap['target']
        q = quote(target.lower().replace(' ', '[space]'))
        link = f'<a href="/?q={q}">{escape(target)}</a>'
        warning = f'"{link}" already exists!'
        data['message'] = warning if target in '\n'.join(lines) else ''
        for item in items:
            item['revision'] = item['line'].replace(source, target)
    date = lambda k: items[k]['line'][:8]
    for i in range(len(items)):
        begin = (i == 0 or items[i - 1]['left'] in {'┴', '─'})
        close = (i == len(items) - 1 or date(i + 1) != date(i))
        items[i]['left'] = [['┼', '┴'], ['┬', '─']][begin][close]
    count = '&nbsp;' * (14 - len(str(len(items)))) + str(len(items)) + '&nbsp;'
    data['title'], data['q'] = query['q'] or 'Clutter', query['q']
    data['items'], data['count'] = items, count
    return data

app = Flask(__name__)

@app.route('/')
def index():
    request.args.get('add') and push(request.args.get('add'))
    q = request.args.get('q') or ''
    query = parse(q)
    data = process(query)
    if query['swap']:
        return render_template('swap.html', data=data)
    else:
        return render_template('index.html', data=data)

@app.route('/add', methods=['POST'])
def add():
    push(request.data.decode('utf-8'))
    return 'ok'

@app.route('/edit', methods=['POST'])
def edit():
    item = json.loads(request.data.decode('utf-8'))
    lines, n = read()
    index = n - int(item['id'])
    if lines[index] != item['line']:
        return 'no'
    lines[index] = item['revision']
    write(lines)
    return 'ok'

@app.route('/swap', methods=['POST'])
def swap():
    items = json.loads(request.data.decode('utf-8'))
    lines, n = read()
    for item in items:
        index = n - int(item['id'])
        if lines[index] != item['line']:
            return 'no'
        lines[index] = item['revision']
        write(lines)
    return 'ok'

@app.template_filter('link')
def link(line):
    parts = []
    tag = {'#': 'hash', '$': 'dollar', '^': 'caret'}
    for word in line.split(' '):
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

if __name__ == '__main__':
    argv = sys.argv
    if len(argv) < 2:
        print('Path required.')
        sys.exit()
    path = argv[1]
    port = argv[2] if len(argv) > 2 else '12224'
    app.run(port=port)
