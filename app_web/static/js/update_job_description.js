function activeJDOrInactiveJd() {
    var statusLabel = document.getElementById('statusLabel');
    var jdStatus = document.getElementById('jdStatus');

    // Check if the checkbox is checked
    if (jdStatus.checked) {
        statusLabel.textContent = '( Active )';
    } else {
        statusLabel.textContent = '( Inactive )';
    }
}


document.getElementById('addJD').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission
    var jdStatus
    var jdStatusElement = document.getElementById('jdStatus');
    if (jdStatusElement.checked) {
        jdStatus = 'D'
    } else {
        jdStatus = 'I'
    }

    // Gather data from the form
    const jdValues = {
        JdID         : JdId,
        title       : document.getElementById('JdTitle').value,
        jobDesc     : document.getElementById('JobDescription').value,
        role        : document.getElementById('jdRole').value,
        minExp      : document.getElementById('min_experince').value,
        maxExp      : document.getElementById('max_experince').value,
        budget      : document.getElementById('jdBudget').value,
        noPositions : document.getElementById('jdNoPositions').value,
        workLocation   : document.getElementById('jdWorkLocation').value,
        skills         : document.getElementById('jdSkills').value,
        anySpecialNote : document.getElementById('JdanySpecialNotes').value,
        jobDescriptionStatus : jdStatus,
    };
    
    // Prepare data to be sent to the backend
    var final_data = {
        "data":JSON.stringify(jdValues),
        csrfmiddlewaretoken: CSRF_TOKEN,
    };

    try {
        $.post(CONFIG['portal'] + "/api/update-jd", final_data, function (res) {
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