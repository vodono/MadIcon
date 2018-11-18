$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};

    $("#position_form").on("keypress", function(e) {
        if (e.keyCode == 13) {
            var form = $(this);
            newPosition(form.formToDict());
            form.find("input[type=text]").val("").select();
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

function newPosition(position_dict) {
    updater.socket.send(JSON.stringify(position_dict));
}

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

            console.log('message received', event.data, JSON.parse(event.data))

            updater.showIcon(JSON.parse(event.data));
        }
    },

    showIcon: function(position) {
        position_style = "--position_h: " + position.position_h + "%; --position_v: " + position.position_v +"%;";
        $("#icon_id").attr("style", position_style);
        $("#icon_id").slideDown();

//        var existing = $("#m" + position.id);
//        if (existing.length > 0) return;
//        var node = $(position.html);
//        node.hide();
//        $("#inbox").append(node);
//        node.slideDown();
    }
};

//$(window).height();
//$(window).width();
