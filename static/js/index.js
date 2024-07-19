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
});

