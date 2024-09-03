// Função de filtro de pesquisa
document.querySelectorAll('.search-bar-tag').forEach((search)=>{
    search.addEventListener('input', function() {
        const searchQuery = this.value.toLowerCase();
        const tags = document.querySelectorAll('.list-tag .list-group label');
        tags.forEach(tag => {
            const name = tag.querySelector('li p').textContent.toLowerCase();        
            if (name.includes(searchQuery)) {
                tag.classList.remove('d-none');
            } else {
                tag.classList.add('d-none');
            }
        });
    });
})

