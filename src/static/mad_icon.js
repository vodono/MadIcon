$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    $("#position_form").on("keypress", function(e) {
        if (e.keyCode == 13) {
            var form = $(this);
            var form_dict = form.formToDict();
            // validate if coordinates are between 0 and 100 (can be transferred
            // to percentage)
            if (
                form_dict.position_h >= 0 && form_dict.position_h <= 100 &&
                form_dict.position_v >= 0 && form_dict.position_v <= 100
            ) {
                newPosition(form_dict);
                form.find("input[type=text]").val("").select();
            } else {
                alert("Incorrect coordinates")
            }

            return false;
        }
    });

    $(document).click(function(e) {
        position_h = e.pageX * 100 / $(window).width();
        position_v = e.pageY * 100 / $(window).height();
        newPosition({"position_v":position_v, "position_h":position_h});
        return false;
    });

    updater.start();
});

// Verify if new coordinates don't lead to icon out of window and send them
// as JSON to server
function newPosition(position_dict) {
    max_w = ($(window).width() - $("#icon_id").width()) * 100 / $(window).width();
    max_h = ($(window).height() - $("#icon_id").height()) * 100 / $(window).height();

    if (position_dict["position_v"] > max_h) {
        position_dict["position_v"] = max_h;
    }

    if (position_dict["position_h"] > max_w) {
        position_dict["position_h"] = max_w;
    }

    updater.socket.send(JSON.stringify(position_dict));
}

// transfer http form's data to dict
jQuery.fn.formToDict = function() {
    var fields = this.serializeArray();
    var json = {}
    for (var i = 0; i < fields.length; i++) {
        json[fields[i].name] = fields[i].value;
    }
    if (json.next) delete json.next;
    return json;
};

var updater = {
    socket: null,

    start: function() {
        var url = "wss://" + location.host + "/iconsocket";
        updater.socket = new WebSocket(url);
        updater.socket.onmessage = function(event) {
            updater.showIcon(JSON.parse(event.data));
        }
    },

    showIcon: function(position) {
        $("#icon_id").animate({
            left: position.position_h + "%",
            top: position.position_v + "%"
        }, 400)
    }
};
