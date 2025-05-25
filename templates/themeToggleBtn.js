themeToggleBtn.addEventListener('click', function() {
    if (document.body.classList.contains('light-mode')) {
        // Cambiar a modo oscuro
        document.body.classList.remove('light-mode');
        themeToggleBtn.classList.remove('btn-light');
        themeToggleBtn.classList.add('btn-dark');
        themeIcon.classList.remove('fa-sun');
        themeIcon.classList.add('fa-moon');
    } else {
        // Cambiar a modo claro
        document.body.classList.add('light-mode');
        themeToggleBtn.classList.remove('btn-dark');
        themeToggleBtn.classList.add('btn-light');
        themeIcon.classList.remove('fa-moon');
        themeIcon.classList.add('fa-sun');
    }
});