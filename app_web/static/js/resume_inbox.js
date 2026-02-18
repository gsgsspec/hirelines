let selectedSources = new Set();

attachResumeRowClick();

function base64ToBlob(base64) {
    const byteCharacters = atob(base64.split(',')[1]);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
        byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: 'application/pdf' });
}

function attachResumeRowClick() {

    document.querySelectorAll(".resume-row").forEach(row => {
        row.addEventListener("click", async function () {

            const isAlreadyActive = this.classList.contains("active-row");

            if(isAlreadyActive){

                this.classList.remove("active-row");

                document.getElementById("resumePreview").style.display = "none";
                document.querySelector('.table-ctn').classList.remove('half-width');

                return;
            }

            document.querySelectorAll(".resume-row").forEach(r => {
                r.classList.remove("active-row");
            });

            this.classList.add("active-row");
            
            const id = this.getAttribute("data-id");
            const status = this.getAttribute("data-status");
    
            const response = await fetch(`/api/get-gmail-resume/${id}`);
            const data = await response.json();
    
            const pdfBlob = base64ToBlob(data.pdf_data);
            const pdfUrl = URL.createObjectURL(pdfBlob);
            const encodedUrl = encodeURIComponent(pdfUrl);
    
            document.getElementById("resumeIframe").src =
                `/static/pdfjs/web/viewer.html?file=${encodedUrl}`;
    
            document.getElementById("resumePreview").style.display = "block";
            document.querySelector('.table-ctn').classList.add('half-width');

    
            document.getElementById("delete-resume-btn").setAttribute("data-id", id);
            document.getElementById("add-profile-btn").setAttribute("data-id", id);

            if (status === "A") {
                document.getElementById("add-profile-btn").style.display = "none";
            } else {
                document.getElementById("add-profile-btn").style.display = "inline-block";
            }
            // 🔥 Load existing tags
            const tagResponse = await fetch(`${CONFIG['portal']}/api/get-resume-tags/${id}`);

            const tagData = await tagResponse.json();

            // Clear old tags
            $("#resume-tags").html("");

            // Add tags to preview
            tagData.tags.forEach(tag => {
                addTagToUI(tag);
            });

            
        });
    });
}

document.getElementById("delete-resume-btn").addEventListener("click", function () {
    const resumeId = this.getAttribute("data-id");

    Swal.fire({
        title: 'Are you sure?',
        text: `You want to delete this resume`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#ff3e1d',
        cancelButtonColor: '#274699',
        confirmButtonText: 'Yes, Delete'
    }).then((result) => {
        if (result.isConfirmed) {

            dataObj = {
                "resume_id": resumeId
            }

            var final_data = {
                'data': JSON.stringify(dataObj),
                csrfmiddlewaretoken: CSRF_TOKEN,
            }

            $.post(CONFIG['portal'] + "/api/delete-resume", final_data, function (res) {
                
                const row = document.querySelector(`tr.resume-row[data-id="${resumeId}"]`);
                if (row) {
                    row.remove();
                }

                document.getElementById("resumePreview").style.display = "none";
                document.querySelector('.table-ctn').classList.remove('half-width');
 
            })
        }
    });
});

document.getElementById("add-profile-btn").addEventListener("click", function () {
    const resumeId = this.getAttribute("data-id");

    dataObj = {
        "resume_id": resumeId
    }

    var final_data = {
        'data': JSON.stringify(dataObj),
        csrfmiddlewaretoken: CSRF_TOKEN,
    }

    $.post(CONFIG['portal'] + "/api/add-resume-profile", final_data, function (res) {
        if (res.statusCode == 0) {

            window.location.href = "/update-profile-data/"+ res.data.profile_id

        }
    
    })
});

document.addEventListener("DOMContentLoaded", function () {

    const items = document.querySelectorAll(".sources-item");
    
    items.forEach(item => {
        item.addEventListener("click", function () {
            const sourceId = this.dataset.sourceid;

            // Toggle selection
            if (selectedSources.has(sourceId)) {
                selectedSources.delete(sourceId);
                this.classList.remove("selected");
            } else {
                selectedSources.add(sourceId);
                this.classList.add("selected");
            }

            reloadResumesWithCurrentFilters();
            
        });
    });
});

