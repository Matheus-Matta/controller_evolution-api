import  {new_toast , loadSpinner}  from './element.js';

// Função de filtro de pesquisa
document.querySelector('#search-bar').addEventListener('input', function() {
    const searchQuery = this.value.toLowerCase();
    searchList(searchQuery)
});

function searchList(query){
    const contacts = document.querySelectorAll('.contact-table-container table tbody tr');
    contacts.forEach(contact => {
        const name = contact.querySelector('.contact-name').textContent.toLowerCase();
        const number = contact.querySelector('.contact-number').textContent.toLowerCase();
        if (name.includes(query) || number.includes(query)) {
            contact.classList.remove('d-none');
        } else {
            contact.classList.add('d-none');
        }
    });
}

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
                    new_toast(data.message, 'success');
                    checkboxes.forEach(checkbox => {
                        checkbox.closest('tr').remove();
                    });
                    const rows = document.querySelectorAll('.contact-table-container tbody tr');
                    document.querySelector("#contact_qtd p").innerText = rows.length
                    document.querySelector(".qtd-ckeck").classList.add("d-none")
                    document.querySelector('#search-bar').value = ''
                    rows.forEach((row,i) =>{
                        row.querySelector("td[data-counter]").innerText = i+1
                    })
                    searchList('')
                    const checkAllOn = document.querySelector(".ckeck-all-on");
                    const checkAllOff = document.querySelector(".ckeck-all-off");
                    checkAllOff.classList.remove("d-none");
                    checkAllOn.classList.add("d-none");
                    checkAllOn.querySelector("input").checked = false
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

