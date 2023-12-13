if (performance.getEntriesByType('navigation')[0].type === 'back_forward') {
    location.reload();
}

const search = document.getElementById('search');

search.addEventListener('keypress', event => {
    if (event.key !== 'Enter') { return; }
    const q = encodeURIComponent(search.value).replaceAll('%20', '+');
    location.href = '/tag?q=' + q;
});
