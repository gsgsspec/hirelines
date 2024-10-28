document.getElementById("save-data").onclick = function () {

    $('#form-data').unbind('submit').bind('submit', function (event) {
        event.preventDefault(); 
    })

    dataObjs = {
        'id':$('#template_name').attr('name'),
        'template_name': $('#template_name').val(),
        'paper_type': $('#paper_type').val(),
        'event': $('#event').val(),
        'sender_label': $('#sender_label').val(),
        // 'from_email': $('#from_email').val(),
        'email_subject': $('#email_subject').val(),
        'email_body': $('#email_body').val(),
        'template_heading': $('#template_heading').val()
    }

    var final_data = {
        'data': JSON.stringify(dataObjs),
        csrfmiddlewaretoken: CSRF_TOKEN,
    }

    $.post(CONFIG['acert'] + "/api/update-emailtemp", final_data, function (res) {
        if (res.statusCode == 0) {
            $.post(CONFIG['portal'] + "/api/update-emailtemp", final_data, function (res){})
                showSuccessMessage('Email Template added successfully');
                setTimeout(function () { window.location.href = '/email-templates' }, 2000);
        }
        else{
            showFailureMessage('Error in saving the Email Template. Please try again after some time')
        }
    })

}
