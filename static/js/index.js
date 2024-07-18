document.addEventListener('DOMContentLoaded', function () {
    var elems = document.querySelectorAll('select');
    var instances = M.FormSelect.init(elems, {});

    // Get the buttons
    const advancedButton = document.getElementById('advancedButton');

    // Add event listerners to the buttons
    advancedButton.addEventListener('click', function () {
        const customOptions = document.getElementById('advancedOptions');
        if (customOptions.style.display === 'none') {
            customOptions.style.display = 'block';
        } else {
            customOptions.style.display = 'none';
        }
    });
});

