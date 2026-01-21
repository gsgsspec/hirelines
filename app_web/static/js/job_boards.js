document.addEventListener("DOMContentLoaded", function () {

    const modal = document.getElementById('modalScrollable');

    modal.addEventListener('show.bs.modal', function (event) {
        const button = event.relatedTarget;
        const jobBoardId = button.getAttribute('data-job-id');
        const jobBoardName = button.getAttribute('data-job-name');

        document.getElementById('modalScrollableTitle').innerText = `${jobBoardName}`;

        document.getElementById('job_board_id').value = jobBoardId;

        document.getElementById('api_key').value = '';
        document.getElementById('endpoint').value = '';
        document.getElementById('username').value = '';
        document.getElementById('password').value = '';
        document.getElementById('is_enabled').checked = false;
        document.getElementById('status').value = 'I';

        const dataObjs = {
            'job-board-id': jobBoardId
        }

        var final_data = {
            'data': JSON.stringify(dataObjs),
            csrfmiddlewaretoken: CSRF_TOKEN,
        }

        $.post(CONFIG['portal'] + "/api/job-board-config", final_data, function (res) {
            if (res.statusCode == 0) {

                const data = res.data || {};

                document.getElementById('api_key').value = data.api_key || '';
                document.getElementById('endpoint').value = data.endpoint || '';
                document.getElementById('username').value = data.username || '';
                document.getElementById('password').value = data.password || '';

                const status = data.status || 'I';
                document.getElementById('is_enabled').checked = (status === 'A');
                document.getElementById('status').value = status;



            }else {
                console.error("API Error:", res.error);
            }
        }).fail(function () {
            console.error("Failed to fetch job board config");
        });
    });

    document.getElementById('is_enabled').addEventListener('change', function () {
        document.getElementById('status').value = this.checked ? 'A' : 'I';
    });

});


document.getElementById('saveJobBoardConfig').addEventListener('click', function () {

    const form = document.getElementById('jobBoardConfigForm');

    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    const payload = {
        job_board_id: document.getElementById('job_board_id').value,
        api_key: document.getElementById('api_key').value,
        endpoint: document.getElementById('endpoint').value,
        username: document.getElementById('username').value,
        password: document.getElementById('password').value,
        status: document.getElementById('status').value  
    };

    const final_data = {
        data: JSON.stringify(payload),
        csrfmiddlewaretoken: CSRF_TOKEN
    };

    $.post(CONFIG['portal'] + "/api/save-job-board-config", final_data, function (res) {

        if (res.statusCode === 0) {

            const jobBoardId = document.getElementById('job_board_id').value;
            const status = document.getElementById('status').value;

            updateJobBoardBadge(jobBoardId, status);
            // Optional: close modal
            $('#modalScrollable').modal('hide');

            // Optional: update UI badge
            console.log("Config saved successfully");
        } else {
            console.error("Save failed:", res.message);
        }

    }).fail(function () {
        console.error("Failed to save job board config");
    });
});


function updateJobBoardBadge(jobBoardId, status) {
    const card = document.querySelector(
        `.jb-card-minimal[data-job-id="${jobBoardId}"]`
    );

    if (!card) return;

    let badge = card.querySelector('.jb-status');

    if (status === "A") {
        if (!badge) {
            badge = document.createElement('span');
            badge.className = 'badge bg-success jb-status';
            badge.innerText = 'Enabled';
            card.appendChild(badge);
        }
    } else {
        // Status = I → remove badge if exists
        if (badge) {
            badge.remove();
        }
    }
}


let filterTimeout = null;

function applyFilters() {
    const showEnabledOnly = document.getElementById('defaultCheck1').checked;
    const searchText = document.getElementById('searchInput').value.toLowerCase();
    const noResults = document.getElementById('noResultsMessage');

    let visibleCount = 0;

    document.querySelectorAll('.jb-card-minimal').forEach(card => {
        const col = card.closest('.job-board-col');
        const name = card.getAttribute('data-name') || '';
        const isEnabled = !!card.querySelector('.jb-status');

        let visible = true;

        if (showEnabledOnly && !isEnabled) {
            visible = false;
        }

        if (searchText && !name.includes(searchText)) {
            visible = false;
        }

        if (visible) {
            col.style.display = '';
            // Force reflow so animation always runs
            col.offsetHeight;
            col.classList.remove('hidden');
            visibleCount++;
        } else {
            col.classList.add('hidden');

            // After animation, hide completely
            setTimeout(() => {
                if (col.classList.contains('hidden')) {
                    col.style.display = 'none';
                }
            }, 250);
        }
    });

    // Empty state
    noResults.style.display = visibleCount === 0 ? 'block' : 'none';
}

// Debounced search
document.getElementById('searchInput').addEventListener('keyup', function () {
    clearTimeout(filterTimeout);
    filterTimeout = setTimeout(applyFilters, 300);
});

// Checkbox filter
document.getElementById('defaultCheck1').addEventListener('change', applyFilters);

