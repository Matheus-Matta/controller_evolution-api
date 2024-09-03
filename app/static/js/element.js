export function new_toast(message,status){
const n = document.querySelectorAll('.toast-container .toast').length + 1
const html = `
             <div class="toast align-items-center" id='new_toast${n}' role="alert" aria-live="assertive" aria-atomic="true" style='background-color: var(--${status});'>
                        <div class="d-flex">
                        <div class="toast-body text-light" style="font-size: 1.1rem;">
                            ${ message }
                        </div>
                        </div>
                    </div>
                </div>`
    document.querySelector(".toast-container").insertAdjacentHTML("beforeend", html)
    var toastEl = document.getElementById('new_toast'+n);
    let delay = 5000
    var toast = new bootstrap.Toast(toastEl, { delay: delay });
    toast.show();
    setTimeout(()=>{toastEl.remove()},delay)
}


export function loadSpinner(bolean){
    if(bolean == true){
        document.querySelector('body').insertAdjacentHTML('beforeend', `
            <div id='spinner' class="conteiner-spinner">
                    <div class="spinner-border mr-2 text-secondary" role="status">
                        <span class="visually-hidden"></span>
                    </div>
             </div>
        `);
    } else {
      const spn = document.querySelector(".conteiner-spinner")
      spn.remove();
    }
}

// funcçao para adicionar o efeito de selecionado as tags do modal
export function activeTag(tag){
    tag.addEventListener("click", function(){
        if(this.classList.contains('active_tag')){
            this.querySelector('p').style.color = "var(--gray) !important"
            this.style.border = '1px solid var(--cleanGray)'
            this.classList.remove("active_tag")
        } else {
            this.querySelector('p').style.color = "var(--sucess) !important"
            this.style.border = '1px solid var(--sucess)'
            this.classList.add("active_tag")
        }
    })
}

export function spinner_button(btn,on){
    if(on){
        btn.setAttribute("data-html", btn.innerHTML)
        btn.innerHTML = `<span class="spinner-border spinner-border-sm" aria-hidden="true"></span>
        <span role="status">Loading...</span>`
        btn.disabled = true;
    } else {
       const html = btn.getAttribute('data-html');
       btn.innerHTML = html
       btn.disabled = false;
    }
}