// Dark Mode Toggle
document.addEventListener('DOMContentLoaded', function() {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const darkModeIcon = document.getElementById('darkModeIcon');
    const lightModeIcon = document.getElementById('lightModeIcon');
    const body = document.body;
    
    // Check for saved theme preference or use system preference
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    const storedTheme = localStorage.getItem('darkMode');
    
    if (storedTheme === 'true' || (storedTheme === null && prefersDarkScheme.matches)) {
        enableDarkMode();
    } else {
        disableDarkMode();
    }
    
    // Toggle dark mode on button click
    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', () => {
            if (body.classList.contains('dark')) {
                disableDarkMode();
            } else {
                enableDarkMode();
            }
        });
    }
    
    // Functions to enable/disable dark mode
    function enableDarkMode() {
        body.classList.add('dark');
        darkModeIcon.classList.add('hidden');
        lightModeIcon.classList.remove('hidden');
        localStorage.setItem('darkMode', 'true');
    }
    
    function disableDarkMode() {
        body.classList.remove('dark');
        darkModeIcon.classList.remove('hidden');
        lightModeIcon.classList.add('hidden');
        localStorage.setItem('darkMode', 'false');
    }
    
    // Listen for changes in system preference
    prefersDarkScheme.addEventListener('change', (e) => {
        if (!localStorage.getItem('darkMode')) {
            if (e.matches) {
                enableDarkMode();
            } else {
                disableDarkMode();
            }
        }
    });
});
