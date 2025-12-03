$(document).ready(function () {
    $.noConflict();
    $('#profiles-table').DataTable({
        "order": [],
        "ordering": false,
        language: { search: "", searchPlaceholder: "Search..." },
        pagingType: 'simple_numbers'
    });
});


document.addEventListener('DOMContentLoaded', () => {
    const loader = document.getElementById('candidates-loader');
    window.addEventListener('load', () => {
        loader.style.display = 'none';
    });
});

function filter_profiles() {

    let dataObj = {
        title: $("#filter_title").val(),
        exp_from: $("#filter_exp").val(),
        exp_to: $("#filter_to_1").val(),
        source: $("#filter_source").val(),
        skills: $("#filter_skills").val(),
        status: $("#begin-from").val(),
        date_from: $("#filter_apl").val(),
        date_to: $("#filter_to_2").val(),
    };

    // Date validation
    if (dataObj.date_from && dataObj.date_to) {
        if (dataObj.date_from > dataObj.date_to) {
            alert("Invalid date range");
            return;
        }
    }

    // Required for backend
    let final_data = {
        data: JSON.stringify(dataObj),
        csrfmiddlewaretoken: CSRF_TOKEN,
    };

    console.log("sending:", final_data);

    $.post(CONFIG['portal'] + "/api/profile-filters", final_data, function (res) {
        console.log("received:", res);

        if (res.statusCode === 0) {

            let rows = res.data;

            // Update DataTable
            let table = $('#profiles-table').DataTable();
            table.clear().draw();

            rows.forEach((p) => {

                // ===== BUILD SKILLS TEXT (NEW) =====
                let skillsText = "";
                if (p.primaryskills_name && p.secondaryskills_name) {
                    skillsText = p.primaryskills_name + ", " + p.secondaryskills_name;
                } else if (p.primaryskills_name) {
                    skillsText = p.primaryskills_name;
                } else if (p.secondaryskills_name) {
                    skillsText = p.secondaryskills_name;
                } else {
                    skillsText = "-";
                }

                // ===== ADDING YOUR ROW WITH SKILLS =====
                table.row.add([
                    p.date,
                    p.title,
                    p.firstname,
                    p.lastname,
                    p.experience,
                    p.source,
                    skillsText,   // <---- NEW COLUMN
                    p.status
                ]).draw(false);
            });
        }
    });
}

// Buttons
$("#applyFilters").click(function () {
    filter_profiles();
});

$("#clearFilters").click(function () {
    location.reload();
});
