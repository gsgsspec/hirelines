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
