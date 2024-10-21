document.getElementById("save-data").onclick = function () {


    $('#candidate-data').unbind('submit').bind('submit', function (event) {
        event.preventDefault(); 
    })

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
                showSuccessMessage('Candidate added successfully');
                setTimeout(function () { window.location.href = '/candidates' }, 2000);
            }
        }
        else{
            showFailureMessage('Error in saving the candidate details. Please try again after some time')
        }
    })

    // window.location.href='/interview-schedule'
    
    

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
