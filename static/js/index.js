document.addEventListener('DOMContentLoaded', function () {
    var elems = document.querySelectorAll('select');
    var instances = M.FormSelect.init(elems, {});

    // Get the buttons
    const advancedPlusButton = document.getElementById('advancedPlusButton');
    const advancedLessButton = document.getElementById('advancedLessButton');

    // Get Custom sections
    const customOptions = document.getElementById('advancedOptions');
    const advancedPlusButtonSection = document.getElementById('advancedOptionsPlus');
    const advancedLessButtonSection = document.getElementById('advancedOptionsLess');

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

    // Get the loading page 
    const loader = document.getElementById('loading');

    // Add a submit event listener to the form
    form.addEventListener('submit', function (event) {
        // Check if the attendees field is empty
        if (document.getElementById('attendees').value === "") {
            // Prevent the form from submitting
            event.preventDefault();

            // Display the error message
            errorMessage.style.display = 'block';

            // Add a visual cue (e.g., red border)
            document.getElementById('attendees-container').classList.add('attendees', 'invalid');
        } else {
            // Hide the error message and remove the visual cue
            errorMessage.style.display = 'none';
            document.getElementById('attendees-container').classList.remove('attendees', 'invalid');
        }
    });

    form.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submission


        callAIToGenerateBoard();
    });
});

async function fetchGenerateBoard(data) {
    const response = await fetch("/result.html", {
        method: "POST",
        body: data
    });

    if (!response.ok) {
        throw new Error("Error while calling the AI");
    }

    return response.text();
}



async function callAIToGenerateBoard() {
    const form = document.getElementById('myForm');
    const loader = document.getElementById('loading');
    const titleContainer = document.getElementById('title-container');


    loader.style.display = 'block';
    titleContainer.style.display = 'none';

    try {
        const formData = new FormData(form);
        const contentResult = await fetchGenerateBoard(formData);

        document.querySelector('html').innerHTML = contentResult


    } catch (error) {
        console.error(error);
    }
}

window.addEventListener('load', function() {
    // Check if the page has been refreshed
    if (window.performance.getEntriesByType) {
        if (window.performance.getEntriesByType("navigation")[0].type === "reload") {
        // Send a request to the server
        console.log('Refresh event sent to server');
            // Clear form values after refresh
            clearFormValues();
    }}
});

function clearFormValues() {
    // Get the form element
    const form = document.getElementById('myForm');

    // Iterate through all form elements
    for (const element of form.elements) {
        // Clear the value of each element
        if (element.type === 'text' || element.type === 'textarea'  || element.type === 'number') {
            element.value = '';
        } else if (element.type === 'checkbox' || element.type === 'radio') {
            element.checked = false;
        } else if (element.type === 'select-one') {
            element.selectedIndex = 0;
        }
    }
}



