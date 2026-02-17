function redirectToJobDetails(redirectId) {
    window.location.href = '/job-description-set-up/' + redirectId;
}

function redirectToJobDashboard(jid) {
    window.location.href = '/jd/' + jid;
}

function tabSwitch(element) {
    if (element === 'active') {
        $('#active').addClass('activeTab shadow');  // Added both classes with space
        $('#Inactive').removeClass('activeTab shadow');  // Removed both classes with space
        $("#activeJdsContainer").fadeIn("slow");
        $("#InactiveJdsContainer").fadeOut("slow").hide(); // Ensures #InactiveJdsContainer is hidden after fading out
    }

    if (element === 'Inactive') {
        $('#Inactive').addClass('activeTab shadow');  // Added both classes with space
        $('#active').removeClass('activeTab shadow');  // Removed both classes with space
        $("#activeJdsContainer").fadeOut("slow");
        $("#InactiveJdsContainer").fadeIn("slow").show(); // Ensures #InactiveJdsContainer is shown after fading in
    }
}


document.addEventListener("DOMContentLoaded", function () {

    const publishBtn = document.getElementById("publishBtn");
    const checkboxes = document.querySelectorAll(".jd-checkbox");
    const noActiveMsg = document.getElementById("noActiveMsg");

    document.getElementById("copyCareerUrlBtn").addEventListener("click", function () {
        const input = document.getElementById("careerUrlInput");
        navigator.clipboard.writeText(input.value);

        const msg = document.getElementById("copyMsg");
        msg.style.display = "inline";
        setTimeout(() => msg.style.display = "none", 1200);
    });


    // If no active JD checkboxes exist
    if (checkboxes.length === 0) {
        publishBtn.disabled = true;
        noActiveMsg.style.display = "block";
        return;
    }

    publishBtn.addEventListener("click", function () {

        const selected = [];
        checkboxes.forEach(cb => {
            if (cb.checked) selected.push(cb.value);
        });

        publishSelectedJobs(selected);

    });

});

// ✅ Your function
function publishSelectedJobs(selectedJobIds) {
    console.log("Publishing these JD IDs:", selectedJobIds);

    dataObjs = {
        'job_ids': selectedJobIds,
    }

    var final_data = {
        'data': JSON.stringify(dataObjs),
        csrfmiddlewaretoken: CSRF_TOKEN,
    }

    $.post(CONFIG['portal'] + "/api/publish-career-jds", final_data, function (res) {

        if (res.statusCode == 0) {
            Swal.fire({
                position: 'center',
                icon: 'success',
                title: 'Career Jobs updated',
                showConfirmButton: false,
                timer: 2000
            })
        }
        else {
            Swal.fire({
                position: 'center',
                icon: 'error',
                title: 'Error in Updating career jobs',
                text: 'Please try again after some time',
                showConfirmButton: false,
                timer: 2000
            })

        }
    }).fail(function (xhr, status, error) {

        Swal.fire({
            position: 'center',
            icon: 'error',
            title: 'Request Failed',
            text: 'Network/server issue. Please try again.',
            showConfirmButton: false,
            timer: 2000
        });
    })

}