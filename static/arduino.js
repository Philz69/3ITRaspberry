    function updateButtons(data) {
        if(data.mode == 1)
        {
            $('.StartMPPT[value=' + data.channelNumber + ']').hide();
            $('.StopMPPT[value=' + data.channelNumber + ']').show();
            $('.StartSweepIv[value=' + data.channelNumber + ']').show();
        }
        else if(data.mode == 2)
        {
            $('.StopMPPT[value=' + data.channelNumber + ']').hide();
            $('.StartMPPT[value=' + data.channelNumber + ']').show();
            $('.StartSweepIv[value=' + data.channelNumber + ']').hide();
        }
        else
        {
            $('.StopMPPT[value=' + data.channelNumber + ']').hide();
            $('.StartMPPT[value=' + data.channelNumber + ']').show();
            $('.StartSweepIv[value=' + data.channelNumber + ']').show();
        }
    }
$(function() {
    $('.StartSweepIV').each(function() {
            $(this).bind('click',function() {
            var data = {command: "sweep", channelNumber: $(this).val() };
            sendCommand(data).done(updateButtons);
        });
    });
    $('.StartMPPT').each(function() {
            $(this).bind('click',function() {
            var data = {command: "startmppt", channelNumber: $(this).val() };
            sendCommand(data).done(updateButtons);
        });
    });
    $('.StopMPPT').each(function() {
            $(this).bind('click',function() {
            var data = {command: "stopmppt", channelNumber: $(this).val() };
            sendCommand(data).done(updateButtons);
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

function sendCommand(data) {
            return $.ajax({
                type: "POST",
                url: "/_send_command",
                data: JSON.stringify(data),
                contentType: "application/json"
            });
}