if (new URLSearchParams(location.search).get('add')) {
    history.replaceState({}, '', '/');
}
if (performance.getEntriesByType('navigation')[0].type === 'back_forward') {
    location.reload();
}
const search = document.getElementById('search');
search.addEventListener('keypress', event => {
    if (event.key !== 'Enter') { return; }
    const q = encodeURIComponent(search.value);
    location.href = '/?q=' + q;
});
const add = document.getElementById('add');
add.addEventListener('keypress', async event => {
    if (event.key !== 'Enter') { return; }
    await fetch('/add', { method: 'POST', body: add.value });
    location.reload();
});
const plus = document.getElementById('plus');
plus.addEventListener('click', event => {
    add.value = search.value;
    add.focus();
});
for (const row of document.getElementById('rows').children) {
    const edit = row.querySelector('div');
    const pre = row.querySelector('pre');
    const none = row.querySelector('div.none');
    const input = row.querySelector('input');
    const line = input.value;
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
        const item = { id: row.id, line: line, revision: input.value };
        const body = JSON.stringify(item);
        const response = await fetch('/edit', { method: 'POST', body: body });
        if (await response.text() === 'no') { alert('Error!'); }
        location.reload();
    });
};