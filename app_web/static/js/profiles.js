$(document).ready(function () {
    $.noConflict();
    $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {

        let input = $('#filter_strength').val().trim();
        if (!input) return true;

        let table = $('#profiles-table').DataTable();
        let rowNode = table.row(dataIndex).node();
        if (!rowNode) return true;

        // Strength column = 7th column
        let strengthCell = rowNode.querySelector('td:nth-child(7)');
        if (!strengthCell) return true;

        let strength = parseFloat(strengthCell.getAttribute('data-order')) || 0;

        // Allow only < or >
        let match = input.match(/^([<>])?\s*(\d+)$/);
        if (!match) return false; // Invalid input = show nothing

        let operator = match.group = match[1];
        let value = parseFloat(match[2]);

        if (operator === ">") {
            return strength > value;
        }

        if (operator === "<") {
            return strength < value;
        }

        // No operator → exact match
        return strength == value;
    });


    $('#profiles-table').DataTable({
        "order": [],
        pageLength: 50,
        // scrollY: '600px',
        "ordering": true,
        autoWidth: false,
        columnDefs: [
            {
                targets: 8,   
                visible: false,
                searchable: true  
            }
        ],

        language: { search: "", searchPlaceholder: "Search..." },
        pagingType: 'simple_numbers'
    });
});


document.addEventListener('DOMContentLoaded', () => {
    
    const fromInput = document.getElementById("filter_apl");

    const today = new Date();

    // 1st day of current month (LOCAL time)
    const firstCurrentMonth = new Date(
        today.getFullYear(),
        today.getMonth(),
        1
    );

    // Format YYYY-MM-DD (NO timezone issue)
    const formatDateLocal = (date) => {
        const y = date.getFullYear();
        const m = String(date.getMonth() + 1).padStart(2, '0');
        const d = String(date.getDate()).padStart(2, '0');
        return `${y}-${m}-${d}`;
    };

    fromInput.value = formatDateLocal(firstCurrentMonth);

    const loader = document.getElementById('candidates-loader');

    window.addEventListener('load', () => {
        if (loader) {
            loader.style.display = 'none';
        }
    });
});

// function filter_profiles() {

//     let dataObj = {
//         title: $("#filter_title").val(),
//         exp_from: $("#filter_exp").val(),
//         exp_to: $("#filter_to_1").val(),
//         source: $("#filter_source").val(),
//         skills: $("#filter_skills").val(),
//         status: $("#begin-from").val(),
//         date_from: $("#filter_apl").val(),
//         date_to: $("#filter_to_2").val(),
//     };

//     // Date validation
//     if (dataObj.date_from && dataObj.date_to) {
//         if (dataObj.date_from > dataObj.date_to) {
//             alert("Invalid date range");
//             return;
//         }
//     }

//     // Required for backend
//     let final_data = {
//         data: JSON.stringify(dataObj),
//         csrfmiddlewaretoken: CSRF_TOKEN,
//     };

//     console.log("sending:", final_data);

//     $.post(CONFIG['portal'] + "/api/profile-filters", final_data, function (res) {
//         console.log("received:", res);

//         if (res.statusCode === 0) {

//             let rows = res.data;

//             // Update DataTable
//             let table = $('#profiles-table').DataTable();
//             table.clear().draw();

//             rows.forEach((p) => {

//                 // ===== BUILD SKILLS TEXT (NEW) =====
//                 let skillsText = "";
//                 if (p.primaryskills_name && p.secondaryskills_name) {
//                     skillsText = p.primaryskills_name + ", " + p.secondaryskills_name;
//                 } else if (p.primaryskills_name) {
//                     skillsText = p.primaryskills_name;
//                 } else if (p.secondaryskills_name) {
//                     skillsText = p.secondaryskills_name;
//                 } else {
//                     skillsText = "-";
//                 }

