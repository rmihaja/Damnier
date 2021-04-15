const body = document.querySelector('body');

print('hello');

// adding random theme to view
const themes = ['space-blue', 'classic-brown'];

body.classList.add(themes[Math.floor(Math.random() * themes.length)]);

console.log(themes[Math.floor(Math.random() * themes.length)]);