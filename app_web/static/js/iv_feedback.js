document.getElementById("save").onclick = function () {
    $('#ivfeedback_form').unbind('submit').bind('submit', function (event) {
        event.preventDefault();

        gonogo = document.getElementById('toggle').checked ? 'Y' : 'N';

        dataObj = {
            'candidateid': $('#candidateid').attr("name"),
            'notes': $('#notes').val(),
            'gonogo':gonogo
        }

        var final_data = {
            'data': JSON.stringify(dataObj),
            csrfmiddlewaretoken: CSRF_TOKEN,
        }

        $.post(CONFIG['portal'] + "/api/interview-feedback", final_data, function (res) {

            if (res.statusCode == 0) {
                Swal.fire({
                    position: 'center',
                    icon: 'success',
                    title: 'Feedback Submitted',
                    showConfirmButton: false,
                    timer: 2000
                })
                setTimeout(function () { window.location.href = '/feedbacks' }, 2000);

            } else {
                Swal.fire({
                    position: 'center',
                    icon: 'error',
                    title: 'Error in submitting the feedback',
                    text: 'Please try again after some time',
                    showConfirmButton: false,
                    timer: 1500
                })
                
            }
        })

    })
}