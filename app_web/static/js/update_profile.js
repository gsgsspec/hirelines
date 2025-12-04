// const profileId = window.location.pathname.split('/')[2]; // profileId 

// document.addEventListener('DOMContentLoaded', () => {
//     const loader = document.getElementById('candidates-loader');

//     const scriptTag = document.getElementById('profileData');
//     let fullProfileData = {};

//     // Initialize empty arrays to prevent errors if data is missing
//     let EducationData = []; 
//     let ExperienceData = [];
//     let ProjectData = [];
//     let AwardsData = [];
//     let CertificationsData = [];
//     let SkillsData = [];

//     if (scriptTag && scriptTag.textContent) {
//         try {
//             fullProfileData = JSON.parse(scriptTag.textContent);

//             // Education
//             if (fullProfileData.education) {
//                 EducationData = fullProfileData.education;
//             }

//             // Experience
//             if (fullProfileData.experience) {
//                 ExperienceData = fullProfileData.experience;
//             }

//             // Projects
//             if (fullProfileData.projects) {
//                 ProjectData = fullProfileData.projects;
//             }

//             // Awards
//             if (fullProfileData.awards) {
//                 AwardsData = fullProfileData.awards;
//             }

//             // Certifications (Check if key is 'certifications' or 'certification' in your DB)
//             if (fullProfileData.certifications) {
//                 CertificationsData = fullProfileData.certifications;
//             }

//             // Skills (Usually a list of strings like ["Java", "Python"])
//             if (fullProfileData.skills) {
//                 SkillsData = fullProfileData.skills;
//             }

//             // Personal Info (Inputs)
//             if (fullProfileData.personal) {
//                 const p = fullProfileData.personal;
//                 $("#Title").val(p.title || "");
//                 $("#FirstName").val(p.firstname || "");
//                 $("#MiddleName").val(p.middlename || "");
//                 $("#LastName").val(p.lastname || "");
//                 $("#Email").val(p.email || "");
//                 $("#Mobile").val(p.mobile || "");
//                 $("#Linkedin").val(p.linkedin || "");
//                 $("#Facebook").val(p.facebook || "");
//                 $("#Passport").val(p.passportnum || "");
//                 $("#FatherName").val(p.fathername || "");
//                 $("#NativeOf").val(p.nativeof || "");
//                 $("#DateOfBirth").val(p.dob || "");
//             }

//         } catch (e) {
//             console.error("Error parsing JSON:", e);
//         }
//     }

//     // ----------------------------------------------------
//     // 3. Call the prefill functions with the dynamic variables
//     // ----------------------------------------------------

//     // Prefill Education Table
//     if (EducationData.length > 0) {
//         prefillTable("#EducationTable tbody", EducationData);
//     }

//     // Prefill Experience Table
//     if (ExperienceData.length > 0) {
//         prefillTable("#ExperienceTable tbody", ExperienceData);
//     }

//     // Prefill Projects Table
//     if (ProjectData.length > 0) {
//         prefillTable("#projectTable tbody", ProjectData);
//     }

//     // Prefill Awards Table
//     if (AwardsData.length > 0) {
//         prefillTable("#AwardsTable tbody", AwardsData);
//     }

//     // Prefill Certifications Table
//     if (CertificationsData.length > 0) {
//         prefillTable("#CertificationsTable tbody", CertificationsData);
//     }

//     // Prefill Skills (Skills use the specific renderSkill function, not the table function)
//     if (SkillsData.length > 0) {
//         SkillsData.forEach(skill => renderSkill(skill));
//     }

//     // Hide the loader when done
//     if (loader) {
//         loader.style.display = 'none';
//     }

//     enableSortableForAllTables();
// });



// document.addEventListener('DOMContentLoaded', () => {
//     const loader = document.getElementById('candidates-loader');

//     window.addEventListener('load', () => {
//         loader.style.display = 'none';
//     });
// });

//  function tabSwitch(selectedTab) {
//     $(".custm-tab").removeClass("activeTab shadow");

//     // Add active to selected tab
//     $("#" + selectedTab).addClass("activeTab shadow");

//     // Hide all sections
//     $(".tab-section").hide();

//     // Show selected section
//     $("#" + selectedTab + "Section").fadeIn("fast");

// }


// // Prefill sample data
// function prefillTable(selector, data) {
//     let tbody = $(selector);

//     data.forEach(item => {
//         let row = "<tr>";
//         row += `
//             <td class="drag-handle" style="cursor: grab;">
//                 <span style="display: inline-flex; gap: 2px; align-items: center;">
//                     <i class="fas fa-ellipsis-v"></i>
//                     <i class="fas fa-ellipsis-v"></i>
//                 </span>
//             </td>
//         `;
//         Object.values(item).forEach(val => {
//             row += `<td contenteditable="true">${val}</td>`;

