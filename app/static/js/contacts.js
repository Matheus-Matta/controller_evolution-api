import  {new_toast , loadSpinner}  from './element.js';

// Função de filtro de pesquisa
document.querySelector('#search-bar').addEventListener('input', function() {
    const query = this.value
    const newUrl = new URL(window.location.href);
    if (query.trim()) {
        newUrl.searchParams.set('query', query);
    } else {
        newUrl.searchParams.delete('query');
    }
    window.history.pushState({}, '', newUrl);
    fetch("contact/filter-contacts?query=" + encodeURIComponent(query))
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                document.getElementById('contact-list').innerHTML = data.list_contact;
            } else {
                new_toast(data.message,"error");
            }
        })
        .catch(error => {
            console.error('Erro na requisição:', error);
            new_toast('Ocorreu um erro ao buscar os contatos. Tente novamente mais tarde.',"error");
        });
});

// Função para excluir contatos
document.querySelector('.btn-del-tag').addEventListener('click', function() {
    const selectedContacts = [];
    const checkboxes = document.querySelectorAll('.contact-checkbox:checked');
    checkboxes.forEach(function(checkbox) {
        selectedContacts.push(checkbox.value);
    });

    if (selectedContacts.length > 0) {
        const confirmDelete = confirm("Tem certeza que deseja excluir os contatos selecionados?");
        if (confirmDelete) {
            const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            fetch('/contact/delete', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ 'contacts': selectedContacts })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    location.reload();
                } else {
                    new_toast(data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Erro:', error);
            });
        }
    } else {
        alert('Selecione pelo menos um contato.');
    }
});

// função para atualizar o numero dos contatos
const urlParams = new URLSearchParams(window.location.search);
const pageNumber = urlParams.get('page') ? parseInt(urlParams.get('page')) : 1;
if (pageNumber) {
    const counters = document.querySelectorAll('td[data-counter]');
    counters.forEach((td) => {
        const counterValue = parseInt(td.getAttribute('data-counter')); // Obtém o valor de data-counter
        const multipliedValue = counterValue + ((pageNumber-1)*100); // Multiplica pelo número da página
        td.textContent = multipliedValue;
        td.setAttribute("data-counter", multipliedValue);
    });
}