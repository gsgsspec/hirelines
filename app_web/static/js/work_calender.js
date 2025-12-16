

$(document).ready(function () {

    getWorkCal();


    function updateDeleteButtons() {
        let rows = $(".work-row");
        let count = rows.length;

        if (count <= 1) {
            rows.find(".deleteDbBtn, .removeBtn").hide();
        } else {
            rows.find(".deleteDbBtn, .removeBtn").show();
        }

        if (window.DB_RECORD_COUNT === 1) {
            $(".deleteDbBtn").hide();
        }
    }


    function getWorkCal() {

        let payload = {
            user_id: USER_ID,
            company_id: COMPANY_ID
        };

        $.post(
            CONFIG['portal'] + "/api/get-work-cal",
            {
                data: JSON.stringify(payload),
                csrfmiddlewaretoken: CSRF_TOKEN
            },
            function (res) {

                let container = $("#rowsContainer");
                container.empty();

                window.DB_RECORD_COUNT = res.data.length;

                if (res.statusCode === 0 && res.data.length > 0) {

                    res.data.forEach(item => {
                        container.append(buildRow(item));
                    });

                    container.append(buildWeekOffSection(
                        res.data[0].weekoff1,
                        res.data[0].weekoff2
                    ));

                    $("#saveBtn").text("Update");

                } else {

                    window.DB_RECORD_COUNT = 0;
                    container.append(buildRow(null));
                    container.append(buildWeekOffSection("", ""));
                    $("#saveBtn").text("Save");
                }

                updateDeleteButtons();
            }
        );
    }


    function buildRow(item) {

        let hasID = item !== null;
        let showDelete = hasID && !(window.DB_RECORD_COUNT === 1);
        let time = hasID && item.starttime ? item.starttime.split(":") : ["", "00"];

        return `
        <div class="row work-row mt-3" data-id="${hasID ? item.id : ''}">

            <div class="col-md-3">
                <label class="form-label">Start Day</label>
                <select class="form-select startDay">
                    <option value="">Select</option>
                    ${dayOptions(hasID ? item.startday : "")}
                </select>
            </div>

            <div class="col-md-3">
                <label class="form-label">Start Time (HH:MM)</label>
                <div class="d-flex gap-2">
                    <select class="form-control startHour">
                        ${hourOptions(time[0])}
                    </select>
                    <select class="form-control startMinute">
                        <option value="00" ${time[1] === "00" ? "selected" : ""}>00</option>
                        <option value="30" ${time[1] === "30" ? "selected" : ""}>30</option>
                    </select>
                </div>
            </div>

            <div class="col-md-3">
                <label class="form-label">Hours</label>
                <input type="number" class="form-control Hours" value="${hasID ? item.hours : ''}">
            </div>

            <div class="col-md-3 d-flex align-items-end">
                ${hasID
                ? `<button class="btn btn-danger deleteDbBtn" style="display:${showDelete ? 'inline-block' : 'none'}">Delete</button>`
                : `<button class="btn btn-danger removeBtn">Remove</button>`
            }
            </div>
        </div>`;
    }


    window.addRow = function () {

        let weekOffSection = $("#rowsContainer .weekoff-section");

        if (weekOffSection.length) {
            // insert row BEFORE weekoff section
            $(buildRow(null)).insertBefore(weekOffSection);
        } else {
            // fallback (first load)
            $("#rowsContainer").append(buildRow(null));
        }

        updateDeleteButtons();
    };

    function buildWeekOffSection(wo1, wo2) {

        return `
        <div class="row mt-4 weekoff-section">

            <div class="col-md-3">
                <label class="form-label">Week Off 1</label>
                <select class="form-select weekOff1">
                    <option value="">Select</option>
                    ${dayOptions(wo1)}
                </select>
            </div>

            <div class="col-md-3">
                <label class="form-label">Week Off 2</label>
                <select class="form-select weekOff2">
                    <option value="">Select</option>
                    ${dayOptions(wo2)}
                </select>
            </div>

        </div>`;
    }

    function dayOptions(selected) {
        const days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
        return days.map(d =>
            `<option value="${d}" ${d === selected ? "selected" : ""}>${d}</option>`
        ).join("");
    }

    function hourOptions(selectedHour) {
        let html = `<option value="">HH</option>`;
        for (let i = 0; i < 24; i++) {
            let h = String(i).padStart(2, "0");
            html += `<option value="${h}" ${h === selectedHour ? "selected" : ""}>${h}</option>`;
        }
        return html;
    }



    $(document).on("click", ".removeBtn", function () {
        $(this).closest(".work-row").remove();
        updateDeleteButtons();
    });


    function toMinutes(t) {
        let [h, m] = t.split(":");
        return (+h * 60) + (+m);
    }
    function exceeds24Hours(row) {

        let h = row.querySelector(".startHour").value;
        let m = row.querySelector(".startMinute").value;
        let hrs = row.querySelector(".Hours").value;

        if (!h || !m || hrs === "" || Number(hrs) <= 0) return false;

        let startMinutes = toMinutes(`${h}:${m}`);
        let endMinutes = startMinutes + (Number(hrs) * 60);

        return endMinutes > 1440; // 24 * 60
    }
    function hasConflict(row) {

        let day = row.querySelector(".startDay").value;
        let h = row.querySelector(".startHour").value;
        let m = row.querySelector(".startMinute").value;
        let hrs = row.querySelector(".Hours").value;

        if (!day || !h || !m || hrs === "" || Number(hrs) <= 0) return false;

        let start = toMinutes(`${h}:${m}`);
        let end = start + (Number(hrs) * 60);

        let conflict = false;

        document.querySelectorAll(".work-row").forEach(r => {

            if (r === row) return;

            let d = r.querySelector(".startDay").value;
            let hh = r.querySelector(".startHour").value;
            let mm = r.querySelector(".startMinute").value;
            let hhrs = r.querySelector(".Hours").value;

            if (!d || !hh || !mm || hhrs === "" || Number(hhrs) <= 0) return;
            if (d !== day) return;

            let s = toMinutes(`${hh}:${mm}`);
            let e = s + (Number(hhrs) * 60);

            if (start < e && s < end) {
                conflict = true;
            }
        });

        return conflict;
    }


    $(document).on(
        "input change",
        ".startDay, .startHour, .startMinute, .Hours",
        function () {
            let row = this.closest(".work-row");
            delete row.dataset.conflict;
        }
    );

    $(document).on(
        "input change",
        ".startDay, .startHour, .startMinute, .Hours",
        function () {

            let row = this.closest(".work-row");

            if (row.dataset.conflict === "1") return;

            if (exceeds24Hours(row)) {

                Swal.fire({
                    icon: "warning",
                    title: "Invalid Duration",
                    text: "Hours cannot exceed 24 hours from the selected start time.",
                    confirmButtonText: 'OK',
                    confirmButtonColor: '#274699'
                });

                row.querySelector(".Hours").value = "";
                return;
            }

            if (hasConflict(row)) {

                row.dataset.conflict = "1";

                Swal.fire({
                    icon: "warning",
                    title: "Time Conflict",
                    text: "This time overlaps with an existing schedule for the same day.",
                    confirmButtonText: 'OK',
                    confirmButtonColor: '#274699'
                });

                row.querySelector(".startHour").value = "";
                row.querySelector(".startMinute").value = "00";
                row.querySelector(".Hours").value = "";
            }
        }
    );

    $(document).on("click", ".deleteDbBtn", function () {

        if ($(".work-row").length <= 1) {
            Swal.fire("Not Allowed!", "At least one record must remain.", "info");
            return;
        }

        let row = $(this).closest(".work-row");
        let id = row.attr("data-id");
        Swal.fire({
            title: "Are you sure?",
            text: "This will permanently delete the record!",
            icon: "warning",
            showCancelButton: true,
            confirmButtonColor: '#ff3e1d',
            confirmButtonText: "Yes, delete!"
        }).then((res) => {
            if (res.isConfirmed) {

                $.post(
                    CONFIG['portal'] + "/api/delete-work-cal/" + id,
                    { csrfmiddlewaretoken: CSRF_TOKEN }
                ).done(function (data) {

                    if (data.statusCode === 0) {
                        Swal.fire("Deleted!", "", "success");
                        row.remove();
                        window.DB_RECORD_COUNT--;
                        updateDeleteButtons();
                    } else {
                        Swal.fire("Failed!", data.error || "Delete failed", "error");
                    }
                });
            }
        });
    });





    $("#saveBtn").click(function () {

        let rows = document.querySelectorAll(".work-row");
        let list = [];

        let weekoff1 = document.querySelector(".weekOff1").value;
        let weekoff2 = document.querySelector(".weekOff2").value;

        let isValid = true;
        let errorMsg = "";

        rows.forEach((row, index) => {

            let day = row.querySelector(".startDay").value;
            let hour = row.querySelector(".startHour").value;
            let minute = row.querySelector(".startMinute").value;
            let hours = row.querySelector(".Hours").value;

            
            if (!day || !hour || !minute || hours === "" || Number(hours) <= 0) {
                isValid = false;
                errorMsg = `Please fill all required fields in row ${index + 1}`;
                return false;
            }

            list.push({
                id: row.dataset.id || null,
                startday: day,
                starttime: `${hour}:${minute}`,
                hours: hours,
                weekoff1: weekoff1,
                weekoff2: weekoff2
            });
        });

        if (!isValid) {
            Swal.fire({
                icon: "warning",
                title: "Missing Feild Details",
                text: errorMsg,
                confirmButtonText: 'OK',
                confirmButtonColor: '#274699'
            });
            return;
        }

        
        $.post(
            CONFIG['portal'] + "/api/save-work-cal",
            {
                data: JSON.stringify({
                    userid: USER_ID,
                    companyid: COMPANY_ID,
                    items: list
                }),
                csrfmiddlewaretoken: CSRF_TOKEN
            },
            function (res) {
                if (res.statusCode === 0) {
                    Swal.fire("Saved!", "", "success");
                    getWorkCal();
                } else {
                    Swal.fire("Error!", res.error || "Unknown error", "error");
                }
            }
        );
    });


    $("#cancelBtn").click(function () {
        location.reload();
    });

});


