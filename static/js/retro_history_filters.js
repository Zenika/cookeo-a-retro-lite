document.addEventListener('DOMContentLoaded', function() {
  const filtersButton = document.getElementById('togglefilter');
  const containerFilters = document.querySelector(".filters")
  const clearFiltersButton = document.getElementById('clearFiltersButton');

  // Ensure select elements are displayed as blocks
  document.querySelectorAll('select').forEach(select => {
    select.style.display = 'block';
  });

  // Function to filter cards based on selected criteria
  function filterCards() {
      const themeFilter = document.getElementById('theme_filter').value;
      const durationFilter = document.getElementById('duration_filter').value;
      const attendeesFilter = document.getElementById('attendees_filter').value;
      const icebreakerFilter = document.getElementById('icebreaker_filter').checked;
      const distancielFilter = document.getElementById('distanciel_filter').checked;
  
      Array.from(document.querySelectorAll(".card")).forEach((card) => {
          const theme = card.dataset.theme;
          const duration = card.dataset.duration;
          const attendees = parseInt(card.dataset.attendees, 10);
          const icebreaker = card.dataset.icebreaker === 'true'; // Convert to boolean
          const distanciel = card.dataset.distanciel === 'true'; // Convert to boolean
  
          // Check if the card matches the selected filters
          const matchTheme = themeFilter === '' || theme === themeFilter;
          const matchDuration = durationFilter === '' || duration === durationFilter;
          const matchAttendees = attendeesFilter === '' || attendees === parseInt(attendeesFilter, 10);
          const matchIcebreaker = !icebreakerFilter || icebreaker;
          const matchDistanciel = !distancielFilter || distanciel;
  
          // Show or hide the card based on filter matching
          card.parentNode.style.display = matchTheme && matchDuration && matchAttendees && matchIcebreaker && matchDistanciel ? 'block' : 'none';
      });
  }

  // Event listener for clearing filters
  clearFiltersButton.addEventListener('click', () => {
      document.getElementById('theme_filter').value = ''; 
      document.getElementById('duration_filter').value = '';
      document.getElementById('attendees_filter').value = '';
      document.getElementById('icebreaker_filter').checked = false;
      document.getElementById('distanciel_filter').checked = false;

      filterCards(); // Apply filters after resetting
  });

  // Event listener for toggling filter visibility
  filtersButton.addEventListener('click', () => {
      const isChecked = filtersButton.getAttribute("aria-checked") === "true";
      containerFilters.style.display = isChecked ? "block" : "none";
      filtersButton.setAttribute("aria-checked", !isChecked);
  });

  // Add event listeners to filters to call filterCards() on change
  document.getElementById('theme_filter').addEventListener('change', filterCards);
  document.getElementById('duration_filter').addEventListener('change', filterCards);
  document.getElementById('attendees_filter').addEventListener('change', filterCards);
  document.getElementById('icebreaker_filter').addEventListener('change', filterCards);
  document.getElementById('distanciel_filter').addEventListener('change', filterCards);

  // Call filterCards() initially to apply filters on page load
  filterCards(); 
});