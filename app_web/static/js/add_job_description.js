var libraryId
var selectValidJd

document.addEventListener('DOMContentLoaded', function() {
    fetchJdLibrarys();

    const searchInput = document.getElementById('searchJobDescription');
    const suggestionsBox = document.getElementById('suggestionsBox');
    const promptMessage = document.getElementById('promptMessage');

    // Function to show suggestions based on the search input
    function showSuggestions() {
        const query = searchInput.value.trim().toLowerCase();

        // Display prompt message if less than 3 characters are entered
        if (query.length < 3) {
            promptMessage.style.display = "block";
            suggestionsBox.style.display = "none";
            return;
        }

        promptMessage.style.display = "none";

        // Filter job descriptions based on the query
        const filteredDescriptions = JDLibrarys.filter(jd =>
            jd.title.toLowerCase().includes(query)
        ).slice(0, 100);  // Limit to 4 suggestions

        // Clear previous suggestions
        suggestionsBox.innerHTML = '';

        // Show suggestions or "No job descriptions found" if none match
        if (filteredDescriptions.length > 0) {
            let suggestionsHTML = '';

            // Loop through the filtered descriptions and build the HTML string
            for (let i = 0; i < filteredDescriptions.length; i++) {
                const jd = filteredDescriptions[i];

                suggestionsHTML += `
                    <div class="suggestion-item p-2 search_item" 
                         style="cursor: pointer;" 
                         data-jdlibraryid="${jd.id}"
                         onclick="selectJd(${jd.id})"
                         >
                        ${jd.title}
                    </div>
                `;
            }

            // Insert the suggestions into the suggestions box
            suggestionsBox.innerHTML = suggestionsHTML;
        } else {
            suggestionsBox.innerHTML = `<div class="p-2 text-muted">No job descriptions found</div>`;
        }

        // Display the suggestions box
        suggestionsBox.style.display = "block";
    }

    // Trigger suggestions on input and focus
    searchInput.addEventListener('input', showSuggestions);
    searchInput.addEventListener('focus', showSuggestions);

    // Hide suggestions on outside click
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.style.display = "none";
        }
    });

    // Add click event to select a suggestion
    suggestionsBox.addEventListener('click', function(e) {
        if (e.target.classList.contains('suggestion-item')) {
            searchInput.value = e.target.textContent.trim();
            searchInput.blur();
            suggestionsBox.style.display = "none";
        }
    });

    // Function to fetch data from the Django API
    async function fetchJdLibrarys() {
        try {
            // Send a GET request to the API endpoint
            const response = await fetch(CONFIG['acert'] + "/api/jd-librarys", {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`Error: ${response.status}`);
            }

            const data = await response.json();

            // Call appendJdLibraryToHtml with the fetched data
            appendJdLibraryToHtml(data.data);  // Assuming `data.data` holds the actual array of JD libraries

        } catch (error) {
            console.error('Failed to fetch jd-libraries:', error);
        }
    }

// Function to append JD libraries
function appendJdLibraryToHtml(jdLibrarys) {
    JDLibrarys = jdLibrarys;
}


// Initialize select2 on jdLibrary
$(document).ready(function () {
    $('#jdLibrary').select2({
            placeholder: "Please Select Job Description",
            allowClear: true
        });
    });
});


// Function to fill JD on Inputs
function selectJd(jdId) {
    selectValidJd = true
    var hrSelectedValue = jdId
    if (hrSelectedValue) {  // Check HR value
        if (JDLibrarys.length > 0) {  // Check JD library data
            for (var jd = 0; jd < JDLibrarys.length; jd++) {
                if (hrSelectedValue == JDLibrarys[jd].id) {
                    libraryId = hrSelectedValue
                    document.getElementById('JobDescription').innerText = JDLibrarys[jd].description ? JDLibrarys[jd].description : "";
                    document.getElementById('min_experince').value = JDLibrarys[jd].minexp ? JDLibrarys[jd].minexp : "";
                    document.getElementById('max_experince').value = JDLibrarys[jd].maxexp ? JDLibrarys[jd].maxexp : "";
                    document.getElementById('jdSkills').innerText = JDLibrarys[jd].skill ? JDLibrarys[jd].skill : "";

                    // Get the role value from the JDLibrarys object
                    const roleValue = JDLibrarys[jd].role ? JDLibrarys[jd].role : "";

                    // Get the select element
                    const roleSelect = document.getElementById('jdRole');

                    // Iterate through all options in the select element
                    for (let i = 0; i < roleSelect.options.length; i++) {
                        // If the option value matches the roleValue, select it
                        if (roleSelect.options[i].value === roleValue) {
                            roleSelect.selectedIndex = i; // Set the selected index
                            break; // Exit the loop once the matching option is found
                        }
                    }
                    break
                }
               
            }

        }
    }
}


