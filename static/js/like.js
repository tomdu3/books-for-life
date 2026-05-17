document.addEventListener('DOMContentLoaded', () => {
    const likeForms = document.querySelectorAll('.like-form');
    
    likeForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const url = this.action;
            const csrfToken = this.querySelector('[name=csrfmiddlewaretoken]').value;
            const btn = this.querySelector('button[type="submit"]');
            const icon = btn.querySelector('i');
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                // Include any form data (like the 'q' parameter)
                body: new URLSearchParams(new FormData(this))
            })
            .then(response => response.json())
            .then(data => {
                if (data.liked !== undefined) {
                    // Update icon based on liked status
                    if (data.liked) {
                        icon.classList.remove('fa-regular', 'text-primary', 'fa-bounce');
                        icon.classList.add('fa-solid', 'text-danger', 'fa-beat');
                    } else {
                        icon.classList.remove('fa-solid', 'text-danger', 'fa-beat');
                        icon.classList.add('fa-regular', 'text-primary', 'fa-bounce');
                    }
                }
                
                if (data.removed !== undefined) {
                    // For user_favourites, remove the row entirely
                    const row = this.closest('tr');
                    if (row) {
                        row.remove();
                    }
                }
                
                // Update likes counter if it exists on the page
                const counter = this.closest('.card-body')?.querySelector('.likes-counter');
                if (counter && data.likes_count !== undefined) {
                    counter.textContent = `Likes: ${data.likes_count}`;
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
});
