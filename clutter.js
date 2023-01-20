if (!localStorage.clutter) {
    localStorage.clutter = '';
}

const escape = x => {
    x = x.replaceAll('&', '&amp;');
    x = x.replaceAll('"', '&quot;');
    x = x.replaceAll("'", '&apos;');
    x = x.replaceAll('<', '&lt;');
    x = x.replaceAll('>', '&gt;');
    return x;
};

const read = () => {
    const lines = localStorage.clutter.split('\n');
    return [lines, lines.length];
};

const write = lines => {
    localStorage.clutter = lines.join('\n');
};

const header = () => {
    const time = new Date();
    const year = time.getFullYear();
    const month = format(time.getMonth() + 1);
    const date = format(time.getDate());
    const hour = format(time.getHours());
    const minute = format(time.getMinutes());
    const second = format(time.getSeconds());
    return year + month + date + hour + minute + second + ' ';
};

const push = content => {
    write([header() + content].concat(read()[0]));
};

const parse = q => {
    const query = { q: q, units: [], sort: null, swap: null };
    for (const word of q.trim().split(/\s+/)) {
        const head = word[0];
        const tail = word.slice(1);
        const convert = word => word.replaceAll('[space]', ' ').toLowerCase();
        if (head === 'S' && word.length >= 4 && word[1] === word.slice(-1)) {
            const chunks = word.split(word[1]);
            if (chunks.length !== 4) { continue; }
            const source = chunks[1].replaceAll('[space]', ' ');
            const target = chunks[2].replaceAll('[space]', ' ');
            query.swap = { source: source, target: target };
            query.units.push({ match: true, word: source.toLowerCase() });
        }
        else if (word.length > 1 && ['A', 'D'].includes(head)) {
            query.sort = { reverse: head === 'D', by: convert(tail) };
            query.units.push({ match: true, word: convert(tail) });
        }
        else if (word.length > 1 && head === 'N') {
            query.units.push({ match: false, word: convert(tail) });
        }
        else {
            query.units.push({ match: true, word: convert(word) });
        }
    }
    return query;
};

const process = query => {
    const [lines, n] = read();
    const data = {};
    let items = [];
    const { units, sort, swap } = query;
    for (const [i, line] of lines.entries()) {
        if (line === '') {
            continue
        }
        const line_ = line.toLowerCase();
        if (units.every(unit => unit.match === line_.includes(unit.word))) {
            items.push({ id: n - i, line: line });
        }
    }
    if (sort) {
        const key = item => {
            const lower = item.line.toLowerCase();
            return lower.slice(lower.indexOf(sort.by));
        };
        const compare = (a, b) => {
            if (key(a) > key(b)) { return 1; }
            else if (key(a) == key(b)) { return 0; }
            else { return -1; }
        };
        const compareFn = (a, b) => {
            return sort.reverse ? compare(b, a) : compare(a, b);
        };
        items = items.sort(compareFn);
    }
    if (swap) {
        const checkCase = item => item.line.includes(swap.source);
        items = items.filter(checkCase);
        const { source, target } = swap;
        const lower = target.toLowerCase();
        const q = encodeURIComponent(lower.replaceAll(' ', '[space]'));
        const link = `<a href="?q=${q}">${escape(target)}</a>`;
        const warning = `"${link}" already exists!`;
        data.message = lines.join('\n').includes(target) ? warning : '';
        for (const item of items) {
            item.revision = item.line.replaceAll(source, target);
        }
    }
    const date = k => items[k].line.slice(0, 8);
    for (let i = 0; i < items.length; i++) {
        const begin = +(i === 0 || ['┴', '─'].includes(items[i - 1].left));
        const close = +(i == items.length - 1 || date(i + 1) !== date(i));
        items[i].left = [['┼', '┴'], ['┬', '─']][begin][close];
    }
    const length = items.length.toString();
    const count = '&nbsp;'.repeat(14 - length.length) + length + '&nbsp;';
    data.title = query.q || 'Clutter';
    data.q = query.q;
    data.items = items;
    data.count = count;
    return data;
};

const createSwap = item => {
    const row = document.createElement('div');
    row.id = item.id;
    document.getElementById('swapRows').appendChild(row);
    const originalRow = document.createElement('div');
    originalRow.className = 'row';
    row.appendChild(originalRow);
    const originalLeft = document.createElement('div');
    originalLeft.className = 'left';
    originalLeft.innerText = '-';
    originalRow.appendChild(originalLeft);
    const originalLine = document.createElement('pre');
    originalLine.className = 'original';
    originalLine.innerHTML = item.line;
    originalRow.appendChild(originalLine);
    const revisionRow = document.createElement('div');
    revisionRow.className = 'row';
    row.appendChild(revisionRow);
    const revisionLeft = document.createElement('div');
    revisionLeft.className = 'left';
    revisionLeft.innerText = '+';
    revisionRow.appendChild(revisionLeft);
    const revisionLine = document.createElement('pre');
    revisionLine.className = 'revision';
    revisionLine.innerHTML = item.revision;
    revisionRow.appendChild(revisionLine);
    const stuff = document.createElement('div');
    stuff.className = 'stuff';
    row.appendChild(stuff);
};

