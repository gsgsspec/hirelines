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
    let selectedSources = new Set();

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

            // Convert Set to Array
            const selectedArray = Array.from(selectedSources);

            dataObj = {
                "source_ids": selectedArray
            }

            var final_data = {
                'data': JSON.stringify(dataObj),
                csrfmiddlewaretoken: CSRF_TOKEN,
            }

            $.post(CONFIG['portal'] + "/api/get-filter-resume", final_data, function (res) {
                updateResumeTable(res.data);
                attachResumeRowClick();
                document.getElementById("resumePreview").style.display = "none";
                document.querySelector('.table-ctn').classList.remove('half-width');
 
                
            })
            
        });
    });
});

function updateResumeTable(resumes){

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
            </tr>
        `;
        tbody.insertAdjacentHTML("beforeend", row);
    });
}

function syncClickHandler() {
    const btn = $("#sync-btn");
    const icon = btn.find("i");

    btn.prop("disabled", true);
    icon.addClass("fa-spin");

    $.get("/api/get-mail-resumes", function(response) {

        if(response.statusCode === 0){

            let dataObj = { source_ids: [] };
    
            let final_data = {
                data: JSON.stringify(dataObj),
                csrfmiddlewaretoken: CSRF_TOKEN
            };
    
            $.post(CONFIG['portal'] + "/api/get-filter-resume", final_data, function (res) {
                updateResumeTable(res.data);
                attachResumeRowClick();
                document.getElementById("resumePreview").style.display = "none";
                document.querySelector('.table-ctn').classList.remove('half-width');

            });
    
            btn.html(`<i class="fas fa-check"></i> &nbsp; Synced Successfully`);
    
            btn.prop("disabled", false);
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