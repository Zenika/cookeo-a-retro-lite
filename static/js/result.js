document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('select');
    var instances = M.FormSelect.init(elems, {});
    var modal = document.getElementById('legalModal');

    // Get UserChoices
    const userChoicesInput = document.getElementById('userChoices');

    // Event Manager for link "politique de confidentialité"
    const privacyPolicyLink = document.getElementById('openPrivacyPolicyModal');

    privacyPolicyLink.addEventListener('click', function(event) {
        event.stopPropagation();
        event.preventDefault();
        modal.style.display = "block";
        const confidentialiteSection = document.getElementById('confidentialite');
        confidentialiteSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
});