import  { new_toast, activeTag }  from './element.js';

document.querySelectorAll('.list-tag .list-group label').forEach((tag)=>{
    activeTag(tag)
})

// Função para coletar contatos selecionados e abrir o modal
document.querySelector('.btn-add-tag').addEventListener('click',()=>{
    const selectedContacts = [];
    const checkboxes = document.querySelectorAll('.contact-checkbox:checked');
    checkboxes.forEach(function(checkbox) {
        selectedContacts.push(checkbox.closest('tr').dataset.contactId);
    });

    if (selectedContacts.length > 0) {
        document.getElementById('selected-contacts').value = selectedContacts.join(',');
        $('#addTagModal').modal('show');
    } else {
        alert('Selecione pelo menos um contato.');
    }
});

// fetch para adicionar tags aos contatos selecionados
document.getElementById('addTagform').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(this);
    const selectedContacts = formData.get('selected-contacts').split(',');
    const activeTags = Array.from(document.querySelectorAll('.active_tag input')).map(input => input.value);
    const csrfToken = formData.get('csrfmiddlewaretoken');
    fetch('/contact/add_tags_to_contacts', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            'contacts': selectedContacts,
            'tags': activeTags
        })
    })
    .then(response => {
        if (!response.ok) {
            new_toast("erro ao adicionar tags",'error')
            throw new Error('Erro ao adicionar tags aos contatos');
        } else {
            location.reload();
        }
    })
    .catch(error => {
        console.error('Erro:', error);
    });
});