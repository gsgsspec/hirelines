
const profileId = window.location.pathname.split('/')[2]; // profileId 

document.addEventListener('DOMContentLoaded', () => {
    const loader = document.getElementById('candidates-loader');

    const scriptTag = document.getElementById('profileData');
    let fullProfileData = {};

    // Initialize empty arrays to prevent errors if data is missing
    let EducationData = [];
    let ExperienceData = [];
    let ProjectData = [];
    let AwardsData = [];
    let CertificationsData = [];
    let SkillsData = [];

    if (scriptTag && scriptTag.textContent) {
        try {
            fullProfileData = JSON.parse(scriptTag.textContent);

            // Education
            if (fullProfileData.education) {
                EducationData = fullProfileData.education;
            }

            // Experience
            if (fullProfileData.experience) {
                ExperienceData = fullProfileData.experience;
            }

            // Projects
            if (fullProfileData.projects) {
                ProjectData = fullProfileData.projects;
            }

            // Awards
            if (fullProfileData.awards) {
                AwardsData = fullProfileData.awards;
            }

            // Certifications (Check if key is 'certifications' or 'certification' in your DB)
            if (fullProfileData.certificates) {
                CertificationsData = fullProfileData.certificates;
            }

            // Skills (Usually a list of strings like ["Java", "Python"])
            if (fullProfileData.skills) {
                SkillsData = fullProfileData.skills;
            }

            // Personal Info (Inputs)
            if (fullProfileData.personal) {
                const p = fullProfileData.personal;
                $("#Title").val(p.title || "");
                $("#FirstName").val(p.firstname || "");
                $("#MiddleName").val(p.middlename || "");
                $("#LastName").val(p.lastname || "");
                $("#Email").val(p.email || "");
                $("#Mobile").val(p.mobile || "");
                $("#Linkedin").val(p.linkedin || "");
                $("#Facebook").val(p.facebook || "");
                $("#Passport").val(p.passportnum || "");
                $("#FatherName").val(p.fathername || "");
                $("#NativeOf").val(p.nativeof || "");
                $("#DateOfBirth").val(p.dateofbirth || "");
            }

        } catch (e) {
            console.error("Error parsing JSON:", e);
        }
    }

    // Prefill Education Table
    if (EducationData.length > 0) {
        prefillTable("#EducationTable tbody", EducationData);
    }

    // Prefill Experience Table
    if (ExperienceData.length > 0) {
        prefillTable("#ExperienceTable tbody", ExperienceData);
    }

    // Prefill Projects Table
    if (ProjectData.length > 0) {
        prefillTable("#projectTable tbody", ProjectData);
    }

    // Prefill Awards Table
    if (AwardsData.length > 0) {
        prefillTable("#AwardsTable tbody", AwardsData);
    }

    // Prefill Certifications Table
    if (CertificationsData.length > 0) {
        prefillTable("#CertificationsTable tbody", CertificationsData);
    }

    // Prefill Skills (Skills use the specific renderSkill function, not the table function)
    if (SkillsData.length > 0) {
        SkillsData.forEach(skill => renderSkill(skill));
    }

    // Hide the loader when done
    if (loader) {
        loader.style.display = 'none';
    }

    enableSortableForAllTables();
    let today = new Date();
    today.setFullYear(today.getFullYear() - 14);     // subtract 14 years
    let maxDate = today.toISOString().split("T")[0];

    document.getElementById("DateOfBirth").setAttribute("max", maxDate);
});

document.addEventListener('DOMContentLoaded', () => {
    const loader = document.getElementById('candidates-loader');

    window.addEventListener('load', () => {
        loader.style.display = 'none';
    });
});

function tabSwitch(selectedTab) {

    const tab = document.getElementById(selectedTab);
    const targetId = tab.getAttribute("data-target");

    const scrollContainer = document.getElementById("resumeScroll");
    const targetElement = document.getElementById(targetId);

    if (scrollContainer && targetElement) {
        // Calculate the position relative to the scroll container
        const containerTop = scrollContainer.getBoundingClientRect().top;
        const targetTop = targetElement.getBoundingClientRect().top;

        const offset = targetTop - containerTop + scrollContainer.scrollTop;

        scrollContainer.scrollTo({
            top: offset,
            behavior: "smooth"
        });
    }
    $(".custm-tab").removeClass("activeTab shadow");

    // Add active to selected tab
    $("#" + selectedTab).addClass("activeTab shadow");

    // Hide all sections
    $(".tab-section").hide();

    // Show selected section
    $("#" + selectedTab + "Section").fadeIn("fast");

}


