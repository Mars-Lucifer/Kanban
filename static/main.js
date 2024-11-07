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


function close_pop() {
  let popMain = document.getElementById("popMain");
  let pop = document.getElementById("pop");
  let pop2 = document.getElementById("pop2");
  pop.classList.add("pop-up_close");
  pop2.classList.add("pop-up_close");
  popMain.classList.add("pop-up-main_close");
}

function close_pop_2() {
  const popUpElement = document.getElementById('popNonMain');
  popUpElement.style.display = 'none';
}

function showPopUp(message, url) {
  const popUpElement = document.getElementById('popNonMain');
  const popupButton = document.getElementById('popup-button');
  popUpElement.style.display = 'flex';
  document.querySelector('.pop-up .gray-color').textContent = message;
  popupButton.href = url; // Устанавливаем href кнопки
}


// Функция выхода из аккаунта
document.addEventListener("DOMContentLoaded", function() {
  const profileName = document.getElementById("profile-name");
  const userNameSpan = profileName.querySelector("span");

  profileName.addEventListener("click", function() {
      const userName = userNameSpan.textContent;
      const logoutConfirmed = confirm(`Вы хотите выйти из аккаунта, ${userName}?`);
      
      if (logoutConfirmed) {
          // Перенаправляем на URL выхода
          window.location.href = '/logout';
      }
  });
});