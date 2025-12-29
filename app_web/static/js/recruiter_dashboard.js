

    document.addEventListener("DOMContentLoaded", function () {

        const monthInput = document.getElementById("monthFilter");

        //  Set current month by default (YYYY-MM)
        const today = new Date();
        const currentMonth =
            today.getFullYear() + "-" + String(today.getMonth() + 1).padStart(2, "0");

        monthInput.value = currentMonth;

        //  Optional: Log formatted value (Dec - 2025)
        formatMonth(currentMonth);

        monthInput.addEventListener("change", function () {
            formatMonth(this.value);
        });

        function formatMonth(value) {
            if (!value) return;

            const date = new Date(value + "-01");
            const formatted = date.toLocaleDateString("en-US", {
                month: "short",
                year: "numeric"
            });

            console.log("Selected Month:", formatted); // Dec 2025
        }
    });

    $(document).ready(function () {

        const recruiterFilter = $("#recruiterFilter");
        const monthFilter = $("#monthFilter");

        function loadDashboardData() {

            let params = {};

            if (recruiterFilter.length && recruiterFilter.val()) {
                params.recruiter = recruiterFilter.val();
            }

            if (monthFilter.length && monthFilter.val()) {
                params.month = monthFilter.val();
            }

            $.get(
                CONFIG['portal'] + "/api/recruiter-dashboard-filter",
                params,   //  filters passed here
                function (response) {
                    console.log("response", response)

                    if (response.statusCode === 0) {
                        updateCards(response.data);
                    } else {
                        console.error(response.error);
                    }
                }
            );

        }

        function updateCards(data) {
            $("#submittedCount").text(data.submitted);
            $("#profiledCount").text(data.profiled);
            $("#rejectedCount").text(data.rejected);
            $("#sentClientCount").text(data.sent_client);
            $("#rejectedClientCount").text(data.rejected_client);
            $("#selectedClientCount").text(data.selected_client);
            $("#waitingFeedbackCount").text(data.waiting_feedback);
            $("#submittedCount").closest(".card-body").find(".text-heading")
                .text(data.submitted_percentage + "%");

            $("#profiledCount").closest(".card-body").find(".text-heading")
                .text(data.profiled_percentage + "%");

            $("#rejectedCount").closest(".card-body").find(".text-heading")
                .text(data.rejected_percentage + "%");

            $("#sentClientCount").closest(".card-body").find(".text-heading")
                .text(data.sent_client_percentage + "%");

            $("#selectedClientCount").closest(".card-body").find(".text-heading")
                .text(data.selected_client_percentage + "%");

            $("#rejectedClientCount").closest(".card-body").find(".text-heading")
                .text(data.rejected_client_percentage + "%");

            $("#waitingFeedbackCount").closest(".card-body").find(".text-heading")
                .text(data.waiting_feedback_percentage + "%");
            $(".comparisonText").text(data.comparison_text);


        }

        recruiterFilter.on("change", function () {
            loadDashboardData();
            loadLineGraph();
        });

        monthFilter.on("change", function () {
            loadDashboardData();
            loadLineGraph();
        });


        loadDashboardData();
        loadLineGraph();

    });

// Line Chart id
const lineChart = document.getElementById('linechart').getContext('2d');


// Line Chart ctx
let lineChartInstance = null;

function loadLineGraph() {

    let params = {};

    if ($("#recruiterFilter").val()) {
        params.recruiter = $("#recruiterFilter").val();
    }

    if ($("#monthFilter").val()) {
        params.month = $("#monthFilter").val();
    }

    $.get(CONFIG['portal'] + "/api/dashboard", params, function (res) {
        console.log("res", res);

        if (res.statusCode !== 0) return;

        const graphData = res.data.line_graph_data;
        const hasData = Object.keys(graphData)
            .filter(k => k !== "dates")
            .some(k => graphData[k].some(v => v > 0));

        if (!hasData) {
            $("#linechart").hide();
            $("#noGraphData").show();

            if (lineChartInstance) {
                lineChartInstance.destroy();
                lineChartInstance = null;
            }
            return;
        }
        $("#noGraphData").hide();
        $("#linechart").show();

        const chartData = {
            labels: graphData.dates,
            datasets: [
                {
                    label: 'Profiles Received',
                    data: graphData.submitted,
                    borderColor: '#696cff',
                    backgroundColor: 'rgba(105,108,255,0.15)',
                    borderWidth: 2,
                    tension: 0
                },
                {
                    label: 'Reviewed & Profiled',
                    data: graphData.profiled,
                    borderColor: '#ffab00',
                    backgroundColor: 'rgba(255,171,0,0.15)',
                    borderWidth: 2,
                    tension: 0
                },
                {
                    label: 'Reviewed & Rejected',
                    data: graphData.rejected,
                    borderColor: '#ff3e1d',
                    backgroundColor: 'rgba(255,62,29,0.15)',
                    borderWidth: 2,
                    tension: 0
                },
                {
                    label: 'Submitted to Client',
                    data: graphData.sent_client,
                    borderColor: '#03c3ec',
                    backgroundColor: 'rgba(3,195,236,0.15)',
                    borderWidth: 2,
                    tension: 0
                },
                {
                    label: 'Rejected by Client',
                    data: graphData.rejected_client,
                    borderColor: '#800040',
                    backgroundColor: 'rgba(128,0,64,0.15)',
                    borderWidth: 2,
                    tension: 0
                },
                {
                    label: 'Selected by Client',
                    data: graphData.selected_client,
                    borderColor: '#00a878',
                    backgroundColor: 'rgba(0,168,120,0.15)',
                    borderWidth: 2,
                    tension: 0
                },
                {
                    label: 'Waiting for Feedback',
                    data: graphData.waiting_feedback,
                    borderColor: '#5856d6',
                    backgroundColor: 'rgba(88,86,214,0.15)',
                    borderWidth: 2,
                    tension: 0
                }
            ]
        };

        const chartConfig = {
            type: 'line',
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                        align: 'end',
                        labels: {
                            boxWidth: 10,
                            padding: 12
                        }
                    },
                    tooltip: { enabled: true }
                },
                scales: {
                    x: {
                        title: { display: true, text: 'Last 15 Days' },
                        grid: { display: false }
                    },
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Profiles Count' },
                        ticks: { precision: 0 }
                    }
                }
            }
        };

        if (lineChartInstance) {
            lineChartInstance.destroy();
        }

        lineChartInstance = new Chart(lineChart, chartConfig);
    });
}




document.addEventListener('DOMContentLoaded', () => {
    const loader = document.getElementById('dashboard-loader');

    window.addEventListener('load', () => {
        loader.style.display = 'none';
    });
});






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