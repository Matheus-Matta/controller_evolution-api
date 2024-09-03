import { new_toast, spinner_button } from '../element.js';
import { activeSelect } from './select_contact.js';
import { activeEditMode } from './edit_contact.js';

const form_import = document.getElementById('form_import')
form_import.addEventListener('submit', function(event) {
    event.preventDefault();
})

document.getElementById('import-submit').addEventListener('click', function(event) {
    event.preventDefault();

    const form = document.getElementById('form_import');
    const formData = new FormData(form);
    const activeTags = Array.from(form.querySelectorAll('.active_tag input')).map(input => input.value);
    activeTags.forEach(tag => {
        formData.append('tags', tag);
    });
    form_import.style.opacity = '0.5'
    form_import.style.cursor = 'default'
    spinner_button(this,true)
    fetch('/contact/import', {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data =>{
        form_import.style.opacity = '1'
        form_import.style.cursor = 'initial'
        spinner_button(this,false)
        if(data.status != "success"){
            new_toast(data.message, data.status)
        } else {
            new_toast(data.message, data.status)
            const modalElement = document.getElementById('importModal');
            modalElement.classList.remove("show")
            const modalbackdrop = document.querySelector('.modal-backdrop');
            modalbackdrop.classList.remove("show")
        }
    })
    .catch(error => console.error('Erro:', error));
});
