$(document).ready(function() {
// здесь открытие/закрытие сайдбара добавляет collapsed когда закрыто  и уберает его когда открыто 
$("#toggle_active_roll").on("click", function() {
        $("#sidebar").toggleClass("collapsed");
        $(".kanban-container").toggleClass("collapsed");

        if ($("#sidebar").hasClass("collapsed")) {
            
            $("#toggle-arrow").attr("src", "/static/icons/arrow_cool_up.svg");
            $(this).find("span").text("Развернуть");
            $(".kanban-container").addClass("collapsed");
        } else {
            $("#toggle-arrow").attr("src", "/static/icons/arrow_cool_down.svg");
            $(this).find("span").text("Свернуть");
            $(".kanban-container").removeClass("collapsed");
        }
    });

    // тут кароче меняются иконки
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
    
    
    
    

});