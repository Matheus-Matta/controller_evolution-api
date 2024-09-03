// função para selecionar contato
const rows = document.querySelectorAll('.contact-table-container tbody tr');
rows.forEach(tr => {
    activeSelect(tr)
});
export function activeSelect(tr){
    tr.addEventListener('click', function(event) {
        if (!event.target.closest('.edit-contact')
            && !event.target.closest('.arrow-left')
            && !event.target.closest('.arrow-right')
            && !event.target.closest('.input-name')
            && !event.target.closest('.input-number')) {
            const id = tr.getAttribute('data-contact-id');
            const td = tr.querySelector("td[data-counter]");
            if(!tr.classList.contains("checkbox-active")){
                const checkbox = `<input type="checkbox" name="contact-checkbox" class="contact-checkbox" value="${id}" checked>`;
                td.innerHTML = checkbox;
                tr.classList.add("checkbox-active");
            } else {
                td.innerHTML = td.getAttribute('data-counter');
                tr.classList.remove("checkbox-active");
            }
            ActiveBtnTags();
        }
    });
}

// função para selecionar todos os contatos
const checkAllOn = document.querySelector(".ckeck-all-on");
const checkAllOff = document.querySelector(".ckeck-all-off");
function ActiveBtnTags(){
    const is_actives = document.querySelectorAll('.contact-table-container tbody .checkbox-active');
    const btns = document.querySelectorAll(".btn-tags");
    const qtd = document.querySelector(".qtd-ckeck");
    if(is_actives.length > 0){
        btns.forEach(btn => {
            btn.disabled = false;
        });
        qtd.innerHTML = is_actives.length;
        qtd.classList.remove("d-none");
        checkAllOn.classList.remove("d-none");
        checkAllOff.classList.add("d-none");
    } else {
        btns.forEach(btn => {
            btn.disabled = true;
        });
        qtd.classList.add("d-none");
        checkAllOff.classList.remove("d-none");
        checkAllOn.classList.add("d-none");
    }
}


checkAllOn.addEventListener("click", ()=>{
    const ipt = checkAllOn.querySelector("input");
    if(checkAllOn.classList.contains("check-all")){
        if(ipt.checked == false){
            rows.forEach((tr) => {
                const td = tr.querySelector("td[data-counter]");
                td.innerHTML = td.getAttribute('data-counter');
                tr.classList.remove("checkbox-active");
                ActiveBtnTags();
            });
            checkAllOn.classList.remove("check-all");
            ipt.checked = false;
        }
    } else {
        if(ipt.checked == true){
            rows.forEach((tr) => {
                if(!tr.classList.contains("d-none")){
                    const id = tr.getAttribute('data-contact-id');
                    const td = tr.querySelector("td[data-counter]");
                    if(!tr.classList.contains("checkbox-active")){
                        const checkbox = `<input type="checkbox" name="contact-checkbox" class="contact-checkbox" value="${id}" checked>`;
                        td.innerHTML = checkbox;
                        tr.classList.add("checkbox-active");
                    }
                    ActiveBtnTags();
                }
            });
            checkAllOn.classList.add("check-all");
            ipt.checked = true;
        }
    }
});