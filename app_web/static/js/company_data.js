document.getElementById("update-data").onclick = function () {

    $('#company-data').unbind('submit').bind('submit', function (event) {
        event.preventDefault(); 
    })

    $("#update-data").prop("disabled", true);


    dataObjs = {
        'company-name': $('#company-name').val(),
        'contact-person': $('#contact-person').val(),
        'company-email': $('#company-email').val(),
        'phone': $('#phone').val(),
        'website': $('#website').val(),
        'city': $('#city').val(),
        'country': $('#country').val(),
        'companytype': $('#companytype').val(),
        'location': $('#location').val(),
        'Linkedin': $('#linkedin').val(),
        'Facebook': $('#facebook').val(),
        'Instagram': $('#instagram').val(),
        'Youtube': $('#youtube').val(),
        'Twitter': $('#twitter').val(),
        'cid' : $('#company-id').attr('name')
    }

    var final_data = {
        'data': JSON.stringify(dataObjs),
        csrfmiddlewaretoken: CSRF_TOKEN,
    }

    $.post(CONFIG['portal'] + "/api/update-company", final_data, function (res) {
        if (res.statusCode == 0) {
            showSuccessMessage('Company Details Updated');
            $("#update-data").prop("disabled", false);
        } else {
            showFailureMessage('Error in updating  the Email Template. Please try again after some time');
            $("#update-data").prop("disabled", false);
        }
    })
}