document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('select');
    var instances = M.FormSelect.init(elems, {});
    // Get the button
    const backButton = document.getElementById('backButton');
    // Get UserChoices
    const userChoicesInput = document.getElementById('userChoices');

    // Add event listerners to the buttons
    backButton.addEventListener('click', function() {
        // Implement the "Retour" functionality here
        // For example, you could:
        // - Redirect the user back to the index page
        // - Show a previous version of the retrospective

        window.location.href = '/'; // Redirect to the index page
    });
});