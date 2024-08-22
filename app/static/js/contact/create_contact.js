import {new_toast} from '../element.js';
import { activeSelect } from './select_contact.js';
import { activeEditMode } from './edit_contact.js';

document.getElementById('addContactForm').addEventListener('submit', function(event) {
    event.preventDefault();
    
    const formData = new FormData(this);
    const name = formData.get('name');
    const number = formData.get('number');
    
    // Verificação do formato do número
    const numberPattern = /^55\d{11}$/;
    if (!numberPattern.test(number)) {
        new_toast('Número deve estar no formato 5521912345678', 'error');
        return;
    }

    fetch('/contact/create', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        },
        body: JSON.stringify({ name, number })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            console.log(data)
            new_toast(data.message, 'success');
            this.reset();
            document.querySelector('tbody').insertAdjacentHTML('beforeend', data.contact_html);
            document.querySelector("#contact_qtd p").innerText = data.contact_len
            const contact = document.querySelector(`tr[data-contact-id='${data.contact_id}'`)
            activeSelect(contact)
            activeEditMode(contact.querySelector(".edit-contact"))
        } else if (data.error) {
            new_toast(data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        new_toast('Erro ao adicionar contato', 'error');
    });
});