//         });
//         // row += `<td><button class="btn btn-danger btn-sm delete-row-icon">✖</button></td>`;
//          row += `<td><span class="delete-row-plain-icon">✖</span></td>`;

//         row += "</tr>";

//         tbody.append(row);
//     });
// }



// // -------------------------
// // ADD ROW
// // -------------------------
// $(document).on("click", ".add-row-btn", function () {
//     let tableSelector = $(this).data("target"); // e.g. "#projectTable"
//     let colCount = $(`${tableSelector} thead th`).length - 2;

//     let row = "<tr>";
//     row += `
//         <td class="drag-handle" style="cursor: grab;">
//             <span style="display: inline-flex; gap: 2px; align-items: center;">
//                 <i class="fas fa-ellipsis-v"></i>
//                 <i class="fas fa-ellipsis-v"></i>
//             </span>
//         </td>
//     `;
//     for (let i = 0; i < colCount; i++) {
//         row += `<td contenteditable="true"></td>`;
//     }
//     // row += `<td><button class="btn btn-danger btn-sm delete-row-icon">✖</button></td>`;
//     row += `<td><span class="delete-row-plain-icon">✖</span></td>`;
//     row += "</tr>";

//     $(`${tableSelector} tbody`).append(row);
// });



// const tableKeyMaps = {

//     // Project keys match the column order (Name, Client, Role, Tech Stack)
//     "#projectTable": ["projectname", "clientname", "roleplayed", "skillsused", "yearfrom", "yearto"], 

//     // Experience keys match the column order (Title, Company, From Year, To Year)
//     "#ExperienceTable": ["jobtitle", "companyname", "yearfrom", "yearto"], 

//     // Education keys match the column order (Course, Institute, From Year, To Year, Grade)
//     "#EducationTable": ["coursename", "institutename", "yearfrom", "yearto", "grade"],

//     // Awards keys match the column order (Name, Purpose, Year)
//     "#AwardsTable": ["awardname",  "year"],

//     // Certifications keys match the column order (Certification Name, Year)
//     "#CertificationsTable": ["cert_name", "year"]


// };
// function getTableData(tableSelector) {
//     let rows = [];

//     // 1. Get the predefined keys for this specific table
//     const dataHeaders = tableKeyMaps[tableSelector];

//     if (!dataHeaders) {
//         console.error("Error: Key map not defined for table selector:", tableSelector);
//         return rows; 
//     }

//     // The number of columns to process is simply the length of our fixed key map
//     const editableColumnCount = dataHeaders.length; 

//     $(`${tableSelector} tbody tr`).each(function () {
//         let rowData = {};

//         // 2. Iterate only over the data cells (excluding the last 'Action' column)
//         // We use :lt() based on the expected number of data columns
//         $(this).find("td:gt(0):lt(" + editableColumnCount  + ")").each(function (i) {

//             // 3. Use the fixed key defined in the map
//             let columnName = dataHeaders[i];
//             rowData[columnName] = $(this).text().trim(); 
//         });

//         rows.push(rowData);
//     });

//     return rows;
// }

// console.log("jQuery version profile:", $.fn.jquery);

// // ===============================
// // UNIVERSAL SAVE BUTTON HANDLER
// // ===============================
//     $(document).on("click", ".save-table-btn", function () {
//         let tableSelector = $(this).data("target");   // example: "#projectTable"
//         let saveUrl      = $(this).data("url");       // Django endpoint

//         let tableData = getTableData(tableSelector);

//         dataObj = {

//             "data": tableData,
//             "profile_id": profileId

//         }

//         console.log("tableData",tableData);

//         var final_data = {
//             'data': JSON.stringify(dataObj),
//             csrfmiddlewaretoken: CSRF_TOKEN,
//         }

//         console.log("final_data",final_data);
//         $.post(CONFIG['portal'] + saveUrl, final_data, function (res) { 



//             })
//     });


//     // $(document).on("click", ".add-row-btn", function () {
//     //     let tableSelector = $(this).data("target");
//     //     addRow(tableSelector);
//     // });

//     $(document).on("click", ".delete-row-plain-icon", function (e) {
//         e.stopPropagation(); // Stop event from triggering row selection
//         $(this).closest("tr").remove(); // Remove the closest parent table row
//     });

//     $(document).on("submit", "#Person-detais", function (e) {
//     e.preventDefault();   // stop normal browser submit