// Clear all input fields
function resetJd(){
    selectValidJd = false
    libraryId = ''
    document.querySelectorAll("input").forEach(input => input.value = "");
    document.querySelectorAll("select").forEach(select => select.selectedIndex = 0);
    document.querySelectorAll("textarea").forEach(textarea => textarea.value = "");
    showSuccessMessage('Jd cleared');
}


// saving JD
document.getElementById('addJD').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    if (selectValidJd){ // verifying jd is selected or not selected
        
        const jdValues = {
            title: document.getElementById('searchJobDescription').value,
            jdLibraryId : libraryId,
            jobDesc: document.getElementById('JobDescription').value,
            role: document.getElementById('jdRole').value,
            minExp: document.getElementById('min_experince').value,
            maxExp: document.getElementById('max_experince').value,
            budget: document.getElementById('jdBudget').value,
            noPositions: document.getElementById('jdNoPositions').value,
            workLocation: document.getElementById('jdWorkLocation').value,
            skills: document.getElementById('jdSkills').value,
            anySpecialNote: document.getElementById('JdanySpecialNotes').value
        };

        // Prepare data to be sent to the backend
        var final_data = {
            "data": JSON.stringify(jdValues),
            csrfmiddlewaretoken: CSRF_TOKEN,
        };

        try {
            $.post(CONFIG['portal'] + "/api/add-jd", final_data, function(res) {
                if (res.statusCode == 0) {
                    var newjdid = res.data['newJdId']
                    document.getElementById('validater').hidden = false;
                    setInterval(3000)
                    window.location.href = '/job-description-set-up/'+newjdid;
                }
            });
        } catch (error) {
            console.error('Failed to send data to backend:', error);
        }

    }
    
});

// document.addEventListener('DOMContentLoaded', function () {

//     function updateDropdownOptions() {
//         var selectedValues = Array.from(document.getElementsByClassName('interviewer-select')).map(function (select) {
//             return select.value;
//         });

//         Array.from(document.getElementsByClassName('interviewer-select')).forEach(function (select) {
//             Array.from(select.options).forEach(function (option) {
//                 if (option.value !== "" && selectedValues.includes(option.value)) {
//                     option.disabled = true;
//                 } else {
//                     option.disabled = false;
//                 }
//             });

//             // Ensure "Select Role" option is always disabled
//             if(select.querySelector('option[value=""]')){
//                 select.querySelector('option[value=""]').disabled = true;
//             }
//         });
//     }

//     document.getElementById('addInterviewerButton').addEventListener('click', function () {
//         var container = document.getElementById('interviewPanelContainer');
//         var panelCount = container.getElementsByClassName('interview-panel').length;

//         var newPanel = document.createElement('div');
//         newPanel.classList.add('form-group', 'row', 'interview-panel');
//         newPanel.id = 'panel_' + (panelCount + 1);

//         // var emptyLabelDiv = document.createElement('div');
//         // emptyLabelDiv.classList.add('col-sm-2');
//         // newPanel.appendChild(emptyLabelDiv);

//         var newDiv = document.createElement('div');
//         newDiv.classList.add('col-sm-5');

//         var newSelect = document.createElement('select');
//         newSelect.classList.add('custom-select', 'custom-select-sm', 'interviewer-select','form-select','my-1');
//         newSelect.required = true;

//         var defaultOption = document.createElement('option');
//         defaultOption.value = '';
//         defaultOption.disabled = true;
//         defaultOption.selected = true;
//         defaultOption.textContent = 'Select Interviewer';
//         newSelect.appendChild(defaultOption);

//         interviewersList.forEach(function (interviewer) {
//             var option = document.createElement('option');
//             option.value = interviewer.id;
//             option.textContent = interviewer.name;
//             newSelect.appendChild(option);
//         });

//         newDiv.appendChild(newSelect);
//         newPanel.appendChild(newDiv);

//         var buttonDiv = document.createElement('div');
//         buttonDiv.classList.add('col-xl-2', 'd-flex', 'align-items-center');

//         var removeButton = document.createElement('button');
//         removeButton.type = 'button';
//         removeButton.classList.add('btn', 'btn-danger', 'btn-sm', 'remove-panel-button');
//         removeButton.innerHTML = '<i class="fas fa-trash-alt"></i>';

//         removeButton.addEventListener('click', function () {
//             container.removeChild(newPanel);
//             updateDropdownOptions();
//         });

//         buttonDiv.appendChild(removeButton);
//         newPanel.appendChild(buttonDiv);

//         container.appendChild(newPanel);
//         updateDropdownOptions();

//         newSelect.addEventListener('change', updateDropdownOptions);
//     });

//     Array.from(document.getElementsByClassName('interviewer-select')).forEach(function (select) {
//         select.addEventListener('change', updateDropdownOptions);
//         // Ensure "Select Role" option is always disabled
//         if(select.querySelector('option[value=""]')){
//             select.querySelector('option[value=""]').disabled = true;
//         }
//     });
// });