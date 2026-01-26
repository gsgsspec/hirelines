document.addEventListener("click", function (event) {
    const card = event.target.closest(".wrk-jd-card");
    if (!card) return;

    const jdid = card.dataset.jdid;

    document.querySelectorAll(".wrk-jd-card").forEach(c => {
        c.classList.remove("active");
    });

    card.classList.add("active");

    dataObjs = {
        'jdid':  jdid
    }

    var final_data = {
        'data': JSON.stringify(dataObjs),
        csrfmiddlewaretoken: CSRF_TOKEN,
    }

    $.post(CONFIG['portal'] + "/api/jd-profile-data", final_data, function (res) {

        renderJDDetails(res.data);

    })

});


function renderJDDetails(data) {

    let html = `
        <h4 class="mb-3 p-clr">${data.title}
            <small>(${data.expmin} - ${data.expmax} yrs)</small>
        </h4>

        <div class="mb-3">Primary Skills : ${data.jd_skills_primary}</div>

        <div class="nav-align-top nav-tabs-shadow">
            <ul class="nav nav-tabs nav-fill" role="tablist">
                <li class="nav-item">
                    <button class="nav-link active" data-bs-toggle="tab" data-bs-target="#tab-shortlisted">
                        Shortlisted (${data.shortlisted_profiles.length})
                    </button>
                </li>
                <li class="nav-item">
                    <button class="nav-link" data-bs-toggle="tab" data-bs-target="#tab-matched">
                        Find Matching Profiles (${data.matched_profiles.length})
                    </button>
                </li>
            </ul>

            <div class="tab-content">
                <div class="tab-pane fade show active" id="tab-shortlisted">
                    ${renderShortlistedTable(data.shortlisted_profiles,data.jdid)}
                </div>

                <div class="tab-pane fade" id="tab-matched">
                    ${renderMatchedTable(data.matched_profiles,data.jdid)}
                </div>
            </div>
        </div>
    `;

    $("#jd-details-container").html(html);

    // Call this AFTER you inject/render the HTML
    const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
    );

    tooltipTriggerList.forEach(function (tooltipTriggerEl) {
    new bootstrap.Tooltip(tooltipTriggerEl);
    });

}


function renderShortlistedTable(list) {

    if (!list || list.length === 0) {
        return `<p class="text-muted">No shortlisted profiles</p>`;
    }

    let rows = "";

    list.forEach((p, index) => {
        const fullname = [p.firstname, p.middlename, p.lastname]
            .filter(Boolean)
            .join(" ");

        rows += `
            <tr>
                <td>${fullname || "-"}</td>
                <td>${p.email || "-"}</td>
                <td>${p.candidate_status}</td>
            </tr>
        `;
    });

    return `
        <table class="table">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody class="table-border-bottom-0">${rows}</tbody>
        </table>
    `;
}


function renderMatchedTable(list,jdid) {

    if (!list || list.length === 0) {
        return `<p class="text-muted">No matched profiles found</p>`;
    }

    let rows = "";

    list.forEach((p, index) => {
        const fullname = [p.firstname, p.middlename, p.lastname]
            .filter(Boolean)
            .join(" ");

        let strength_class = "";

        if (p.overall_strength >= 80) {
            strength_class = "high";
        } else if (p.overall_strength >= 50 && p.overall_strength <= 79) {
            strength_class = "medium";
        } else {
            strength_class = "low";
        }


        rows += `
            <tr>
                <td>${fullname}</td>
                <td>${p.email}</td>
                <td>${p.profile_strength}%</td>
                <td class="${strength_class}">${p.overall_strength}%
                    <i class='bx bx-info-circle' data-bs-toggle="tooltip" data-bs-offset="0,6" data-bs-placement="top" data-bs-html="true" style="color: var(--primary-color);cursor: pointer;"
                        data-bs-original-title="<span>Experience : ${p.exp_math_strength}</span> <br> <span> Skills : ${p.skill_math_strength}</span>"></i>
                </td>
                <td>${p.total_experience} Yrs -  ${p.exp_strength}%</td>
                <td>${p.skill_strength}% <i class='bx bx-info-circle' data-bs-toggle="tooltip" data-bs-offset="0,6" data-bs-placement="top" data-bs-html="true" style="color: var(--primary-color);cursor: pointer;"
                        data-bs-original-title="
                            <div>
                                <strong>Matched Skills:</strong><br>
                                <span style='color: #28a745;'>${p.matched_skills || 'None'}</span><br>
                                <strong>Not Matched Skills:</strong><br>
                                <span style='color: #dc3545;'>${p.not_matched_skills || 'None'}</span>
                            </div>
                    "></i>
                </td>
                <td>
                    <button class="btn-primary btn btn-sm shortlist-btn" data-profile-id="${p.id}" data-jdid="${jdid}">Shortlist</button>
                </td>
            </tr>
        `;
    });

    return `
        <table class="table">
            <thead>
                <tr>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Profile Strength</th>
                    <th>Matching Score</th>
                    <th>Experience</th>
                    <th>Skill</th>
                    <th></th>
                </tr>
            </thead>
            <tbody class="table-border-bottom-0">${rows}</tbody>
        </table>
    `;
}


$(document).on("click", ".shortlist-btn", function () {

    $(this).prop("disabled", true);

    dataObjs = {
        "profile_id": $(this).data("profile-id"),
        "jdid": $(this).data("jdid"),
    }

    var final_data = {
        'data': JSON.stringify(dataObjs),
        csrfmiddlewaretoken: CSRF_TOKEN,
    }


    $.post(CONFIG['portal'] + "/api/shortlist-profile", final_data, function (res) {

        if (res.statusCode === 0) {
            var candidateData = res.data
            console.log("candidateData",candidateData);
            

            if (candidateData == "insufficient_credits") {

                Swal.fire({
                    position: 'center',
                    icon: 'error',
                    title: 'Insufficient Credits',
                    showConfirmButton: true,
                    confirmButtonText: 'OK',
                    confirmButtonColor: '#274699'
                })

                $(this).prop("disabled", false);

                return 
            }

            if (candidateData == "candidate_already_registered") {

                Swal.fire({
                    position: 'center',
                    icon: 'error',
                    title: 'Profile already shortlisted for this jd',
                    showConfirmButton: true,
                    confirmButtonText: 'OK',
                    confirmButtonColor: '#274699'
                })

                $(this).prop("disabled", false);

                return 
                
            }

            Swal.fire({
                position: 'center',
                icon: 'success',
                title: 'Profile shortlisted',
                showConfirmButton: false,
                timer: 1500,
                didClose: () => {
                location.reload();
            }
            })

            // Optional UX
            $(this).prop("disabled", true).text("Shortlisted");  
        } else {
            Swal.fire({
                position: 'center',
                icon: 'error',
                title: 'Error in shortlisting the profile',
                showConfirmButton: true,
                confirmButtonText: 'OK',
                confirmButtonColor: '#274699'
            })
            $(this).prop("disabled", false);
        }
    });
});
