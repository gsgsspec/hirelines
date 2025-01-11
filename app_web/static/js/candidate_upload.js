$(document).ready(function () {
    $('#process-excel-file').on('click', function () {
        const fileInput = $('#excelFile')[0];
        const selectedFile = fileInput.files[0]; // Access the file directly from the input

        if (!selectedFile) {
            alert("Please select a file before processing!");
            return;
        }

        const reader = new FileReader();

        reader.onload = function (e) {
            const data = new Uint8Array(e.target.result);
            const workbook = XLSX.read(data, { type: 'array' });

            // Assuming the first sheet is needed
            const sheetName = workbook.SheetNames[0];
            const sheet = workbook.Sheets[sheetName];

            // Convert sheet data to JSON
            const jsonData = XLSX.utils.sheet_to_json(sheet, { defval: "" });
            console.log('jsonData',jsonData)

            
            // Generate the table with validation
            displayTableWithValidation(jsonData);
        };

        reader.readAsArrayBuffer(selectedFile);

        // Create a FormData object to send the file
        const formData = new FormData();
        formData.append('file', selectedFile);

        // Send the file to the backend using AJAX
        sendFileToBackend(formData);
    });

    function displayTableWithValidation(data) {
        if (data.length === 0) {
            alert("No data found in the file!");
            return;
        }

        let table = `<table class="table"><thead><tr style="background-color:var(--primary-color)">`;
        // Generate header row from keys of the first object
        for (let key in data[0]) {
            table += `<th style="color:#fff">${key}</th>`;
        }
        table += `</tr></thead><tbody class="table-border-bottom-0">`;

        // Generate rows with validation check for 'Source' field
        data.forEach((row) => {
            table += `<tr>`;
            for (let key in row) {
                // Check if 'Source' field is invalid and apply red font if true
                if (key === 'Source' && row[key] && row[key].length !== 5) {
                    table += `<td style="color: red;">${row[key]}</td>`;
                } else {
                    table += `<td>${row[key]}</td>`;
                }
            }
            table += `</tr>`;
        });

        table += `</tbody></table>`;
        $('#table-container').html(table);
    }

    function sendFileToBackend(formData) {
        var final_data = {
            csrfmiddlewaretoken: CSRF_TOKEN,
        }

        Object.keys(final_data).forEach(key => formData.append(key, final_data[key]));

        $.ajax({
            url: CONFIG['portal'] + '/api/candidate-upload-file',  // Adjust the endpoint
            method: 'POST',
            data: formData,
            contentType: false,  // Important: this tells jQuery not to set the content-type
            processData: false,  // Prevent jQuery from converting the data to a query string
            success: function (response) {
                console.log('File uploaded successfully:', response);
                alert('File has been uploaded successfully!');
                processBackendResponse(response.data);
            },
            error: function (error) {
                console.error('Error uploading file:', error);
                alert('There was an error uploading the file.');
            }
        });
    }
});



const existingSources = Array.isArray(sourcesData) ? sourcesData : [];

const searchInput = document.getElementById("source-code");
const suggestionsBox = document.getElementById("existing-sources");
const selectedSourceLabel = document.getElementById("selected-source");

searchInput.addEventListener("input", function () {

    searchInput.value = searchInput.value.toUpperCase();  // Enforce uppercase

    const query = searchInput.value.trim().toLowerCase();
    suggestionsBox.innerHTML = ""; // Clear suggestions

    if (query === "") {
        selectedSourceLabel.textContent = ""; // Remove label if input is empty
    }

    if (query.length === 5){
        $('#code-error').hide();
    }

    if (query) {
        // Match search against the `code` field
        const matchedSources = existingSources.filter(source =>
            source.code.toLowerCase().includes(query)
        );

        if (matchedSources.length) {

            matchedSources.forEach(source => {
                const suggestion = document.createElement("div");
                suggestion.textContent = source.code; // Display the label
                suggestion.dataset.id = source.id; // Store the id in data attributes
                suggestion.dataset.code = source.code; // Store the code in data attributes

                suggestion.addEventListener("click", function () {
                    searchInput.value = source.code; // Set the input value to the code
                    suggestionsBox.innerHTML = ""; // Clear suggestions
                    suggestionsBox.style.display = "none"; // Hide suggestions
                    selectedSourceLabel.textContent = `${source.label}`;

                    // console.log({
                    //     id: source.id,
                    //     code: source.code,
                    //     label: source.label
                    // });
                    
                });

                suggestionsBox.appendChild(suggestion);
            });
            suggestionsBox.style.display = "block"; // Show suggestions
            
        } else {
            suggestionsBox.style.display = "none"; // Hide suggestions if no matches
        }

        const exactMatch = existingSources.find(source => source.code.toLowerCase() === query);
        
        if (exactMatch) {
            selectedSourceLabel.textContent = exactMatch.label;  // Only update if there's an exact match
        } else {
            selectedSourceLabel.textContent = ""; // Clear the label if there's no exact match
        }

    } else {
        suggestionsBox.style.display = "none"; // Hide suggestions if query is empty
        selectedSourceLabel.textContent = "";
    }
});


// Hide suggestions on blur
searchInput.addEventListener("blur", function () {
    setTimeout(() => suggestionsBox.style.display = "none", 200);
});


const sourceInputField = document.getElementById("source-code");

sourceInputField.addEventListener("keypress", function (e) {

    if (e.key === " " || e.keyCode === 32) {
        e.preventDefault();  // Prevent space from being typed
    }
});




