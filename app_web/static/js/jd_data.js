function showFullPage() {
    $('#layout-menu').css('display', '')
    $('#web-page').addClass('layout-menu-fixed')
    $('#display_icon').css('display', 'none')
    $('#hide_icon').css('display', 'block')
}


function hideFullPage() {
    $('#layout-menu').css('display', 'none')
    $('#web-page').removeClass('layout-menu-fixed')
    $('#display_icon').css('display', 'block')
    $('#hide_icon').css('display', 'none')
}

if (window.innerWidth > 900) {
    $('#layout-menu').css('display', 'none');
}

$('#web-page').removeClass('layout-menu-fixed')


async function getReportData(cid) {
    var url = CONFIG['acert'] + "/api/hireline-candidate-report";

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
            a.download = 'report.pdf';
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
