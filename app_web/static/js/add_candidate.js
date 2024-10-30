document.getElementById("save-data").onclick = function () {

    $('#candidate-data').unbind('submit').bind('submit', function (event) {
        event.preventDefault(); 
    })

    $("#save-data").prop("disabled", true);


    dataObjs = {
        'firstname': $('#firstname').val(),
        'lastname': $('#lastname').val(),
        'email': $('#email').val(),
        'mobile': $('#mobile').val(),
        'jd': $('#jd').val(),
        'begin-from': $('#begin-from').val(),
    }

    var final_data = {
        'data': JSON.stringify(dataObjs),
        csrfmiddlewaretoken: CSRF_TOKEN,
    }

    $.post(CONFIG['portal'] + "/api/add-candidate", final_data, function (res) {
        if (res.statusCode == 0) {
            var candidateData = res.data
            if(candidateData['papertype'] == 'I'){
                window.location.href = '/interview-schedule/'+ candidateData['candidateid']
            } else {
                Swal.fire({
                    position: 'center',
                    icon: 'success',
                    title: 'andidate added successfully',
                    showConfirmButton: false,
                    timer: 1500
                })
                setTimeout(function () { window.location.href = '/candidates' }, 2000);
            }
        }
        else{
            $("#save-data").prop("disabled", false);
            Swal.fire({
                position: 'center',
                icon: 'error',
                title: 'Error in saving the candidate details',
                text: 'Please try again after some time',
                showConfirmButton: false,
                timer: 1500
            })
        }
    })
}


$(document).ready(function () {
    $('#jd').change(function() {
        let jobid = $(this).val();
        $('#begin-from').html('');
        $.get(CONFIG['portal'] + "/api/get-jd-workflow?jid="+jobid, function (res) {
            if(res.statusCode==0){
                var WORKFLOW = res.data
                $("#begin-from").html('')
                $("#begin-from").append('<option value="" disabled selected></option>')
                for (var i = 0; i < WORKFLOW.length; i++) {
                    $("#begin-from").append('<option value='+WORKFLOW[i]["paperid"]+'>' + WORKFLOW[i]["title"] + '</option>')
                }
            }else{
                alert("Cannot able to get JD Workflow")
            }
                
        })

    });
});
