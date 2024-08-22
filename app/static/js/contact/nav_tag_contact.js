// função para passar as tags 
document.addEventListener('DOMContentLoaded', function () {
    const rows = document.querySelectorAll('tbody tr');
    rows.forEach(row => {
        const leftArrow = row.querySelector('.arrow-left');
        const rightArrow = row.querySelector('.arrow-right');
        const tags = row.querySelectorAll('.conteiner-tags');
        let currentTagIndex = 0;

        function updateTags() {
            tags.forEach((tag, index) => {
                if (index === currentTagIndex) {
                    tag.classList.remove('d-none');
                    tag.classList.add('d-block');
                } else {
                    tag.classList.remove('d-block');
                    tag.classList.add('d-none');
                }
            });
        }

        if (leftArrow) {
            leftArrow.addEventListener('click', () => {
                if (currentTagIndex > 0) {
                    currentTagIndex--;
                    updateTags();
                }
            });
        }

        if (rightArrow) {
            rightArrow.addEventListener('click', () => {
                if (currentTagIndex < tags.length - 1) {
                    currentTagIndex++;
                    updateTags();
                }
            });
        }

        updateTags();
    });
});