const onSwap = data => {
    document.getElementById('gap').style.display = 'block';
    document.getElementById('space').style.display = 'block';
    document.getElementById('swapRows').style.display = 'block';
    const button = '&nbsp;'.repeat(5) + 'swap' + '&nbsp;'.repeat(5);
    document.getElementById('swap').innerHTML = button;
    document.getElementById('message').innerHTML = '&nbsp;' + data.message;
    for (const item of data.items) {
        createSwap(item);
    }
    const swap = document.getElementById('swap');
    swap.addEventListener('click', async event => {
        if (!confirm('Are you sure?')) { return; }
        if (!postSwap(data.items)) { alert('Error!'); }
        location.href = location.pathname;
    });
};

const createIndex = item => {
    const row = document.createElement('div');
    row.className = 'row';
    row.id = item.id;
    document.getElementById('indexRows').appendChild(row);
    const edit = document.createElement('div');
    edit.className = 'btn left';
    edit.innerText = item.left;
    row.appendChild(edit);
    const pre = document.createElement('pre');
    pre.innerHTML = link(item.line);
    row.appendChild(pre);
    const none = document.createElement('div');
    none.className = 'left none';
    none.innerText = '*';
    row.appendChild(none);
    const input = document.createElement('input');
    input.className = 'none';
    input.spellcheck = false;
    input.value = item.line;
    row.appendChild(input);
    if (['┼', '┬'].includes(edit.textContent)) {
        edit.innerHTML += `<br>│`.repeat(pre.offsetHeight / 15 - 1);
    }
    edit.addEventListener('click', event => {
        edit.style.display = 'none';
        pre.style.display = 'none';
        none.style.display = 'block';
        input.style.display = 'block';
        input.focus();
        const length = input.value.length;
        input.setSelectionRange(length, length);
        row.style.background = 'aliceblue';
    });
    input.addEventListener('keypress', async event => {
        if (event.key !== 'Enter') { return; }
        const item_ = { id: item.id, line: item.line, revision: input.value };
        if (!postEdit(item_)) { alert('Error!'); }
        location.reload();
    });
};

const download = event => {
    const element = document.createElement('a');
    const data = encodeURIComponent(localStorage.clutter);
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + data);
    element.setAttribute('download', header().trim() + '.txt');
    element.click();
};

const upload = event => {
    const reader = new FileReader();
    const element = document.createElement('input');
    element.type = 'file';
    element.addEventListener('change', event => {
        reader.addEventListener('load', event => {
            localStorage.clutter = event.target.result;
            location.href = location.pathname;
        });
        reader.readAsText(event.target.files[0]);
    });
    element.click();
};

const onIndex = data => {
    document.getElementById('getset').style.display = 'flex';
    document.getElementById('new').style.display = 'flex';
    document.getElementById('indexRows').style.display = 'block';
    const get = document.getElementById('get');
    get.addEventListener('click', download );
    const set = document.getElementById('set');
    set.addEventListener('click', upload );
    const add = document.getElementById('add');
    add.addEventListener('keypress', async event => {
        if (event.key !== 'Enter') { return; }
        push(add.value);
        location.reload();
    });
    const plus = document.getElementById('plus');
    plus.addEventListener('click', event => {
        add.value = search.value;
        add.focus();
    });
    for (const item of data.items.slice(0, 1000)) {
        createIndex(item);
    }
    if (data.items.length > 1000) {
        document.getElementById('overflow').style.display = 'flex';
    }
};

const main = () => {
    const params = new URLSearchParams(location.search);
    if (params.has('add')) {
        push(params.get('add'));
        history.replaceState({}, '', location.pathname);
    }
    if (performance.getEntriesByType('navigation')[0].type === 'back_forward') {
        location.reload();
    }
    const q = params.get('q') || '';
    const query = parse(q);
    const data = process(query);
    document.title = data.title;
    document.getElementById('count').innerHTML = data.count;
    const search = document.getElementById('search');
    search.value = data.q;
    search.addEventListener('keypress', event => {
        if (event.key !== 'Enter') { return; }
        const q = encodeURIComponent(search.value);
        location.href = '?q=' + q;
    });
    if (query.swap) {
        onSwap(data);
    }
    else {
        onIndex(data);
    }
    document.querySelectorAll('.left').forEach(element => {
        element.style.visibility = 'visible';
    });
};

const postEdit = item => {
    const [lines, n] = read();
    const index = n - item.id;
    if (lines[index] !== item.line) {
        return false;
    }
    lines[index] = item.revision;
    write(lines);
    return true;
};

const postSwap = items => {
    const [lines, n] = read();
    for (const item of items) {
        const index = n - item.id;
        if (lines[index] !== item.line) {
            return false;
        }
        lines[index] = item.revision;
        write(lines);
    }
    return true;
};

const link = line => {
    const parts = [];
    tag = { '#': 'hash', '$': 'dollar', '^': 'caret' };
    for (const word of line.split(' ')) {
        if (word.startsWith('http')) {
            parts.push(`<a href="${escape(word)}">${escape(word)}</a>`);
        }
        else if (word && word[0] in tag) {
            parts.push(`<span class="${tag[word[0]]}">${escape(word)}</span>`);
        }
        else {
            parts.push(escape(word));
        }
    }
    line = parts.join(' ');
    if (line.match(/\d{14}/)) {
        const year = `<span class="timestamp">${line.slice(0, 4)}</span>`;
        const a = `<a href="?q=${line.slice(0, 8)}">${line.slice(4, 8)}</a>`;
        const moment = `<span class="timestamp">${line.slice(8, 14)}</span>`;
        const body = line.slice(14);
        line = `${year}${a}${moment}${body}`;
    }
    return line;
};

main();
