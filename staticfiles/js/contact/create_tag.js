import  { new_toast, activeTag }  from '../element.js';

// fetch para criar tag
document.querySelectorAll('.createTag').forEach((div)=>{
    div.querySelector(".btn_create_tag").addEventListener('click', function(event) {
        const name_tag = div.querySelector("#new-tag")
        fetch('/contact/create_tag', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': div.querySelector('input[name="csrfmiddlewaretoken"]').value
            },
            body: JSON.stringify({ 'name': name_tag.value})
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erro na criação da tag');
            }
            return response.json().then(data => ({
                status: response.status,
                body: data
            }));
        })
        .then(data => {
            if(data.status === 200){
                new_toast(data.body.message,'error')
                return
            }
            new_toast(data.body.message,'sucess')
            name_tag.value = ''
            const lists = document.querySelectorAll('.list-tag .list-group');
            const html = data.body.tag.modal_tag_html
            lists.forEach((list)=>{
            list.insertAdjacentHTML('beforeend',html)
            const tag = list.querySelector(`label[for='check-tag-${data.body.tag.id}']`)
            activeTag(tag)
            document.querySelector("#conteiner-tags ul").insertAdjacentHTML("beforeend",data.body.tag.tag_html)
            })
            
        })
        .catch(error => {
            console.error('Erro:', error);
        });
    });
})

