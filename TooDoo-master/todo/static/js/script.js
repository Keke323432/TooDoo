document.addEventListener('DOMContentLoaded', function() {
    // Function to handle checkbox changes
    document.querySelectorAll('.task-checkbox').forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            const taskId = this.getAttribute('data-task-id');
            const isChecked = this.checked;

            // Send AJAX request to update task status
            fetch('/mark_completed/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify({
                    'task_id': taskId,
                    'completed': isChecked
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Remove the task from the list if completed
                    if (isChecked) {
                        document.getElementById(`task-${taskId}`).remove();
                    }
                } else {
                    console.error('Failed to update task.');
                }
            })
            .catch(error => console.error('Error:', error));
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const logoutLink = document.getElementById('logout-link');
    if (logoutLink) {
        logoutLink.addEventListener('click', function(event) {
            event.preventDefault();
            document.getElementById('logout-form').submit();
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.getElementById('theme-toggle');
    if (!toggleButton) return; // Exit if toggle button is not found

    const currentTheme = localStorage.getItem('theme') || 'light';
    const darkThemeLink = document.createElement('link');

    // Set attributes for the dark theme link element
    darkThemeLink.rel = 'stylesheet';
    darkThemeLink.href = window.darkModeCssUrl; // Use the global variable for the URL
    darkThemeLink.id = 'dark-theme';

    // Check the current theme from local storage and apply dark theme if needed
    if (currentTheme === 'dark') {
        document.head.appendChild(darkThemeLink);
    }

    // Add event listener to toggle button
    toggleButton.addEventListener('click', function() {
        if (document.getElementById('dark-theme')) {
            document.getElementById('dark-theme').remove();
            localStorage.setItem('theme', 'light');
        } else {
            document.head.appendChild(darkThemeLink);
            localStorage.setItem('theme', 'dark');
        }
    });
});



function applyDarkMode() {
            document.body.classList.add('dark-mode');
            document.getElementById('darkModeSwitch').checked = true;
        }

        // Function to remove dark mode
        function removeDarkMode() {
            document.body.classList.remove('dark-mode');
            document.getElementById('darkModeSwitch').checked = false;
        }

        // Function to toggle dark mode
        function toggleDarkMode() {
            if (document.getElementById('darkModeSwitch').checked) {
                applyDarkMode();
                localStorage.setItem('darkMode', 'enabled');
            } else {
                removeDarkMode();
                localStorage.setItem('darkMode', 'disabled');
            }
        }

        

        // Event listener for the dark mode switch
        document.getElementById('darkModeSwitch').addEventListener('change', toggleDarkMode);

        // Check for saved dark mode preference on page load
        window.addEventListener('load', () => {
            const darkMode = localStorage.getItem('darkMode');
            if (darkMode === 'enabled') {
                applyDarkMode();
            } else {
                removeDarkMode();
            }
        });


document.getElementById('darkModeSwitch').addEventListener('change', toggleDarkMode);


