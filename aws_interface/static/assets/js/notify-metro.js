$.notify.addStyle("metro", {
    html:
        "<div>" +
            "<div class='text-wrapper'>" +
                "<div class='title' data-notify-html='status' style='display:inline-block; margin-right: 10px;'/>" +
                "<div class='text' data-notify-html='text' style='display:inline-block;'/>" +
            "</div>" +
        "</div>",
    classes: {
        error: {
            "color": "#fafafa !important",
            "background-color": "#F71919",
            "border": "1px solid #FF0026"
        },
        success: {
            "background-color": "#32CD32",
            "border": "1px solid #4DB149"
        },
        info: {
            "color": "#fafafa !important",
            "background-color": "#6772e5",
            "border": "1px solid #777fd5",
        },
        warning: {
            "background-color": "#FAFA47",
            "border": "1px solid #EEEE45"
        },
        black: {
            "color": "#fafafa !important",
            "background-color": "#333",
            "border": "1px solid #000"
        },
        white: {
            "background-color": "#f1f1f1",
            "border": "1px solid #ddd"
        }
    }
});