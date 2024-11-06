function opens() {
    const menu = document.getElementById("hamburger");

    menu.style.display = 'flex';
    setTimeout(() => {
        menu.classList.add("show");
    }, 10);
}

function closes() {
    const menu = document.getElementById("hamburger");

    menu.classList.remove("show");
    setTimeout(() => {
        menu.style.display = 'none';
    }, 500);
}