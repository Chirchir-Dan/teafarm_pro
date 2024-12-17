document.addEventListener("DOMContentLoaded", function() {
    // Function to switch between tabs
    function setFilterType(type) {
        document.querySelectorAll('.tab-content').forEach(function(tab) {
            tab.style.display = 'none';
        });
        document.getElementById(type + '-tab').style.display = 'block';
    }

    // Set initial filter type based on the hidden input
    const filterType = document.getElementById('filter_type').value;
    if (filterType) {
        setFilterType(filterType);
    }

    // Add event listeners to tab buttons
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', function() {
            const type = this.getAttribute('onclick').match(/'(\w+)'/)[1];
            document.getElementById('filter_type').value = type;
            setFilterType(type);
        });
    });

    // Enforce Sunday selection for the week tab
    const weekDateInput = document.getElementById('start_date_week');
    if (weekDateInput) {
        weekDateInput.addEventListener('change', function() {
            enforceSunday(this);
        });
    }

    // Function to ensure only Sundays are selectable in the week tab
    function enforceSunday(dateInput) {
        if (!dateInput.value) return; // If no date is selected, do nothing

        const selectedDate = new Date(dateInput.value);
        const dayOfWeek = selectedDate.getDay();

        // If the selected date is not a Sunday (day 0), adjust it to the nearest Sunday
        if (dayOfWeek !== 0) {
            const adjustedSunday = new Date(selectedDate);
            adjustedSunday.setDate(selectedDate.getDate() - dayOfWeek);

            // Format date to YYYY-MM-DD to set it back to the input field
            const yyyy = adjustedSunday.getFullYear();
            const mm = String(adjustedSunday.getMonth() + 1).padStart(2, '0'); // Months are zero-indexed
            const dd = String(adjustedSunday.getDate()).padStart(2, '0');
            
            // Update the input field with the adjusted Sunday date
            dateInput.value = `${yyyy}-${mm}-${dd}`;
            
            alert('Only Sundays are selectable. Adjusting to the nearest Sunday.');
        }
    }
});
