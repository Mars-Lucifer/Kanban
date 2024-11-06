// Функция для отображения текущего времени и даты
function updateCurrentDateTime() {
    const timeElement = document.getElementById('currentTime');
    const dateElement = document.getElementById('currentDate');

    const currentTime = new Date();
    const hours = String(currentTime.getHours()).padStart(2, '0'); // Получаем часы
    const minutes = String(currentTime.getMinutes()).padStart(2, '0'); // Получаем минуты

    // Форматируем дату
    const options = { weekday: 'long', day: 'numeric', month: 'long' };
    const formattedDate = currentTime.toLocaleDateString('ru-RU', options).split(', ');

    // Приводим день недели к заглавной букве
    const dayOfWeek = formattedDate[0].charAt(0).toUpperCase() + formattedDate[0].slice(1);

    timeElement.textContent = `${hours}:${minutes}`; // Обновляем текст элемента только с часами и минутами
    dateElement.innerHTML = `<p>${dayOfWeek}</p><p>${formattedDate[1]}</p>`; // Обновляем текст элемента с датой
}

// Обновляем время и дату каждую секунду
setInterval(updateCurrentDateTime, 1000);

// Вызываем функцию сразу, чтобы не ждать первую секунду
updateCurrentDateTime();

// Ширина для sidebar
const parent = document.querySelector('.sidebar__space');
const child = document.querySelector('.sidebar');

function updateParentWidth() {
  const childWidth = child.getBoundingClientRect().width;
  const parentPadding = 
    parseFloat(getComputedStyle(parent).paddingLeft) + 
    parseFloat(getComputedStyle(parent).paddingRight);
  
  parent.style.width = `${childWidth + parentPadding}px`;
}

// Вызов при загрузке и обновлении
updateParentWidth();
window.addEventListener('resize', updateParentWidth);
