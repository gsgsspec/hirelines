$(document).ready(function () {
    var cd = "7365656e75";

    if ((window.location.href).split('api')[1]) {

        loadIframe((window.location.href).split('api')[1]);
    }
})


function hex2a(hexx) {

    var hex = hexx.toString();
    var str = '';
    for (var i = 0; i < hex.length; i += 2) {
        str += String.fromCharCode(parseInt(hex.substr(i, 2), 16));
    }

    return str;
}


function loadIframe(id) {
   $("#container").append('<iframe style="width:100% !important; " allow="autoplay;camera;microphone;" src="https://orbstage.onecall.ae:8001/vn/?room=' + id + '&wc&q=2"></iframe>')
}


var check_call_status_flag = callend_status

$(document).ready(function () {
    if (check_call_status_flag === 'N'){
        check_call_status();
        $('.int-cmplt').hide()
    }
    else if (check_call_status_flag === 'Y'){
        $('#interview-sec').hide()
        $('.int-cmplt').show()
    }
})

setInterval(function () {
    if (check_call_status_flag == "N") {
        check_call_status();
    }
}, 5000);


function check_call_status() {
    dataObj = {
        "candidate_id": candidate_id,
        "schedule_id": schedule_id
    }

    var final_data = {
        'data': JSON.stringify(dataObj),
        csrfmiddlewaretoken: CSRF_TOKEN,
    }

    $.post(CONFIG['portal'] + "/api/get-interview-status", final_data, function (res) {

        if (res.statusCode == 0) {
            if (res.data == "call_ended") {
                check_call_status_flag = "Y"
                let timerInterval;
                Swal.fire({
                    icon: "info",
                    title: "NOTE",
                    html: "Your interview is completed, your call will end in <b></b> seconds.",
                    timer: 6 * 1000,
                    timerProgressBar: true,
                    allowOutsideClick: false,
                    didOpen: () => {
                        Swal.showLoading();
                        const timer = Swal.getPopup().querySelector("b");
                        timerInterval = setInterval(() => {
                            const secondsLeft = Math.ceil(Swal.getTimerLeft() / 1000);
                            timer.textContent = `${secondsLeft}`;
                        }, 1000);
                    },
                    willClose: () => {
                        clearInterval(timerInterval);
                    }
                }).then((result) => {
                    $('#interview-sec').hide()
                    $('.int-cmplt').show()
                });

            }
        }

    })
}