//                 // ===== ADDING YOUR ROW WITH SKILLS =====
//                 table.row.add([
//                     p.date,
//                     p.title,
//                     p.firstname,
//                     p.lastname,
//                     p.experience,
//                     p.source,
//                     skillsText,   // <---- NEW COLUMN
//                     p.status
//                 ]).draw(false);
//             });
//         }
//     });
// }
function filter_profiles() {

    // COLLECT FILTER VALUES
    let dataObj = {
        title: $("#filter_title").val(),
        exp_from: $("#filter_exp").val(),
        exp_to: $("#filter_to_1").val(),
        source: $("#filter_source").val(),
        skills: $("#filter_skills").val(),
        status: $("#begin-from").val(),
        date_from: $("#filter_apl").val(),
        date_to: $("#filter_to_2").val(),
        strength: $("#filter_strength").val()

    };

    // DATE VALIDATION
    if (dataObj.date_from && dataObj.date_to) {
        if (dataObj.date_from > dataObj.date_to) {
            alert("Invalid date range");
            return;
        }
    }

    var final_data = {
        data: JSON.stringify(dataObj),
        csrfmiddlewaretoken: CSRF_TOKEN,
    };

    $.post(CONFIG['portal'] + "/api/profile-filters", final_data, function (res) {

        console.log("res", res);

        if (res.statusCode == 0) {

            var FILTERED_DATA = res.data;   // SAME NAME STYLE AS YOUR REFERENCE

            // DESTROY OLD DATATABLE
            $('#profiles-table').DataTable().destroy();

            // CLEAR OLD ROWS
            $("#profiles-table tbody").html('');

            // LOOP & APPEND ROWS EXACTLY LIKE YOUR REFERENCE
            for (var n = 0; n < FILTERED_DATA.length; n++) {

                var p = FILTERED_DATA[n];
                var tr = '<tr onclick="window.location.href=\'/profileview/' + p["id"] + '\'" style="cursor:pointer;">';


                // SKILLS TEXT METHOD SAME AS BEFORE
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

                 // Experience
                var expText = p["experience"] || "";
                var expNumber = parseInt(expText);
                expNumber = isNaN(expNumber) ? 0 : expNumber;

                // for (var n = 0; n < FILTERED_DATA.length; n++) {

                //     var p = FILTERED_DATA[n];

                    // var tr = '<tr onclick="window.location.href=\'/profileview/' + p["id"] + '\'" style="cursor:pointer;">';
                var strength = parseInt(p["profilestrength"] || 0);

                var strengthClass = "red";
                if (strength >= 70) strengthClass = "green";
                else if (strength >= 40) strengthClass = "orange";

                $("#profiles-table tbody").append(
                        tr
                        + '<td style="width: 180px;">' + p["date"] + '</td>'
                        + '<td>' + p["source"] + '</td>'
                        + '<td>' + p["code"] + '</td>'
                        + '<td>' + p["firstname"] + " " + p["lastname"] + '</td>'
                        + '<td>' + p["title"] + '</td>'
                        +'<td data-order="' + expNumber + '">' + expText + '</td>'
                        + '<td data-order="' + strength + '">'
                        +   '<div class="strength-wrap">'
                        +       '<div class="bar ' + strengthClass + '" style="--w:' + strength + '%;">'
                        +           '<span></span>'
                        +       '</div>'
                        +       '<span class="percent">' + strength + '%</span>'
                        +   '</div>'
                        + '</td>'                        + '<td>' + p["status"] + '</td>'
                        // + '<td>' + (p["profile_tags"] || "") + '</td>'
                        + '<td>' + (p["profile_tags"] ? p["profile_tags"].join(", ") : "") + '</td>'

                        + '</tr>'
                );
            }

                // for (var n = 0; n < FILTERED_DATA.length; n++) {

                //     var p = FILTERED_DATA[n];

                //     var strength = parseInt(p["profilestrength"] || 0);

                //     // Strength color
                //     var strengthClass = "red";
                //     if (strength >= 70) strengthClass = "green";
                //     else if (strength >= 40) strengthClass = "orange";

                //     // Status class
                //     var statusText = (p["status"] || "").trim();
                //     var statusClass = "draft";

                //     if (statusText === "Draft") statusClass = "draft";
                //     else if (statusText === "Ready") statusClass = "ready";
                //     else if (statusText === "Hired") statusClass = "hired";
                //     else if (statusText === "Rejected") statusClass = "rejected";
                //     else if (statusText === "Process") statusClass = "process";

                //     var tr = '<tr onclick="window.location.href=\'/profileview/' + p["id"] + '\'" style="cursor:pointer;">';

                //     $("#profiles-table tbody").append(
                //         tr
                //         + '<td>' + (p["date"] || "") + '</td>'
                //         + '<td>' + (p["source"] || "") + '</td>'
                //         + '<td>' + (p["code"] || "") + '</td>'
                //         + '<td>' + (p["firstname"] || "") + " " + (p["lastname"] || "") + '</td>'
                //         + '<td>' + (p["title"] || "") + '</td>'
                //         + '<td>' + (p["experience"] || "") + '</td>'

                //         // Strength Progress Bar
                //         + '<td>'
                //         +   '<div class="strength-wrap">'
                //         +     '<div class="bar ' + strengthClass + '" style="--w:' + strength + '%;">'
                //         +       '<span></span>'
                //         +     '</div>'
                //         +     '<span class="percent">' + strength + '%</span>'
                //         +   '</div>'
                //         + '</td>'

                //         // Status Badge
                //         + '<td>'
                //         +   '<span class="pill ' + statusClass + '">' + statusText + '</span>'
                //         + '</td>'

                //         + '</tr>'
                //     );
                // }


            // }

            // 4️⃣ REINITIALIZE DATATABLE
            $('#profiles-table').DataTable({
                "order": [],
                "ordering": true,
                autoWidth: false,
                pageLength: 50,
                columnDefs: [
                    {
                        targets: 8,   
                        visible: false,
                        searchable: true   
                    }
                ],
                language: { search: "", searchPlaceholder: "Search..." },
                pagingType: 'simple_numbers'
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