function updateResumeTable(resumes){

    $('#resume-table').DataTable().destroy();

    let tbody = document.querySelector("#resume-table tbody");

    tbody.innerHTML = "";

    if (!resumes || resumes.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="3" class="text-center">No resumes found</td>
            </tr>
        `;
        return;
    }


    resumes.forEach(r => {

        let status = "-"

        if(r.status === "A"){
            status = "Added to Profile"
        }else if(r.status === "P"){
            status = "Review Pending"
        }else if(r.status === "D"){
            status = "Deleted"
        }

        let row = `
            <tr class="resume-row" data-id="${r.id}" data-status="${r.status}" style="cursor: pointer;">
                <td>${r.source}</td>
                <td>${r.name}</td>
                <td>${r.date}</td>
                <td>${status}</td>
                <td style="display:none;">${r.tags || ""}</td>
            </tr>
        `;
        tbody.insertAdjacentHTML("beforeend", row);
    });

    $('#resume-table').DataTable({
        "pageLength": 50,
        "lengthMenu": [10, 25, 50 , 100],
        "order": [],
        "ordering": true,
        columnDefs: [
            {
                targets: 4,
                visible: false,
                searchable: true
            }
        ],
        language: { search: "", searchPlaceholder: "Search..." },
        pagingType: 'simple_numbers'
    });
}

function syncClickHandler() {
    const btn = $("#sync-btn");
    const icon = btn.find("i");

    btn.prop("disabled", true);
    icon.addClass("fa-spin");

    $.get("/api/get-mail-resumes", function(response) {

        if(response.statusCode === 0){

            reloadResumesWithCurrentFilters();

            // let dataObj = { source_ids: [] };
    
            // let final_data = {
            //     data: JSON.stringify(dataObj),
            //     csrfmiddlewaretoken: CSRF_TOKEN
            // };
    
            // $.post(CONFIG['portal'] + "/api/get-filter-resume", final_data, function (res) {
            //     updateResumeTable(res.data);
            //     attachResumeRowClick();
            //     document.getElementById("resumePreview").style.display = "none";
            //     document.querySelector('.table-ctn').classList.remove('half-width');
            //     $(".sources-item").removeClass("selected");

            // });
    
            btn.html(`<i class="fas fa-check"></i> &nbsp; Synced Successfully`);
    
            btn.prop("disabled", true);
        } else {

            Swal.fire({
                position: 'center',
                icon: 'error',
                title: 'Error in syncing with email',
                text: 'Please try again after some time',
                showConfirmButton: false,
                timer: 1500
            })

            btn.html(`<i class="fas fa-times-circle text-danger"></i> &nbsp; Failed`);

        }


    })
    .fail(function () {
        Swal.fire({
            position: 'center',
            icon: 'error',
            title: 'Error in syncing with email',
            text: 'Please try again after some time',
            showConfirmButton: false,
            timer: 1500
        })

        btn.html(`<i class="fas fa-times-circle text-danger"></i> &nbsp; Failed`);
    })
    
}

$("#sync-btn").one("click", syncClickHandler);


function reloadResumesWithCurrentFilters() {
    const selectedArray = Array.from(selectedSources);

    let dataObj = {
        source_ids: selectedArray
    };

    let final_data = {
        data: JSON.stringify(dataObj),
        csrfmiddlewaretoken: CSRF_TOKEN
    };

    $.post(CONFIG['portal'] + "/api/get-filter-resume", final_data, function (res) {
        updateResumeTable(res.data);
        attachResumeRowClick();

        // Reset preview UI
        document.getElementById("resumePreview").style.display = "none";
        document.querySelector('.table-ctn').classList.remove('half-width');

        // Restore selected filter UI
        document.querySelectorAll(".sources-item").forEach(item => {
            if (selectedSources.has(item.dataset.sourceid)) {
                item.classList.add("selected");
            }
        });
    });
}

document.getElementById("close-resume-preview-btn").addEventListener("click", function () {

    // Hide preview
    document.getElementById("resumePreview").style.display = "none";
    document.querySelector('.table-ctn').classList.remove('half-width');

    // Remove active row highlight
    document.querySelectorAll(".resume-row").forEach(row => {
        row.classList.remove("active-row");
    });

    // Clear iframe src (optional but recommended)
    document.getElementById("resumeIframe").src = "";
});


document.getElementById("addResumeBtn")?.addEventListener("click", function () {

    const form = document.getElementById('addResumeForm');

    if (!form.checkValidity()) {
        form.reportValidity();
        return;
    }

    $("#addResumeBtn").prop("disabled", true);
        $("#addResumeBtn").html('Please wait &nbsp; <i class="fas fa-circle-notch fa-spin"></i>');

    dataObjs = {
        'source': $('#r-source').val(),
    }

    var formData = new FormData();

    formData.append("data", JSON.stringify(dataObjs));
    formData.append("csrfmiddlewaretoken", CSRF_TOKEN);

    if (!selectedFile) {
        Swal.fire({
            icon: "warning",
            title: "Please attach resume",
            text: "Resume file is required.",
            confirmButtonColor: '#274699'
        });

        $("#addResumeBtn").prop("disabled", false);
        $("#addResumeBtn").html('Save');
        return false; 
    }

    formData.append("resumefile", selectedFile);

    $.ajax({
        url: CONFIG['portal'] + "/api/add-resume",
        type: "POST",
        data: formData,
        processData: false,
        contentType: false,
        success: function (res) {
            if (res.statusCode == 0) {

                Swal.fire({
                    icon: "success",
                    title: "Resume added",
                    text: "The resume was added successfully!",
                    timer: 1500,
                    showConfirmButton: false
                });

                reloadResumesWithCurrentFilters();

                $("#addResumeBtn").prop("disabled", false);
                $("#addResumeBtn").html('Save');

                const modalEl = document.getElementById('modalScrollable');
                const modalInstance = bootstrap.Modal.getInstance(modalEl);

                if (modalInstance) {
                    modalInstance.hide();
                }

                resetAddResumeForm()


            }else {
                $("#addResumeBtn").prop("disabled", false);
                $("#addResumeBtn").html('Save');

                Swal.fire(
                    "Error",
                    "Unable to add resume",
                    "error"
                );
            }
        }
    });


})




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


function resetAddResumeForm() {

    const form = document.getElementById('addResumeForm');
    form.reset(); // resets select + native inputs

    // Reset file input
    const fileInput = document.getElementById('resumeInput');
    fileInput.value = '';

    // Reset custom variables
    selectedFile = null;

    // Reset upload UI
    document.getElementById('filePreview').style.display = 'none';
    document.getElementById('defaultText').style.display = 'block';
    document.getElementById('fileName').innerText = '';
    document.getElementById('fileIcon').src = '';

    // Hide remove button
    document.getElementById('removeBtn').style.display = 'none';

    // Remove error styles if any
    document.getElementById('uploadBox').classList.remove('error');
}


function addTagToUI(tagName) {
    let tagHtml = `
        <span class="tag-badge">
            ${tagName}
            <span class="remove-tag">&times;</span>
        </span>
    `;
    $("#resume-tags").append(tagHtml);
}
function loadResumeTags(resumeId) {

    fetch(`${CONFIG['portal']}/api/get-resume-tags/${resumeId}`)
        .then(res => res.json())
        .then(data => {

            $("#resume-tags").html("");

            data.tags.forEach(tag => {
                addTagToUI(tag);
            });

        });
}


function normalizeTag(tag) {
    return tag
        .toLowerCase()
        .replace(/\s+/g, "")   
        .trim();
}

function tagExists(tagName) {

    let normalizedInput = normalizeTag(tagName);
    let exists = false;

    $(".tag-badge").each(function () {

        let text = $(this)
            .clone()
            .children()
            .remove()
            .end()
            .text()
            .trim();

        let normalizedExisting = normalizeTag(text);

        if (normalizedExisting === normalizedInput) {
            exists = true;
        }
    });

    return exists;
}



$("#resume-tags-input").on("input", function () {

    let currentVal = $(this).val().trim();

    if (!currentVal) {
        $("#tag-info-msg").hide();
        $(this).removeClass("is-invalid");
        return;
    }

    if (tagExists(currentVal)) {
        $("#tag-info-msg").show();
        $(this).addClass("is-invalid");
    } else {
        $("#tag-info-msg").hide();
        $(this).removeClass("is-invalid");
    }
});




$("#save-tagsdata").on("click", function () {

    let inputVal = $("#resume-tags-input").val().trim();
    if (!inputVal) return;

    // let tagParts = inputVal.split(",");
    // let tags = tagParts.map(t => t.trim()).filter(t => t !== "");
    let tagParts = inputVal.split(",");
    let tags = [];

    for (let part of tagParts) {

        let cleaned = part.trim();
        if (!cleaned) continue;

        if (tagExists(cleaned)) {
            Swal.fire({
                icon: "warning",
                title: "Duplicate Tag",
                text: `"${cleaned}" is already added`
            });
            return;
        }

        tags.push(cleaned);
    }

    let activeRow = $(".resume-row.active-row");

    if (!activeRow.length) {
        Swal.fire("Select a resume first");
        return;
    }

    let resumeId = activeRow.data("id");

    let dataObj = {
        resume_id: resumeId,
        tags: tags
    };

    $.post(CONFIG['portal'] + "/api/save-resume-tags", {
        data: JSON.stringify(dataObj),
        csrfmiddlewaretoken: CSRF_TOKEN
    }, function (res) {

        if (res.statusCode === 0) {

            Swal.fire({
                icon: "success",
                title: "Tags saved",
                timer: 1200,
                showConfirmButton: false
            });

          
            $("#resume-tags-input").val("");

            $('#close-resume-preview-btn').click();
            reloadResumesWithCurrentFilters();
            loadResumeTags(resumeId);
        }

    });
});
$("#resume-tags-input").on("keypress", function(e) {
        if (e.which === 13) {
            e.preventDefault();
            $("#save-tagsdata").click();
        }
});

$(document).on("click", ".remove-tag", function (e) {

    e.stopPropagation();

    let tagBadge = $(this).parent();
    let tagText = tagBadge.clone().children().remove().end().text().trim();

    let activeRow = $(".resume-row.active-row");

    if (!activeRow.length) {
        Swal.fire({
            icon: "warning",
            title: "Select a resume first"
        });
        return;
    }

    let resumeId = activeRow.data("id");



    $.ajax({
        url: CONFIG['portal'] + "/api/delete-tags",
        type: "POST",
        contentType: "application/json",
        data: JSON.stringify({
            resume_id: resumeId,
            tag: tagText
        }),
        headers: { "X-CSRFToken": CSRF_TOKEN },
        success: function (res) {
            if (res.statusCode === 0) {

                tagBadge.remove();

                Swal.fire({
                    icon: "success",
                    title: "Deleted successfully",
                    timer: 1200,
                    showConfirmButton: false
                });

            } else {
                Swal.fire("Delete failed");
            }
        },
        error: function () {
            Swal.fire("Something went wrong");
        }
    });

});
