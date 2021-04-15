const body = document.querySelector('body');

// adding random theme to view
const themes = ['space-blue', 'classic-brown'];

body.classList.add(themes[Math.floor(Math.random() * themes.length)]);