// Prefill sample data
function prefillTable(selector, data) {
    let tbody = $(selector);

    data.forEach(item => {
        let row = "<tr>";

        row += `
            <td class="drag-handle" style="cursor: grab;">
                <span style="display: inline-flex; gap: 2px; align-items: center;">
                    <i class="fas fa-ellipsis-v"></i>
                    <i class="fas fa-ellipsis-v"></i>
                </span>
            </td>
        `;

        Object.values(item).forEach(val => {
            row += `<td contenteditable="true">${val}</td>`;

        });

        row += `<td><span class="delete-row-plain-icon">✖</span></td>`;

        row += "</tr>";

        tbody.append(row);
    });
}

$(document).on("click", ".add-row-btn", function () {
    let tableSelector = $(this).data("target"); // e.g. "#projectTable"
    let colCount = $(`${tableSelector} thead th`).length - 2;

    let row = "<tr>";

    row += `
        <td class="drag-handle" style="cursor: grab;">
            <span style="display: inline-flex; gap: 2px; align-items: center;">
                <i class="fas fa-ellipsis-v"></i>
                <i class="fas fa-ellipsis-v"></i>
            </span>
        </td>
    `;

    for (let i = 0; i < colCount; i++) {
        row += `<td contenteditable="true"></td>`;
    }

    row += `<td><span class="delete-row-plain-icon">✖</span></td>`;
    row += "</tr>";

    $(`${tableSelector} tbody`).append(row);
});



const tableKeyMaps = {
    "#projectTable": ["projectname", "clientname", "roleplayed", "skillsused", "yearfrom", "yearto"],
    "#ExperienceTable": ["jobtitle", "companyname", "yearfrom", "yearto"],
    "#EducationTable": ["coursename", "institutename", "yearfrom", "yearto", "grade"],
    "#AwardsTable": ["awardname", "year"],
    "#CertificationsTable": ["cert_name", "year"]
};

function getTableData(tableSelector) {

    let rows = [];

    const dataHeaders = tableKeyMaps[tableSelector];

    if (!dataHeaders) {
        console.error("Error: Key map not defined for table selector:", tableSelector);
        return rows;
    }

    const editableColumnCount = dataHeaders.length;

    let hasEmpty = false; // flag

    $(`${tableSelector} tbody tr`).each(function () {

        let rowData = {};

        $(this).find("td:gt(0):lt(" + editableColumnCount + ")").each(function (i) {

            let value = $(this).text().trim();
            let columnName = dataHeaders[i];

            // Check empty cell
            if (value === "" || value === null || value === undefined) {
                hasEmpty = true;
            }

            rowData[columnName] = value;
        });

        rows.push(rowData);
    });

    // If any empty found  Show SweetAlert + Stop
    if (hasEmpty) {
        Swal.fire({
            title: "Please fill all items",
            icon: "warning",
            confirmButtonColor: "#3085d6",
        });
        return []; // stop returning incomplete data
    }

    return rows;
}

$(document).on("click", ".save-table-btn", function () {
    let tableSelector = $(this).data("target");   // "#projectTable"
    let saveUrl = $(this).data("url");       // Django endpoint

    let tableData = getTableData(tableSelector);

    // If validation failed, stop here (getTableData already showed Swal)
    if (!tableData || tableData.length === 0) {
        return;
    }

    let dataObj = {
        "data": tableData,
        "profile_id": profileId
    };

    let final_data = {
        'data': JSON.stringify(dataObj),
        csrfmiddlewaretoken: CSRF_TOKEN,
    };

    console.log("final_data", final_data);

    $.post(CONFIG['portal'] + saveUrl, final_data)
        .done(function (res) {

            Swal.fire({
                title: "Saved Successfully!",
                icon: "success",
                timer: 1500,
                showConfirmButton: "OK"
            });
        })
        .fail(function (err) {

            Swal.fire({
                title: "Error!",
                text: "Something went wrong while saving.",
                icon: "error",
                confirmButtonText: "OK"
            });
        });
});


$(document).on("click", ".add-row-btn", function () {
    let tableSelector = $(this).data("target");
    addRow(tableSelector);
});


$(document).on("click", ".delete-row-plain-icon", function (e) {
    e.stopPropagation(); // Stop event from triggering row selection
    $(this).closest("tr").remove(); // Remove the closest parent table row
});


