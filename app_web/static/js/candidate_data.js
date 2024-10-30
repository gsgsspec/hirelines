async function getReportData(cid) {
    
    var url = CONFIG['portal'] + "/api/get-candidate-report";

    if (cid) {
        url += "?cid=" + cid;
    }

    try {
        Swal.fire({
            title: 'Downloading',
            text: 'Please wait while your report is being downloaded...',
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading();
            }
        });

        const response = await fetch(url, { method: 'GET' });

        if (response.ok) {
            const blob = await response.blob();
            const downloadUrl = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = downloadUrl;
            a.download = cid + '.pdf';
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