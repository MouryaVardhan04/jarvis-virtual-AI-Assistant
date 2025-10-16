// ✅ Expose DisplayMessage to Python
eel.expose(DisplayMessage);
function DisplayMessage(message) {
    console.log("From Python:", message);
    $(".siri-message").text(message);
    
    // Stop any current animation to prevent conflicts
    $('.siri-message').textillate('stop'); 

    $('.siri-message').textillate({
        in: { effect: 'fadeInUp', sync: true },
        out: { effect: 'fadeOutUp', sync: true },
        callback: function () {
            console.log("✅ Text animation complete");
            eel.display_done();  // Notify Python
        }
    });

    $('.siri-message').textillate('start');
}

// ✅ Expose showHood to Python
eel.expose(showHood);
function showHood() {
    $("#Oval").show();
    $("#SiriWave").hide();
}

// ✅ Single Mic button handler
$("#MicBtn").click(function () {
    const micSound = document.getElementById("micSound");
    if (micSound) micSound.play();

    // Notify Python to play the assistant sound and start listening
    if (typeof eel !== "undefined" && typeof eel.playAssistantSound === "function") {
      eel.playAssistantSound();
    }

    $("#Oval").hide();
    $("#SiriWave").show();
    $("#siriwave").empty();

    new SiriWave({
        container: document.getElementById('siriwave'),
        width: 600,
        height: 200,
        style: 'ios9',
        amplitude: 1,
        speed: 0.2,
        autostart: true,
    });

    // Call the Python function that handles recording and recognition
    eel.takecommand()();
});