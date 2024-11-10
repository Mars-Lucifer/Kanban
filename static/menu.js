$(document).ready(function() {
    // При загрузке проверяем состояние меню в localStorage
    const isCollapsed = localStorage.getItem("sidebarCollapsed") === "true";

    // Применяем состояние меню при загрузке и обновляем иконку
    if (isCollapsed) {
        $("#sidebar").addClass("collapsed");
        $(".kanban-container").addClass("collapsed");
        $("#toggle-arrow").attr("src", "/static/icons/arrow_cool_up.svg");
        $("#toggle_active_roll").find("span").text("Развернуть");
    } else {
        $("#sidebar").removeClass("collapsed");
        $(".kanban-container").removeClass("collapsed");
        $("#toggle-arrow").attr("src", "/static/icons/arrow_cool_down.svg");
        $("#toggle_active_roll").find("span").text("Свернуть");
    }

    // Функция для обработки клика по кнопке и обновления состояния
    $("#toggle_active_roll").on("click", function() {
        // Переключаем классы и текст для раскрытия/свертывания меню
        $("#sidebar").toggleClass("collapsed");
        $(".kanban-container").toggleClass("collapsed");

        // Определяем текущее состояние (свернуто или развернуто)
        const isNowCollapsed = $("#sidebar").hasClass("collapsed");

        if (isNowCollapsed) {
            $("#toggle-arrow").attr("src", "/static/icons/arrow_cool_up.svg");
            $(this).find("span").text("Развернуть");
            $(".kanban-container").addClass("collapsed");
        } else {
            $("#toggle-arrow").attr("src", "/static/icons/arrow_cool_down.svg");
            $(this).find("span").text("Свернуть");
            $(".kanban-container").removeClass("collapsed");
        }

        // Сохраняем текущее состояние меню в localStorage
        localStorage.setItem("sidebarCollapsed", isNowCollapsed);

        // Обновляем ширину родительского контейнера
        updateParentWidth();
    });

    // Функция для обновления иконок внутри элементов меню
    function updateMenuIcons() {
        $(".page.dymanic").each(function() {
            var img = $(this).find('img');

            if ($(this).hasClass("active")) {
                if (img.attr("src") === "/static/icons/note_stack.svg") {
                    img.attr("src", "/static/icons/note_stack_active.svg");
                } else if (img.attr("src") === "/static/icons/add_circle.svg") {
                    img.attr("src", "/static/icons/add_circle_active.svg");
                }
            } else {
                if (img.attr("src") === "/static/icons/note_stack_active.svg") {
                    img.attr("src", "/static/icons/note_stack.svg");
                } else if (img.attr("src") === "/static/icons/add_circle_active.svg") {
                    img.attr("src", "/static/icons/add_circle.svg");
                }
            }
        });
    }

    // Вызываем обновление иконок при загрузке и после изменения состояния меню
    updateMenuIcons();
    updateParentWidth();
});
