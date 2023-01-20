if (performance.getEntriesByType('navigation')[0].type === 'back_forward') {
    location.reload();
}
const search = document.getElementById('search');
search.addEventListener('keypress', event => {
    if (event.key !== 'Enter') { return; }
    const q = encodeURIComponent(search.value).replaceAll('%20', '+');
    location.href = '/?q=' + q;
});
const items = [];
for (const row of document.getElementById('rows').children) {
    items.push({
        id: row.id,
        line: row.children[0].children[1].innerText,
        revision: row.children[1].children[1].innerText
    });
}
const swap = document.getElementById('swap');
swap.addEventListener('click', async event => {
    if (!confirm('Are you sure?')) { return; }
    const body = JSON.stringify(items);
    const response = await fetch('/swap', { method: 'POST', body: body });
    if (await response.text() === 'no') { alert('Error!'); }
    location.href = '/';
});
document.querySelectorAll('.left').forEach(element => {
    element.style.visibility = 'visible';
});
