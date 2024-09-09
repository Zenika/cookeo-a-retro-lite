document.addEventListener('DOMContentLoaded', function () {
    // Récupérer les éléments de la modale
    const historyModal = document.getElementById('historyModal');
    const openHistoryModalButton = document.getElementById('openHistoryModalButton');
    const closeHistoryModalSpan = document.getElementById('closeHistoryModalSpan');

    // Quand l'utilisateur clique sur "Filtrer", on ouvre la modale
    openHistoryModalButton.onclick = function() {
        event.stopPropagation();
        historyModal.style.display = "block";
    };

    // Affiche les checkbox et les select en mode block
    document.querySelectorAll('select').forEach(select => {
        select.style.display = 'block';
    });


    // Quand l'utilisateur clique sur le 'X' ou sur le bouton "Fermer", on ferme la modale
    closeHistoryModalSpan.onclick = function() {
        historyModal.style.display = "none";
    };

    // Quand l'utilisateur clique en dehors de la modale, on la ferme également
    window.onclick = function(event) {
        if (event.target == historyModal) {
            historyModal.style.display = "none";
        }
    };
});