$(document).on("submit", "#Person-detais", function (e) {
    e.preventDefault();   // stop normal browser submit

    let dataObj = {
        title: $("#Title").val(),
        firstname: $("#FirstName").val(),
        middlename: $("#MiddleName").val(),
        lastname: $("#LastName").val(),
        email: $("#Email").val(),
        mobile: $("#Mobile").val(),
        linkedin: $("#Linkedin").val(),
        facebook: $("#Facebook").val(),
        passport: $("#Passport").val(),
        dob: $("#DateOfBirth").val(),
        father_name: $("#FatherName").val(),
        native_of: $("#NativeOf").val(),
        profileid: profileId
    };

    $.post(
        CONFIG['portal'] + "/api/update-profile",
        {
            data: JSON.stringify(dataObj),
            csrfmiddlewaretoken: CSRF_TOKEN
        },
        function (response) {
            console.log("Saved!", response);
        }
    ).done(function (res) {

            Swal.fire({
                title: "Saved Successfully!",
                icon: "success",
                timer: 1500,
                showConfirmButton: "OK"
            });
        })
        .fail(function (err) {

            Swal.fire({
                title: "Error!",
                text: "Something went wrong while saving.",
                icon: "error",
                confirmButtonText: "OK"
            });
        });
});

var technologiesList = languages;

const skillsContainer = $("#skillsContainer");

function renderSkill(skillName) {
    if (!skillName) return;

    // Prevent Duplicates
    let exists = false;
    $("#skillsContainer .skill-text").each(function () {
        if ($(this).text().trim().toLowerCase() === skillName.toLowerCase()) exists = true;
    });
    if (exists) return;

    let skillHtml = `
        <div class="skill-bubble">
            <span class="skill-text" contenteditable="false">${skillName}</span>
            <span class="delete-skill-icon">&times;</span>
        </div>
    `;
    skillsContainer.append(skillHtml);
}

$(document).ready(function () {

    // Filter and Show Dropdown
    $("#skillInput").on("keyup", function (e) {
        // Ignore Enter key here (handled in keypress)
        if (e.which === 13) return;

        let inputVal = $(this).val().toLowerCase().trim();
        let suggestionBox = $("#suggestion-box");
        let html = "";
        let count = 0;

        if (inputVal.length > 0) {
            for (let [key, value] of Object.entries(technologiesList)) {
                // Search in Keys (e.g., typing "front" matches "frontend...")
                if (key.toLowerCase().includes(inputVal)) {
                    // Mark first item for Enter key selection
                    let activeClass = (count === 0) ? "active-suggestion" : "";
                    html += `<div class="suggestion-item ${activeClass}" data-value="${value}">${value}</div>`;
                    count++;
                }
            }
        }

        if (html !== "") {
            suggestionBox.html(html).show();
        } else {
            suggestionBox.hide();
        }
    });

    // Handle Click on Suggestion
    $(document).on("click", ".suggestion-item", function () {
        let selectedSkill = $(this).data("value");
        renderSkill(selectedSkill);

        $("#skillInput").val("").focus(); // Clear input
        $("#suggestion-box").hide(); // Hide dropdown
    });

    // Handle Enter Key (Select first suggestion)
    $("#skillInput").on("keypress", function (e) {
        if (e.which === 13) { // Enter key
            e.preventDefault(); // Stop form submit

            // Check if dropdown is visible and has items
            let firstItem = $("#suggestion-box .suggestion-item").first();

            if (firstItem.length > 0 && $("#suggestion-box").is(":visible")) {
                let val = firstItem.data("value");
                renderSkill(val);
                $("#skillInput").val("");
                $("#suggestion-box").hide();
            }
        }
    });

    // Hide Dropdown when clicking outside
    $(document).on("click", function (e) {
        if (!$(e.target).closest("#skillInput, #suggestion-box").length) {
            $("#suggestion-box").hide();
        }
    });


    $(document).on("click", ".delete-skill-icon", function () {
        $(this).closest(".skill-bubble").fadeOut(200, function () {
            $(this).remove();
        });
    });


    $("#save-skills-btn").on("click", function () {
        let saveUrl = $(this).data("url");
        let skillsList = [];


        $("#skillsContainer .skill-bubble .skill-text").each(function () {
            skillsList.push($(this).text().trim());
        });

        let dataObj = {
            "skills": skillsList,
            "profile_id": profileId
        };

        $.post(CONFIG['portal'] + saveUrl, {
            data: JSON.stringify(dataObj),
            csrfmiddlewaretoken: CSRF_TOKEN
        }).done( function (res) {
            
             Swal.fire({
            icon: "success",
            title: "Saved!",
            text: "Your skills have been saved successfully.",
            timer: 1500,
            showConfirmButton: false
        }).fail(function (xhr) {
        Swal.fire({
            icon: "error",
            title: "Oops!",
            text: "Something went wrong while saving.",
        });
    });

        });
    });

});


function enableSortableForAllTables() {
    $(".dynamic-table tbody").each(function () {
        $(this).sortable({
            handle: ".drag-handle",
            animation: 200,
            ghostClass: "ghost"
        });
    });
}