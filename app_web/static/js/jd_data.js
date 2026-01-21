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

        const chart = echarts.init(document.getElementById('funnelChartContainer'));

        const stages = [
            { key: 'Screening', value: screening_count, color: '#17b0e3' },
            { key: 'Coding', value: coding_count, color: '#3bc482' },
            { key: 'Interview', value: interview_count, color: '#e3cd09' },
            { key: 'Offer Letter', value: offer_count, color: '#93c131' }
        ];

        const nonZeroStages = stages.filter(stage => stage.value > 0);

        if (nonZeroStages.length < 2) {
            chart.clear();
            chart.setOption({
                graphic: {
                    type: 'text',
                    left: 'center',
                    top: 'middle',
                    style: {
                        text: 'Not enough data to build funnel',
                        fill: '#999',
                        fontSize: 16,
                        fontWeight: 500
                    }
                }
            });
            return;
        }



        const funnelData = nonZeroStages.map(stage => ({
            name: stage.key,
            value: stage.value,
            itemStyle: { color: stage.color }
        }));


        if (!funnelData.length) {
            chart.clear();
            chart.showLoading({
                text: 'No data available',
                color: '#999'
            });
            return;
        }

        const option = {
            backgroundColor: '#f4f6f9',
            tooltip: {
                trigger: 'item',
                formatter: '<b>{b}</b>: {c} candidates'
            },
            series: [{
                type: 'funnel',
                top: 0,
                bottom: 0,
                width: '80%',
                minSize: funnelData.length === 1 ? '60%' : '20%', // 👈 better single block look
                maxSize: '100%',
                gap: 0,
                funnelAlign: 'center',
                sort: 'descending',

                label: {
                    show: true,
                    position: 'inside',
                    color: '#ffffff',
                    fontSize: 20,
                    formatter: '{c}'
                },

                itemStyle: {
                    borderWidth: 0
                },

                data: funnelData
            }]
        };

        chart.setOption(option);
    };




    // window.onload = function () {
    //     var chart = new CanvasJS.Chart("funnelChartContainer", {
    //       animationEnabled: true,
    //       theme: "light2",
    //       backgroundColor: "#f4f6f9",  // Light background color for contrast
    //       data: [{
    //         type: "funnel",
    //         indexLabelFontSize: 20,
    //         toolTipContent: "<b>{label}</b>: {y} candidates",
    //         indexLabel: "{y}",
    //         indexLabelPlacement: "inside", // Centers labels
    //         indexLabelFontColor: "white",  // White font for contrast in each layer
    //         neckWidth: "30%",  // Narrow neck for the funnel shape
    //         neckHeight: "30%", // Tall neck to emphasize the funnel shape
    //         valueRepresents: "area",
    //         // showInLegend: true,
    //         // legendText: "{label}",
    //         dataPoints: [
    //           { y: screening_count, label: "Screening", color: "#17b0e3" },
    //           { y: coding_count, label: "Coding", color: "#3bc482" },
    //           { y: interview_count, label: "Interview", color: "#e3cd09" },
    //           { y: offer_count, label: "Offer Letter", color: "#93c131" }
    //         ]
    //       }]
    //     });
    //     chart.render();
    // }
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