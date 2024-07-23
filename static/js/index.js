document.addEventListener('DOMContentLoaded', function () {
    var elems = document.querySelectorAll('select');
    var instances = M.FormSelect.init(elems, {});

    // Get the buttons
    const advancedPlusButton = document.getElementById('advancedPlusButton');
    const advancedLessButton = document.getElementById('advancedLessButton');

    // Get Custom sections
    const customOptions = document.getElementById('advancedOptions');
    const  advancedPlusButtonSection = document.getElementById('advancedOptionsPlus');
    const  advancedLessButtonSection = document.getElementById('advancedOptionsLess');

    // Get the form
    const form = document.querySelector('form');

    // Get the error message element
    const errorMessage = document.getElementById('attendees-error');

    // Add event listerners to the buttons
    advancedPlusButton.addEventListener('click', function () {
        customOptions.style.display = 'block';
        advancedPlusButtonSection.style.display = 'none';
        advancedLessButtonSection.style.display = 'block';
    });

    // Add event listerners to the buttons
    advancedLessButton.addEventListener('click', function () {
        customOptions.style.display = 'none';
        advancedPlusButtonSection.style.display = 'block';
        advancedLessButtonSection.style.display = 'none';
    });

    // Add a submit event listener to the form
    form.addEventListener('submit', function(event) {
        // Check if the attendees field is empty
        if (document.getElementById('attendees').value === "") {
            // Prevent the form from submitting
            event.preventDefault();

            // Display the error message
            errorMessage.style.display = 'block';

            // Add a visual cue (e.g., red border)
            document.getElementById('attendees').classList.add('invalid');
        } else {
            // Hide the error message and remove the visual cue
            errorMessage.style.display = 'none';
            document.getElementById('attendees').classList.remove('invalid');
        }
    });
});

