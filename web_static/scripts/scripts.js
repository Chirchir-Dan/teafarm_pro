document.addEventListener('DOMContentLoaded', () => {
    const filterForm = document.getElementById('filter-form');
    const rateForm = document.getElementById('rate-form');

    if (filterForm) {
        filterForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const formData = new FormData(filterForm);
            const response = await fetch(filterForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrf_token') // Adjust based on your CSRF setup
                }
            });

            if (response.ok) {
                const result = await response.json();
                // Update the page with the new data
                document.getElementById('production-records').innerHTML = result.recordsHtml;
                document.getElementById('total-weight').innerText = result.totalWeight;
                document.getElementById('total-payment').innerText = result.totalPayment;
                // Optionally handle other updates or errors
            } else {
                alert('There was a problem with your request.');
            }
        });
    }

    if (rateForm) {
        rateForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            const formData = new FormData(rateForm);
            const response = await fetch(rateForm.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrf_token') // Adjust based on your CSRF setup
                }
            });

            if (response.ok) {
                const result = await response.json();
                alert('Plucking rate updated successfully!');
                // Optionally handle other updates or errors
            } else {
                alert('There was a problem with your request.');
            }
        });
    }
});

<script>
    document.addEventListener('DOMContentLoaded', () => {
        const filterBy = document.getElementById('filter_by');
        const dayFilter = document.getElementById('day_filter');
        const weekFilter = document.getElementById('week_filter');
        const monthFilter = document.getElementById('month_filter');
        const yearFilter = document.getElementById('year_filter');

        function updateFilters() {
            const filterValue = filterBy.value;
            dayFilter.style.display = filterValue === 'day' ? 'block' : 'none';
            weekFilter.style.display = filterValue === 'week' ? 'block' : 'none';
            monthFilter.style.display = filterValue === 'month' ? 'block' : 'none';
            yearFilter.style.display = filterValue === 'year' ? 'block' : 'none';
        }

        // Initialize filters on page load
        updateFilters();

        // Update filters when filter_by changes
        filterBy.addEventListener('change', updateFilters);
    });
</script>

