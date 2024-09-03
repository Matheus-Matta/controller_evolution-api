
// Editar contato
document.querySelectorAll('.edit-contact').forEach((button)=>{
    activeEditMode(button)
});

export function activeEditMode(button){
    const edit = button.querySelector('.edit-button');
    const confirm = button.querySelector('.confirm-edit');
    const tr = button.closest('tr');
    const nameTd = tr.querySelector('.contact-name');
    const numberTd = tr.querySelector('.contact-number');

    edit.addEventListener('click', function(event) {
        if (!tr.classList.contains('edit-mode')) {
            tr.classList.add('edit-mode');
            edit.classList.add('d-none');
            confirm.classList.remove('d-none');
            nameTd.innerHTML = `<input type="text" name="name" value="${nameTd.textContent.trim()}" class="form-control input-name">`;
            numberTd.innerHTML = `<input type="number" name="number" value="${numberTd.textContent.trim().substring(1)}" class="form-control input-number">`;
            
            // Add global click listener
            document.addEventListener('click', ClickOutside);
        }
    });

    confirm.addEventListener("click", ()=>{
        saveChanges();
    });

    function saveChanges() {
        const input_name = tr.querySelector(".input-name");
        const input_number = tr.querySelector(".input-number");
        nameTd.innerHTML = `<td class="contact-name">${input_name.value}</td>`;
        numberTd.innerHTML = `<td class="contact-number" style="font-weight: 500; letter-spacing: 1px;">+${input_number.value}</td>`;
        confirm.classList.add('d-none');
        edit.classList.remove('d-none');
        tr.classList.remove('edit-mode');

        const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
        const id = tr.getAttribute('data-contact-id');
        fetch('/contact/update', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken 
            },
            body: JSON.stringify({'id': id, 'name':input_name.value, 'number': input_number.value})
        })
        .catch((error) => {
            console.error('Error:', error);
        });

        document.removeEventListener('click', ClickOutside);
    }

    function ClickOutside(event) {
        if (!tr.contains(event.target) && tr.classList.contains('edit-mode')) {
            cancelEdit();
            document.removeEventListener('click', ClickOutside);
        }
    }

    function cancelEdit() {
        nameTd.innerHTML = nameTd.querySelector('input').value;
        numberTd.innerHTML = `+${numberTd.querySelector('input').value}`;
        confirm.classList.add('d-none');
        edit.classList.remove('d-none');
        tr.classList.remove('edit-mode');
    }
}