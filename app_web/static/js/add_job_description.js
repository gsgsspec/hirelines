var interviewersList = [{'id':1,'name':'Srinivas'},{'id':2,'name':'Srikanth'},{'id':3,'name':'Balu'},{'id':4,'name':'Pratap'}]

document.addEventListener('DOMContentLoaded', function () {

    function updateDropdownOptions() {
        var selectedValues = Array.from(document.getElementsByClassName('interviewer-select')).map(function (select) {
            return select.value;
        });

        Array.from(document.getElementsByClassName('interviewer-select')).forEach(function (select) {
            Array.from(select.options).forEach(function (option) {
                if (option.value !== "" && selectedValues.includes(option.value)) {
                    option.disabled = true;
                } else {
                    option.disabled = false;
                }
            });

            // Ensure "Select Role" option is always disabled
            if(select.querySelector('option[value=""]')){
                select.querySelector('option[value=""]').disabled = true;
            }
        });
    }

    document.getElementById('addInterviewerButton').addEventListener('click', function () {
        var container = document.getElementById('interviewPanelContainer');
        var panelCount = container.getElementsByClassName('interview-panel').length;

        var newPanel = document.createElement('div');
        newPanel.classList.add('form-group', 'row', 'interview-panel');
        newPanel.id = 'panel_' + (panelCount + 1);

        // var emptyLabelDiv = document.createElement('div');
        // emptyLabelDiv.classList.add('col-sm-2');
        // newPanel.appendChild(emptyLabelDiv);

        var newDiv = document.createElement('div');
        newDiv.classList.add('col-sm-5');

        var newSelect = document.createElement('select');
        newSelect.classList.add('custom-select', 'custom-select-sm', 'interviewer-select','form-select','my-1');
        newSelect.required = true;

        var defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.disabled = true;
        defaultOption.selected = true;
        defaultOption.textContent = 'Select Interviewer';
        newSelect.appendChild(defaultOption);

        interviewersList.forEach(function (interviewer) {
            var option = document.createElement('option');
            option.value = interviewer.id;
            option.textContent = interviewer.name;
            newSelect.appendChild(option);
        });

        newDiv.appendChild(newSelect);
        newPanel.appendChild(newDiv);

        var buttonDiv = document.createElement('div');
        buttonDiv.classList.add('col-xl-2', 'd-flex', 'align-items-center');

        var removeButton = document.createElement('button');
        removeButton.type = 'button';
        removeButton.classList.add('btn', 'btn-danger', 'btn-sm', 'remove-panel-button');
        removeButton.innerHTML = '<i class="fas fa-trash-alt"></i>';

        removeButton.addEventListener('click', function () {
            container.removeChild(newPanel);
            updateDropdownOptions();
        });

        buttonDiv.appendChild(removeButton);
        newPanel.appendChild(buttonDiv);

        container.appendChild(newPanel);
        updateDropdownOptions();

        newSelect.addEventListener('change', updateDropdownOptions);
    });

    Array.from(document.getElementsByClassName('interviewer-select')).forEach(function (select) {
        select.addEventListener('change', updateDropdownOptions);
        // Ensure "Select Role" option is always disabled
        if(select.querySelector('option[value=""]')){
            select.querySelector('option[value=""]').disabled = true;
        }
    });
});