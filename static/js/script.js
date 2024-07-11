document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('select');
    var instances = M.FormSelect.init(elems, {});
});
document.getElementById('advancedButton').addEventListener('click', function() {
var customOptions = document.getElementById('advancedOptions');
if (customOptions.style.display === 'none') {
    customOptions.style.display = 'block';
} else {
    customOptions.style.display = 'none';
}
});