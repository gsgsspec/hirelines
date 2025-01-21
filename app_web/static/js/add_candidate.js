document.getElementById("save-data").onclick = function () {

    $('#candidate-data').unbind('submit').bind('submit', function (event) {
        event.preventDefault(); 

        var inputValue = $('#source-code').val();

        $('#code-error').hide();
        $('#career-code-error').hide();

        if (inputValue.length !== 5) {
            event.preventDefault();  
            $('#code-error').show();
            return false;
        }

        if (inputValue == "CARER") {
            event.preventDefault();
            $('#career-code-error').show();
            return false;
        }

        $("#save-data").prop("disabled", true);
    
        dataObjs = {
            'firstname': $('#firstname').val(),
            'lastname': $('#lastname').val(),
            'email': $('#email').val(),
            'mobile': $('#mobile').val(),
            'jd': $('#jd').val(),
            'begin-from': $('#begin-from').val(),
            'source-code': $('#source-code').val()
        }

        var final_data = {
            'data': JSON.stringify(dataObjs),
            csrfmiddlewaretoken: CSRF_TOKEN,
        }

        $.post(CONFIG['portal'] + "/api/add-candidate", final_data, function (res) {
            if (res.statusCode == 0) {
                var candidateData = res.data

                if (candidateData == "insufficient_credits") {

                    Swal.fire({
                        position: 'center',
                        icon: 'error',
                        title: 'Insufficient Credits',
                        showConfirmButton: true,
                        confirmButtonText: 'OK',
                        confirmButtonColor: '#274699'
                    })

                    $("#save-data").prop("disabled", false);

                    return 
                    
                }

                if (candidateData == "candidate_already_registered") {

                    Swal.fire({
                        position: 'center',
                        icon: 'error',
                        title: 'Candidate already registered for this jd',
                        showConfirmButton: true,
                        confirmButtonText: 'OK',
                        confirmButtonColor: '#274699'
                    })

                    $("#save-data").prop("disabled", false);

                    return 
                    
                }

                if(candidateData['papertype'] == 'I'){
                    window.location.href = '/interview-schedule/'+ candidateData['candidateid']
                } else {
                    Swal.fire({
                        position: 'center',
                        icon: 'success',
                        title: 'Candidate added successfully',
                        showConfirmButton: false,
                        timer: 1500
                    })
                    setTimeout(function () { window.location.href = '/candidates' }, 2000);
                }
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
    })
}


$(document).ready(function () {
    $('#jd').change(function() {
        let jobid = $(this).val();
        $('#begin-from').html('');
        $.get(CONFIG['portal'] + "/api/get-jd-workflow?jid="+jobid, function (res) {
            if(res.statusCode==0){
                var WORKFLOW = res.data
                $("#begin-from").html('')
                $("#begin-from").append('<option value="" disabled selected></option>')
                for (var i = 0; i < WORKFLOW.length; i++) {
                    $("#begin-from").append('<option value='+WORKFLOW[i]["paperid"]+'>' + WORKFLOW[i]["title"] + '</option>')
                }
            }else{
                alert("Cannot able to get JD Workflow")
            }
                
        })

    });
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
        e.preventDefault();  
    }
});

