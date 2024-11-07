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


document.getElementById("notify").onclick = function () {
    $('#notify-candidate').unbind('submit').bind('submit', function (event) {
        event.preventDefault();

        $("#notify").prop("disabled", true);

        dataObj = {
            'notify': $('#notify').val(),
            'cid': candidate_code,
        }

        var final_data = {
            'data': JSON.stringify(dataObj),
            csrfmiddlewaretoken: CSRF_TOKEN,
        }

        $.post(CONFIG['portal'] + "/api/notify-candidate", final_data, function (res) {

            if (res.statusCode == 0) {

                Swal.fire({
                    position: 'center',
                    icon: 'success',
                    title: 'Canididate Notified',
                    showConfirmButton: false,
                    timer: 2000
                })

                setTimeout(function () { window.location.reload();}, 2000);


            } else {
                Swal.fire({
                    position: 'center',
                    icon: 'error',
                    title: 'Error in notifying the Canidate',
                    text: 'Please try again after some time',
                    showConfirmButton: false,
                    timer: 1500
                })

                $("#notify").prop("disabled", false);
            }
        })

    })
}
