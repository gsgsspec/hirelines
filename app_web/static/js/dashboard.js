// Line Chart id
const lineChart = document.getElementById('linechart').getContext('2d');

// Bar Chart id
const jdBarChart = document.getElementById('top-jds-bar-chart').getContext('2d');


$(document).ready(function () {
    $.get(CONFIG['portal'] + "/api/dashboard-graph-data", function (res, status) {
        if (res.statusCode == 0){

            var dashboardData = res.data

            // Line Chart 
            
            var lineGraphData = dashboardData['line_graph_data']
            
            const lineChartData = {

                labels: lineGraphData['dates'],

                datasets: [{
                        label: 'Screening',
                        data: lineGraphData['screening'],
                        backgroundColor: 'rgba(135, 99, 238, 0.5)',
                        borderColor: 'rgba(135, 99, 238, 1)',
                        borderWidth: 2,
                        tension: 0 
                    },
                    {
                        label: 'Coding',
                        data: lineGraphData['coding'],
                        backgroundColor: 'rgba(0, 212, 98, 0.5)',
                        borderColor: 'rgba(0, 212, 98, 1)',
                        borderWidth: 2,
                        tension: 0 
                    },
                    {
                        label: 'Interview',
                        data: lineGraphData['interview'],
                        backgroundColor: 'rgba(31, 104, 243, 0.5)',
                        borderColor: 'rgba(31, 104, 243, 1)',
                        borderWidth: 2,
                        tension: 0 
                    }
                ],
            };

            const lineChartConfig = {
                type: 'line',
                data: lineChartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                            align: 'end',
                            labels: {
                                boxWidth: 12,
                                padding: 10
                            }
                        },
                        tooltip: {
                            enabled: true
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'Days'
                            }
                        },
                        y: {
                            title: {
                                display: true,
                                text: 'Registrations'
                            },
                            beginAtZero: true
                        }
                    }
                }
            };

            const linechart = new Chart(lineChart, lineChartConfig);
        
            // Bar Chart

            var jdChartData = dashboardData['jd_reg_data']
            
            const jdBarChartdata = {
                labels: jdChartData['jdtitle'], 
                datasets: [
                    {
                        label: 'Screening',
                        data: jdChartData['screening_count'],
                        backgroundColor: 'rgba(135, 99, 238, 0.5)',
                        borderColor: 'rgba(135, 99, 238, 1)',
                        borderWidth: 1,
                        barPercentage: 0.8,
                        categoryPercentage: 0.6 
                    },
                    {
                        label: 'Coding',
                        data: jdChartData['coding_count'],
                        backgroundColor: 'rgba(0, 212, 98, 0.5)',
                        borderColor: 'rgba(0, 212, 98, 1)',
                        borderWidth: 1,
                        barPercentage: 0.8,
                        categoryPercentage: 0.6
                    },
                    {
                        label: 'Interview',
                        data: jdChartData['interview_count'],
                        backgroundColor: 'rgba(31, 104, 243, 0.5)',
                        borderColor: 'rgba(31, 104, 243, 1)',
                        borderWidth: 1,
                        barPercentage: 0.8,
                        categoryPercentage: 0.6
                    },
                    {
                        label: 'Offered',
                        data: jdChartData['offered_count'],
                        backgroundColor: 'rgba(13, 148, 136, 0.5)',
                        borderColor: 'rgba(13, 148, 136, 1)',
                        borderWidth: 1,
                        barPercentage: 0.8,
                        categoryPercentage: 0.6
                    }
                ]
            };

            const jdBarChartConfig = {
                type: 'bar',
                data: jdBarChartdata,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                    },
                    scales: {
                        x: {
                            stacked: false,
                            ticks: {
                                callback: function(value, index, ticks) {
                                    const label = this.getLabelForValue(value); // Get the label for the value
                                    const maxLength = 20; // Set max length for the label
                                    return label.length > maxLength ? label.substring(0, maxLength) + '...' : label;
                                },
                            },
                        },
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            };

            const barJDchart = new Chart(jdBarChart, jdBarChartConfig);
            
        }
    })

})


document.addEventListener('DOMContentLoaded', () => {
    const loader = document.getElementById('dashboard-loader');

    window.addEventListener('load', () => {
        loader.style.display = 'none';
    });
});


// function showFullPage() {
//     $('#layout-menu').css('display', '')
//     $('#web-page').addClass('layout-menu-fixed')
//     $('#display_icon').css('display', 'none')
//     $('#hide_icon').css('display', 'block')
// }


// function hideFullPage() {
//     $('#layout-menu').css('display', 'none')
//     $('#web-page').removeClass('layout-menu-fixed')
//     $('#display_icon').css('display', 'block')
//     $('#hide_icon').css('display', 'none')
// }

// if (window.innerWidth > 900) {
//     $('#layout-menu').css('display', 'none');
// }

// $('#web-page').removeClass('layout-menu-fixed')



$(document).ready(function() {

    $('.counter').each(function () {
        $(this).prop('Counter',0).animate({
            Counter: $(this).text()
        }, {
            duration: 2000,
            easing: 'swing',
            step: function (now) {
                $(this).text(Math.ceil(now));
            }
        });
    }); 

});  


window.onload = function() {

    const elementsToAnimate = document.querySelectorAll('.animate-on-load');

    elementsToAnimate.forEach(function(element) {
        const animationType = element.getAttribute('data-animation'); // Get animation type

        element.classList.add('animate__animated');

        if (animationType) {
            element.classList.add(`animate__${animationType}`);
        }

        // Optionally, add delay classes based on a custom attribute or class
        // element.classList.add('animate__delay-1s');
    });
}