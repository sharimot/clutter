from flask import Flask, render_template, request
from html import escape
from pathlib import Path
from urllib.parse import quote
import collections
import datetime
import difflib
import json
import logging
import os
import re
import shutil
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

def change(old, new):
    timestamp = datetime.datetime.now().strftime(f'%Y%m%d%H%M%S')
    Path(log_path).touch()
    with open(log_path, 'r') as f:
        original = f.read()
    if old == '':
        delta = new
    elif new == '':
        delta = f'{timestamp}\n{old}'
    else:
        delta = f'{timestamp}\n{new}\n{old}'
    with open(log_path, 'w') as f:
        f.write(delta + '\n\n' + original)

def push(content):
    header = datetime.datetime.now().strftime('%Y%m%d%H%M%S ')
    change('', header + content)
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
        if sort:
            items[i]['left'] = '─'
            continue
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

@app.route('/tag')
def tag():
    request.args.get('add') and push(request.args.get('add'))
    q = request.args.get('q') or ''
    query = parse(q)
    data = process(query)
    tags = collections.Counter()
    for item in data['items']:
        for word in item['line'].split(' '):
            if word.startswith('#'):
                tags[word] += 1
    data['title'] = data['q'] or 'Tag'
    data['tags'] = tags.most_common()
    return render_template('tag.html', data=data)

@app.route('/log')
def log():
    q = request.args.get('q') or ''
    words = [word.replace('[space]', ' ').lower() for word in q.split()]
    with open(log_path, 'r') as f:
        blocks = f.read().split('\n\n')
    items = []
    total = 0
    for block in blocks:
        block_ = block.lower()
        if not all(word in block_ for word in words):
            continue
        total += 1
        if total > 1000:
            continue
        complete = False
        lines = block.split('\n')
        if len(lines) == 1:
            timestamp = lines[0][:14]
        elif len(lines) == 2:
            timestamp = lines[1][:14]
            lines[1] = f'<del>{escape(lines[1])}</del>'
        elif len(lines) == 3:
            timestamp = lines[1][:14]
            if '#plan' in lines[1] and '|' in lines[1]:
                complete = lines[0][:8] == lines[1][:8]
            old, new = '', ''
            for diff in difflib.ndiff(lines[2], lines[1]):
                code, letter = diff[0], escape(diff[2])
                if code == ' ':
                    old += letter
                    new += letter
                elif code == '-':
                    old += f'<del>{letter}</del>'
                elif code == '+':
                    new += f'<ins>{letter}</ins>'
            lines[1], lines[2] = new, old
        else:
            continue
        yyyy = f'<span class="timestamp">{escape(lines[0][:4])}</span>'
        log_q = f'/log?q={quote(lines[0][:8])}#{quote(lines[0][:14])}'
        mmdd = f'<a href="{log_q}">{escape(lines[0][4:8])}</a>'
        hhmmss = f'<span class="timestamp">{escape(lines[0][8:14])}</span>'
        body_ = escape(lines[0][14:])
        body = f'<ins>{body_}</ins>' if body_ else ''
        lines[0] = yyyy + mmdd + hhmmss + body
        href = '/?q=' + quote(timestamp)
        items.append({'href': href, 'lines': lines, 'complete': complete})
    data = {'title': q or 'Log', 'q': q, 'items': items, 'total': total}
    return render_template('log.html', data=data)

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
    change(lines[index], item['revision'])
    lines[index] = item['revision']
    write(lines)
    return 'ok'

@app.route('/swap', methods=['POST'])
def swap():
    backup()
    items = json.loads(request.data.decode('utf-8'))
    lines, n = read()
    for item in items:
        index = n - int(item['id'])
        if lines[index] != item['line']:
            return 'no'
        change(lines[index], item['revision'])
        lines[index] = item['revision']
        write(lines)
    return 'ok'

def backup():
    snapshots = os.path.join(os.path.dirname(path), 'snapshots')
    if not os.path.exists(snapshots):
        os.mkdir(snapshots)
    name = datetime.datetime.now().strftime('%Y%m%d%H%M%S.clutter.txt')
    shutil.copyfile(path, os.path.join(snapshots, name))
    return 'ok'

@app.template_filter('link')
def link(line):
    parts = []
    tag = {'#': 'hash', '$': 'dollar'}
    for word in line.split(' '):
        if word.startswith('http'):
            parts.append(f'<a href="{escape(word)}">{escape(word)}</a>')
        elif word and word[0] in tag:
            parts.append(f'<span class="{tag[word[0]]}">{escape(word)}</span>')
        elif word.startswith('/') and len(word) > 1:
            parts.append(f'<a href="file://{escape(word)}">{escape(word)}</a>')
        else:
            parts.append(escape(word))
    line = ' '.join(parts)
    if re.match(r'\d{14}', line):
        yyyy = f'<span class="timestamp">{line[:4]}</span>'
        mmdd = f'<a href="/?q={line[:8]}#{line[:14]}">{line[4:8]}</a>'
        hh = f'<span class="timestamp">{line[8:10]}</span>'
        mmss = f'<a href="/log?q={line[:14]}">{line[10:14]}</a>'
        body = line[14:]
        line = yyyy + mmdd + hh + mmss + body
    return line

if __name__ == '__main__':
    argv = sys.argv
    if len(argv) < 2:
        print('Path required.')
        sys.exit()
    path = argv[1]
    log_path = path + '.log'
    port = argv[2] if len(argv) > 2 else '12224'
    app.run(port=port)
