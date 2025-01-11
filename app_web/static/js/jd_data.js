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


document.addEventListener("DOMContentLoaded", function() {
    const positionedNumbers = document.querySelectorAll('.positioned-number');

    positionedNumbers.forEach(span => {
        const numberLength = span.textContent.length; // Get the length of the number

        // Adjust the left position based on the number of digits
        const leftPosition = 33 - (numberLength - 1); // Decrease left by 1% for each additional digit
        span.style.left = leftPosition + '%'; // Set the calculated left position
    });
});

if (screening_count === 0 && coding_count === 0 && interview_count === 0 && offer_count === 0) {
    // Show the "No candidates registered" message
    document.getElementById('noCandidatesMessage').style.display = 'block';
    document.getElementById('funnelChartContainer').style.display = 'none';
} else {

    window.onload = function () {
        var chart = new CanvasJS.Chart("funnelChartContainer", {
          animationEnabled: true,
          theme: "light2",
          backgroundColor: "#f4f6f9",  // Light background color for contrast
          data: [{
            type: "funnel",
            indexLabelFontSize: 20,
            toolTipContent: "<b>{label}</b>: {y} candidates",
            indexLabel: "{y}",
            indexLabelPlacement: "inside", // Centers labels
            indexLabelFontColor: "white",  // White font for contrast in each layer
            neckWidth: "20%",  // Narrow neck for the funnel shape
            neckHeight: "30%", // Tall neck to emphasize the funnel shape
            valueRepresents: "area",
            // showInLegend: true,
            // legendText: "{label}",
            dataPoints: [
              { y: screening_count, label: "Screening", color: "#17b0e3" },
              { y: coding_count, label: "Coding", color: "#3bc482" },
              { y: interview_count, label: "Interview", color: "#93c131" },
              { y: offer_count, label: "Offer Letter", color: "#e3cd09" }
            ]
          }]
        });
        chart.render();
    }
}


$('#dashboard-display').on('change', function() {
    var isChecked = $(this).prop('checked');

    var status = isChecked ? 'Y' : 'N';

    dataObjs = {
        'dashboard-display':status,
        'jobid':jobId
    }

    var final_data = {
        'data': JSON.stringify(dataObjs),
        csrfmiddlewaretoken: CSRF_TOKEN,
    }

    $.post(CONFIG['portal'] + "/api/display-dashboardflag", final_data, function (res) {
     
    })

})