if (performance.getEntriesByType('navigation')[0].type === 'back_forward') {
    location.reload();
}

const search = document.getElementById('search');

search.addEventListener('keypress', event => {
    if (event.key !== 'Enter') { return; }
    const q = encodeURIComponent(search.value).replaceAll('%20', '+');
    location.href = '/log?q=' + q;
});

const highlight = new URL(window.location.href).hash.substring(1);

if (highlight) {
    for (const block of document.getElementById('blocks').children) {
        if (!block.firstElementChild) { continue; }
        if (block.firstElementChild.innerText.includes(highlight)) {
            block.classList.add('selected');
            block.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
}
