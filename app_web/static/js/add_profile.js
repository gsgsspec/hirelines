document.getElementById("save-data").onclick = function () {

    $('#candidate-data').unbind('submit').bind('submit', function (event) {
        event.preventDefault(); 

        // var inputValue = $('#source-code').val();

        // $('#code-error').hide();
        // $('#career-code-error').hide();

        // if (inputValue.length !== 5) {
        //     event.preventDefault();  
        //     $('#code-error').show();
        //     return false;
        // }

        // if (inputValue == "CARER") {
        //     event.preventDefault();
        //     $('#career-code-error').show();
        //     return false;
        // }

        $("#save-data").prop("disabled", true);
        $("#save-data").html('Please wait &nbsp; <i class="fas fa-circle-notch fa-spin"></i>');
    
        dataObjs = {
            'title': $('#title').val(),
            'firstname': $('#firstname').val(),
            'middlename': $('#middlename').val(),
            'lastname': $('#lastname').val(),
            'email': $('#email').val(),
            'source-code': $('#source-type').val()
        }

        var formData = new FormData();

        formData.append("data", JSON.stringify(dataObjs));
        formData.append("csrfmiddlewaretoken", CSRF_TOKEN);

        // var fileObj = $('#resumeInput')[0].files[0];

        if (!selectedFile) {
            Swal.fire({
                icon: "warning",
                title: "Please attach resume",
                text: "Resume file is required.",
                confirmButtonColor: '#274699'
            });

            $("#save-data").prop("disabled", false);
            $("#save-data").html('Save');
            return false; 
        }

        formData.append("attachment", selectedFile);

        $.ajax({
            url: CONFIG['portal'] + "/api/add-profile",
            type: "POST",
            data: formData,
            processData: false,
            contentType: false,
            success: function (res) {
                if (res.statusCode == 0) {

                    Swal.fire({
                        icon: "success",
                        title: "Profile added",
                        text: "The profile was created successfully!",
                        timer: 1500,
                        showConfirmButton: false
                    });

                    setTimeout(function () {
                        window.location.href = "/profiles";
                    }, 1500);

                }else {
                    $("#save-data").prop("disabled", false);
                    $("#save-data").html('Save');

                    Swal.fire(
                        "Error",
                        "Unable to add profile",
                        "error"
                    );
                }
            }
        });
    })
}


// const existingSources = Array.isArray(sourcesData) ? sourcesData : [];

// const searchInput = document.getElementById("source-code");
// const suggestionsBox = document.getElementById("existing-sources");
// const selectedSourceLabel = document.getElementById("selected-source");

// searchInput.addEventListener("input", function () {

//     searchInput.value = searchInput.value.toUpperCase();  // Enforce uppercase

//     const query = searchInput.value.trim().toLowerCase();
//     suggestionsBox.innerHTML = ""; // Clear suggestions

//     if (query === "") {
//         selectedSourceLabel.textContent = ""; // Remove label if input is empty
//     }

//     if (query.length === 5){
//         $('#code-error').hide();
//     }

//     if (query) {
//         // Match search against the `code` field
//         const matchedSources = existingSources.filter(source =>
//             source.code.toLowerCase().includes(query)
//         );

//         if (matchedSources.length) {

//             matchedSources.forEach(source => {
//                 const suggestion = document.createElement("div");
//                 suggestion.textContent = source.code; // Display the label
//                 suggestion.dataset.id = source.id; // Store the id in data attributes
//                 suggestion.dataset.code = source.code; // Store the code in data attributes

//                 suggestion.addEventListener("click", function () {
//                     searchInput.value = source.code; // Set the input value to the code
//                     suggestionsBox.innerHTML = ""; // Clear suggestions
//                     suggestionsBox.style.display = "none"; // Hide suggestions
//                     selectedSourceLabel.textContent = `${source.label}`;

//                 });

//                 suggestionsBox.appendChild(suggestion);
//             });
//             suggestionsBox.style.display = "block"; // Show suggestions
            
//         } else {
//             suggestionsBox.style.display = "none"; // Hide suggestions if no matches
//         }

//         const exactMatch = existingSources.find(source => source.code.toLowerCase() === query);
        
//         if (exactMatch) {
//             selectedSourceLabel.textContent = exactMatch.label;  // Only update if there's an exact match
//         } else {
//             selectedSourceLabel.textContent = ""; // Clear the label if there's no exact match
//         }

//     } else {
//         suggestionsBox.style.display = "none"; // Hide suggestions if query is empty
//         selectedSourceLabel.textContent = "";
//     }
// });


// // Hide suggestions on blur
// searchInput.addEventListener("blur", function () {
//     setTimeout(() => suggestionsBox.style.display = "none", 200);
// });


// const sourceInputField = document.getElementById("source-code");

// sourceInputField.addEventListener("keypress", function (e) {

//     if (e.key === " " || e.keyCode === 32) {
//         e.preventDefault();  
//     }
// });



let selectedFile = null;

document.getElementById("resumeInput").addEventListener("change", function(event) {
    if (event.target.files[0]) {
        handleFile(event.target.files[0]);
    }
});


function removeFile(event) {
    event.stopPropagation(); // prevent triggering file picker

    selectedFile = null;
    document.getElementById("resumeInput").value = "";

    // Reset UI
    document.getElementById("filePreview").style.display = "none";
    document.getElementById("defaultText").style.display = "block";
    document.getElementById("removeBtn").style.display = "none";
}


function dragOver(event) {
    event.preventDefault();
    document.getElementById("uploadBox").classList.add("drag-over");
}

function dragLeave(event) {
    event.preventDefault();
    document.getElementById("uploadBox").classList.remove("drag-over");
}

function dropFile(event) {
    event.preventDefault();
    document.getElementById("uploadBox").classList.remove("drag-over");

    const file = event.dataTransfer.files[0];
    if (!file) return;

    handleFile(file);
}


function handleFile(file) {
    const ext = file.name.split('.').pop().toLowerCase();
    let iconUrl = "";

    if (ext === "pdf") {
        iconUrl = "/static/img/pdf.png";
    } else if (ext === "doc" || ext === "docx") {
        iconUrl = "/static/img/doc.png";
    } else {
        Swal.fire({
            icon: "error",
            title: "Invalid File",
            text: "Only PDF or Word files are allowed!",
            confirmButtonColor: "#274699"
        });
        return;
    }

    selectedFile = file;

    document.getElementById("fileIcon").src = iconUrl;
    document.getElementById("fileName").textContent = file.name;

    document.getElementById("defaultText").style.display = "none";
    document.getElementById("filePreview").style.display = "flex";
    document.getElementById("removeBtn").style.display = "block";
}
