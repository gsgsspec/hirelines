function tabSwitch(element) {

    if (element === 'active') {
        $('#active').addClass('activeTab shadow');
        $('#Inactive').removeClass('activeTab shadow');
        window.location.href = "/profileview/" + pid;
    }

    if (element === 'Inactive') {
        $('#Inactive').addClass('activeTab shadow');
        $('#active').removeClass('activeTab shadow');
        window.location.href = "/profileactivity/" + pid;
    }
}

async function downloadResume(pid) {

    var url = CONFIG['portal'] + "/api/download-branded-profile";

    try {
        Swal.fire({
            title: 'Downloading',
            text: 'Please wait while your profile is being downloaded...',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });

        const formData = new FormData();
        formData.append("pid", pid);
        formData.append("csrfmiddlewaretoken", CSRF_TOKEN);

        const response = await fetch(url, {
            method: "POST",
            body:formData
        });

        if (response.ok) {
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            
            let filename = "download.pdf";

            const disposition = response.headers.get("Content-Disposition");
            if (disposition) {
                filename = disposition.split("filename=")[1]?.replace(/"/g, "") || filename;
            }

            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(downloadUrl);
        } else {
            console.error('Request failed', response.status);
        }
    } catch (error) {
        console.error('Error:', error);
    } finally {
        Swal.close();
    }
}

function confirmPrefill(profileId, docParserId) {
    Swal.fire({
        icon: "warning",
        title: "Warning",
        text: "Any manually entered data will be lost. Do you want to continue?",
        showCancelButton: true,
        confirmButtonText: "Yes, continue",
        cancelButtonText: "Cancel"
    }).then((result) => {
        if (result.isConfirmed) {
            // User confirmed, call the original prefill function
            requestprefill(profileId, docParserId);
        }
    });
}
function requestprefill(pid, doc_parser_id) {
    var getPrefillDocParserDataUrl = CONFIG['docparser'] + "/api/request-prefill";
    var autoFillUrl = CONFIG['portal'] + "/api/auto-fill-profile";

    $.ajax({
        url: getPrefillDocParserDataUrl,
        type: "POST",
        data: {
            doc_parser_id: doc_parser_id,
            csrfmiddlewaretoken: CSRF_TOKEN
        },
        success: function(res) {
            // ---------------- Handle first API response ----------------
            if (!res || res.statusCode !== 0) {
                Swal.fire({
                    icon: "error",
                    title: "Prefill Request Failed",
                    text: res?.error || "Unknown error"
                });
                return;
            }

            // If document is not ready
            if (res.message && res.message.toLowerCase().includes("document not ready")) {
                Swal.fire({
                    icon: "info",
                    title: "Document Not Ready",
                    text: res.message
                });
                return;
            }

            // If valid JSON received
            if (res.data) {
                var dataObj = res.data;
                dataObj['profileid'] = pid; // append profileid

                // ---------------- Call auto-fill-profile ----------------
                $.ajax({
                    url: autoFillUrl,
                    type: "POST",
                    data: {
                        data: JSON.stringify(dataObj),
                        csrfmiddlewaretoken: CSRF_TOKEN
                    },
                    success: function(autoRes) {
                       if (autoRes.statusCode === 0) {
                            Swal.fire({
                                icon: "success",
                                title: "Profile Auto-filled",
                                text: "Profile has been updated successfully!"
                            }).then(() => {
                                // Refresh the page after user closes the alert
                                location.reload();
                            });
                        } else {
                            Swal.fire({
                                icon: "error",
                                title: "Auto-fill Failed",
                                text: autoRes.error || "Unknown error"
                            });
                        }
                    },
                    error: function(xhr, status, error) {
                        Swal.fire({
                            icon: "error",
                            title: "Auto-fill Request Failed",
                            text: error
                        });
                    }
                });
            }
        },
        error: function(xhr, status, error) {
            Swal.fire({
                icon: "error",
                title: "Prefill Request Failed",
                text: error
            });
        }
    });
}