let selectedColumns = {}; // Tracks the final mapping of fields to columns
let usedColumns = new Set(); // Tracks indices of confirmed columns
let currentFieldIndex = 0; // Tracks the current field being processed
let fieldKeys = []; // Stores the keys (field names) from the backend
let fieldData = {}; // Stores the backend response data (column indices)


// Initialize processing based on the backend response
function processBackendResponse(response) {
    fieldKeys = Object.keys(response); // Get the field names
    fieldData = response; // Store the backend data
    currentFieldIndex = 0; // Start with the first field

    highlightNextField(); // Begin with the first field
}

// Highlight the next field
function highlightNextField() {
    if (currentFieldIndex < fieldKeys.length) {
        const fieldName = fieldKeys[currentFieldIndex];
        const columnIndices = fieldData[fieldName];

        // Find the first unused index for the current field
        let columnIndex = columnIndices.find(index => !usedColumns.has(index));

        if (columnIndex !== undefined) {
            // Highlight the suggested column
            highlightColumn({ fieldName, columnIndex });
            selectedColumns[fieldName] = columnIndex; // Tentative selection
        } else {
            // If no default column is available, prompt manual selection
            resetHighlights();
            $('#confirmation-prompt').html(`
                <strong>${fieldName}</strong>: No default column available. Please select manually.
            `);
        }

        // Show confirmation prompt
        showConfirmationPrompt(fieldName);

        // Enable manual selection for the user
        enableManualSelection();
    } else {
        // If all fields are processed
        alert('All columns have been confirmed!');
        $('#confirmation-prompt').html(''); // Clear the prompt
        resetHighlights();

        // Log the final column mapping
        console.log('Final Column Mapping:', selectedColumns);

        sendConfirmedColumnsData(selectedColumns)
    }
}

// Highlight a specific column
function highlightColumn(response) {
    const fieldName = response.fieldName;
    const columnIndex = response.columnIndex;

    // Reset current field highlights
    resetHighlights();

    // Highlight the suggested column with #e3f0fc
    $(`table tbody tr`).each(function () {
        const cell = $(this).find(`td:eq(${columnIndex})`);
        cell.css('background-color', '#e3f0fc'); // Default highlight color
    });

    // Highlight the column header
    // $(`table th:eq(${columnIndex})`).css('background-color', '#e3f0fc');

    // Maintain light grey for confirmed columns
    usedColumns.forEach(index => {
        // $(`table th:eq(${index})`).css('background-color', 'lightgrey');
        $(`table tbody tr td:nth-child(${index + 1})`).css('background-color', 'lightgrey');
    });
}

// Reset all highlights for the current field
function resetHighlights() {
    $('table td').css('background-color', ''); // Reset table cell background
    $('table th').css('background-color', ''); // Reset header background
}

// Show confirmation prompt for the current field
function showConfirmationPrompt(fieldName) {
    $('#confirmation-prompt').html(`
        Confirm the column for <strong>${fieldName}</strong>?
        <button id="confirm-column" class="btn btn-primary">Confirm</button>
    `);

    // Attach the confirm button event
    $('#confirm-column').off('click').on('click', function () {
        proceedToNextField(); // Move to the next field upon confirmation
    });
}

// Enable manual column selection
function enableManualSelection() {
    $('table th').off('click').on('click', function () {
        const columnIndex = $(this).index(); // Get the clicked column index
        const fieldName = $('#confirmation-prompt strong').text(); // Current field name

        // Prevent selecting already confirmed columns
        if (usedColumns.has(columnIndex)) {
            alert('This column has already been selected for another field.');
            return;
        }

        // Update the selection for the current field
        selectedColumns[fieldName] = columnIndex;

        // Highlight the selected column
        highlightColumn({ fieldName, columnIndex });
    });
}

// Proceed to the next field after confirmation
function proceedToNextField() {
    const fieldName = fieldKeys[currentFieldIndex];
    const columnIndex = selectedColumns[fieldName];

    // Confirm the selected column
    if (columnIndex !== undefined && !usedColumns.has(columnIndex)) {
        usedColumns.add(columnIndex); // Mark the column as confirmed

        // Set the confirmed column to light grey
        $(`table th:eq(${columnIndex})`).css('background-color', 'lightgrey');
        $(`table tbody tr td:nth-child(${columnIndex + 1})`).css('background-color', 'lightgrey');

        // Log the confirmation
        console.log(`Field "${fieldName}" confirmed for column index ${columnIndex}`);
    } else {
        console.log(`Field "${fieldName}" could not be confirmed. Please ensure a valid column is selected.`);
    }

    // Move to the next field
    currentFieldIndex++;

    // Highlight the next field
    highlightNextField();
}




function sendConfirmedColumnsData(columnsData) {
    
    dataObjs = {
        'jd': $('#jd').val(),
        'source-code': $('#source-code').val(),
        'columns-data': columnsData
    }

    var final_data = {
        'data': JSON.stringify(dataObjs),
        csrfmiddlewaretoken: CSRF_TOKEN,
    }

    console.log('dataObjs',dataObjs);

    $.post(CONFIG['portal'] + "/api/confirmed-candidates-data", final_data, function (res) {

        if (res.statusCode == 0) {
            var candidateData = res.data

            
        }
        else{
            $("#save-data").prop("disabled", false);
            Swal.fire({
                position: 'center',
                icon: 'error',
                title: 'Error in saving the candidate details',
                text: 'Please try again after some time',
                showConfirmButton: false,
                timer: 1500
            })
        }
    })

}