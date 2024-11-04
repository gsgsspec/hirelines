var JDLibrarys
// var interviewersList = [{'id':1,'name':'Srinivas'},{'id':2,'name':'Srikanth'},{'id':3,'name':'Balu'},{'id':4,'name':'Pratap'}]

document.addEventListener('DOMContentLoaded', function () {
    // Call the fetch function when the page loads
    fetchJdLibrarys(); // Remove the extra console.log and just call the function
});

// Function to fetch data from the Django API
async function fetchJdLibrarys() {
    try {
        // Send a GET request to the API endpoint
        const response = await fetch(CONFIG['acert']+"/api/jd-librarys", {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        // Check if the request was successful
        if (!response.ok) {
            throw new Error(`Error: ${response.status}`);
        }

        // Parse the JSON response
        const data = await response.json();

        // Call appendJdLibraryToHtml with the fetched data
        appendJdLibraryToHtml(data.data);  // Assuming `data.data` holds the actual array of JD libraries

    } catch (error) {
        // Handle any errors that occurred during the fetch
        console.error('Failed to fetch jd-libraries:', error);
    }
}


// Function to append JD librarys to select element
function appendJdLibraryToHtml(jdLibrarys) {
    JDLibrarys = jdLibrarys
    const selectElement = document.getElementById('jdLibrary'); // Assuming the <select> element has this ID

    if (jdLibrarys.length > 0) {
        for (var jd = 0; jd < jdLibrarys.length; jd++) {

            // Check if the 'title' exists and is not null/undefined
            if (jdLibrarys[jd].title){
                const option = document.createElement('option');
                option.value = jdLibrarys[jd].id;
                option.textContent = jdLibrarys[jd].title ? jdLibrarys[jd].title : 'Untitled';
                // Append the option to the select element
                selectElement.appendChild(option);
            }

        }
    }
}


function fillJdData(){
    // hr selected value
    var hrSelectedValue = document.getElementById('jdLibrary').value

    if (hrSelectedValue){ // check hr value
        if (JDLibrarys.length > 0){ // check jd library data
            
            for (var jd = 0; jd < JDLibrarys.length; jd++){
                if(hrSelectedValue == JDLibrarys[jd].id){
                    
                    document.getElementById('JobDescription').innerText = JDLibrarys[jd].description ? JDLibrarys[jd].description : ""
                    document.getElementById('min_experince').value      = JDLibrarys[jd].minexp      ? JDLibrarys[jd].minexp      : ""
                    document.getElementById('max_experince').value      = JDLibrarys[jd].maxexp      ? JDLibrarys[jd].maxexp      : ""
                    document.getElementById('jdSkills').innerText       = JDLibrarys[jd].skill       ? JDLibrarys[jd].skill       : ""

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

                }
            }
        }

    }
}


document.getElementById('addJD').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    var select = document.getElementById("jdLibrary");
    var selectedText = select.options[select.selectedIndex].text;

    // Gather data from the form
    const jdValues = {
        jdLibraryId : document.getElementById('jdLibrary').value,
        title       : selectedText,
        jobDesc     : document.getElementById('JobDescription').value,
        role        : document.getElementById('jdRole').value,
        minExp      : document.getElementById('min_experince').value,
        maxExp      : document.getElementById('max_experince').value,
        budget      : document.getElementById('jdBudget').value,
        noPositions : document.getElementById('jdNoPositions').value,
        workLocation   : document.getElementById('jdWorkLocation').value,
        skills         : document.getElementById('jdSkills').value,
        anySpecialNote : document.getElementById('JdanySpecialNotes').value
    };
    
    // Prepare data to be sent to the backend
    var final_data = {
        "data":JSON.stringify(jdValues),
        csrfmiddlewaretoken: CSRF_TOKEN,
    };

    try {
        $.post(CONFIG['portal'] + "/api/add-jd", final_data, function (res) {
            if (res.statusCode == 0){   
               document.getElementById('validater').hidden = false;
               setInterval(1000)
               window.location.href = '/job-descriptions';
            }
        })

    } catch (error) {
        console.error('Failed to send data to backend:', error);
    }
});



// search for jd librarys
$(document).ready(function () {
    $('#jdLibrary').select2({
      placeholder: "Please Select Job Description",
      allowClear: true
    });
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