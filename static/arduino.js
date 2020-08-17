$(function() {
    $('#SweepIV').each(function() {
            $(this).bind('click',function() {
            var data = {command: "mppt", channelNumber: $(this).val() };
            $.ajax({
                type: "POST",
                url: "/_send_command",
                data: JSON.stringify(data),
                contentType: "application/json",
            });
        });
    });
    $('#getChannels').bind('click',function() {
        $.getJSON('/_get_channels', {
        }, function(data) {
            $("#result").text(data.channels);
        });
        return false;
    });
});