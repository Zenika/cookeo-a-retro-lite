// Get the modal
var modal;

document.addEventListener('DOMContentLoaded', function() {
    modal = document.getElementById('legalModal');

    // Get the button that opens the modal
    var btn = document.getElementById("openLegalModal");

    // Get the <span> element that closes the modal
    var span = document.getElementById("closeModalButton");

    // Get the button "Fermer" that closes the modal
    const closeLegalModalButton = document.getElementById("closeLegalModalButton");

    // When the user clicks the button, open the modal 
    btn.addEventListener('click', function(event) {
        event.stopPropagation();
        modal.style.display = (modal.style.display === 'block') ? 'none' : 'block';
    });

    // When the user clicks on <span> (x), close the modal
    span.addEventListener('click', function(event) {
        event.stopPropagation();
        modal.style.display = "none";
    });

    // When the user clicks on "Fermer", close the modal
    closeLegalModalButton.addEventListener('click', function() {
        modal.style.display = "none";
    });

    // When the user clicks anywhere outside of the modal, close it
    window.addEventListener('click', function(event) {
        if (event.target != modal) {
            modal.style.display = "none";
        }
    });

    // When the user use the Escape key, close the modal
    document.addEventListener('keydown', function(event) {
        if (event.key === "Escape" && modal.style.display === 'block') {
            modal.style.display = "none";
        }
    });

});