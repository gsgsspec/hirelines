window.addEventListener("pageshow", function (event) {
    var historyTraversal = event.persisted ||
        (typeof window.performance != "undefined" &&
            window.performance.navigation.type === 2);
    if (historyTraversal) {
        // Handle page restore.
        window.location.reload();
    }
});

$('#update_email_template_form').on('change keyup paste', ':input', function (e) {
    $('#test_mail').prop("disabled", true);
    $("#save_template").prop("disabled", false).html("Save");
    $("#clr_data").prop("disabled", false);
});

function clr_data() {
    $('#test_mail').prop("disabled", true);
    $("#save_template").prop("disabled", false).html("Save");
}


var attachment_name = null;
$(document).ready(function () {

    var attachmentFileInput = $('#email_attachment_file');

    if (attachmentFileInput.get(0).files.length > 0) {
        $('#remove_attachment').prop("hidden", false);
        attachment_name = attachmentFileInput[0].files[0].name

    } else {
        attachment_name = null;
    }

    $('#email_attachment_file').change(function (e) {
        attachment_name = e.target.files[0].name;
    });


});


var remove_attachment = "no";
$('#remove_attachment').on('click', function () {
    remove_attachment = "yes";
    $('#email_attachment_file').val('');
    $('#remove_attachment').prop("hidden", true);
    attachment_name = null;
})




$('#email_attachment_file').on('change', function (e) {
    if (this.files.length > 0) {
        attachment_name =  this.files[0].name
        $('#remove_attachment').prop("hidden", false);
    }else{
        $('#remove_attachment').prop("hidden", true);
        attachment_name = null
    }
})


document.getElementById("save-data").onclick = function () {

    $('#update_email_template_form').unbind('submit').bind('submit', function (event) {
        event.preventDefault();
    })

    dataObjs = {
        'id': $('#template_name').attr('name'),
        'template_name': $('#template_name').val(),
        'paper_type': $('#paper_type').val(),
        'event': $('#event').val(),
        'sender_label': $('#sender_label').val(),
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
            $.post(CONFIG['portal'] + "/api/update-emailtemp", final_data, function (res) { })
            showSuccessMessage('Email Template added successfully');
            setTimeout(function () { window.location.href = '/email-templates' }, 2000);
        }
        else {
            showFailureMessage('Error in saving the Email Template. Please try again after some time')
        }
    })

}