//     let dataObj = {
//         title: $("#Title").val(),
//         firstname: $("#FirstName").val(),
//         middlename: $("#MiddleName").val(),
//         lastname: $("#LastName").val(),
//         email: $("#Email").val(),
//         mobile: $("#Mobile").val(),
//         linkedin: $("#Linkedin").val(),
//         facebook: $("#Facebook").val(),
//         passport: $("#Passport").val(),
//         dob: $("#DateOfBirth").val(),
//         father_name: $("#FatherName").val(),
//         native_of: $("#NativeOf").val(),
//         profileid: profileId
//     };

//     $.post(
//         CONFIG['portal'] + "/api/update-profile",
//         {
//             data: JSON.stringify(dataObj),
//             csrfmiddlewaretoken: CSRF_TOKEN
//         },
//         function (response) {
//             console.log("Saved!", response);
//         }
//     );
// });





// // ===============================
// // SKILLS LOGIC
// // ===============================

// // 1. Prefill Sample Skills
// let sampleSkills = ["Python", "Django", "JavaScript", "HTML5", "CSS3"];
// const skillsContainer = $("#skillsContainer");

// function renderSkill(skillName) {
//     if (!skillName) return;

//     let skillHtml = `
//         <div class="skill-bubble">
//             <span class="skill-text" contenteditable="false">${skillName}</span>
//             <span class="delete-skill-icon">&times;</span>
//         </div>
//     `;
//     skillsContainer.append(skillHtml);
// }

// // Load initial skills
// sampleSkills.forEach(skill => renderSkill(skill));


// // 2. Add New Skill (Click Button)
// $("#addSkillBtn").on("click", function() {
//     let input = $("#skillInput");
//     let val = input.val().trim();

//     if (val) {
//         renderSkill(val);
//         input.val(""); // Clear input
//         input.focus();
//     }
// });

// // 2.1 Add New Skill (Press Enter)
// $("#skillInput").on("keypress", function(e) {
//     if (e.which === 13) { // Enter key
//         $("#addSkillBtn").click();
//     }
// });

// // 3. Delete Skill
// $(document).on("click", ".delete-skill-icon", function() {
//     $(this).closest(".skill-bubble").fadeOut(200, function() {
//         $(this).remove();
//     });
// });

// // 4. Save Skills Logic
// $("#save-skills-btn").on("click", function() {
//     let saveUrl = $(this).data("url");
//     let skillsList = [];

//     // Loop through bubbles and get text
//     $("#skillsContainer .skill-bubble .skill-text").each(function() {
//         skillsList.push($(this).text().trim());
//     });

//     let dataObj = {
//         "skills": skillsList,
//         "profile_id": profileId
//     };

//     console.log("Saving Skills:", dataObj);

//     $.post(CONFIG['portal'] + saveUrl, {
//         data: JSON.stringify(dataObj),
//         csrfmiddlewaretoken: CSRF_TOKEN
//     }, function(res) {
//         console.log("Skills Saved!", res);
//         // Optional: Show a success alert here
//     });
// });

// // In your static/js/profile.js file

// function enableSortableForAllTables() {
//     $(".dynamic-table tbody").each(function () {
//         $(this).sortable({
//             handle: ".drag-handle",
//             animation: 200,
//             ghostClass: "ghost"
//         });
//     });
// }



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
            console.log("Full Profile Data Loaded:", fullProfileData);



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
            if (fullProfileData.certifications) {
                CertificationsData = fullProfileData.certifications;
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
                $("#DateOfBirth").val(p.dob || "");
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



// -------------------------
// ADD ROW
// -------------------------
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

    $(`${tableSelector} tbody tr`).each(function () {

        let rowData = {};

        $(this).find("td:gt(0):lt(" + editableColumnCount + ")").each(function (i) {

            let columnName = dataHeaders[i];
            rowData[columnName] = $(this).text().trim();
        });

        rows.push(rowData);
    });

    return rows;
}


$(document).on("click", ".save-table-btn", function () {
    let tableSelector = $(this).data("target");   // example: "#projectTable"
    let saveUrl = $(this).data("url");       // Django endpoint

    let tableData = getTableData(tableSelector);

    dataObj = {
        "data": tableData,
        "profile_id": profileId
    }

    var final_data = {
        'data': JSON.stringify(dataObj),
        csrfmiddlewaretoken: CSRF_TOKEN,
    }

    $.post(CONFIG['portal'] + saveUrl, final_data, function (res) {



    })

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
    );
});

var technologiesList = languages;

$(document).ready(function () {

    let sampleSkills = ["Python", "Django", "JavaScript", "HTML5", "CSS3"];
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

    sampleSkills.forEach(skill => renderSkill(skill));

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

        console.log("Saving Skills:", dataObj);

        $.post(CONFIG['portal'] + saveUrl, {
            data: JSON.stringify(dataObj),
            csrfmiddlewaretoken: CSRF_TOKEN
        }, function (res) {
            // console.log("Skills Saved!", res);

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