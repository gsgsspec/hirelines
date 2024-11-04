window.addEventListener("pageshow", function (event) {
    var historyTraversal = event.persisted ||
        (typeof window.performance != "undefined" &&
            window.performance.navigation.type === 2);
    if (historyTraversal) {
        // Handle page restore.
        window.location.reload();
    }
});
var remove_attachment = "no";
var update_remove_attachment = "no"

$('#update_email_template_form').on('change keyup paste', ':input', function (e) {
    $('#test_mail').prop("disabled", true);
    $("#save_template").prop("disabled", false).html("Save");
    $("#clr_data").prop("disabled", false);
});

function clr_data() {
    $('#test_mail').prop("disabled", true);
    $("#save_template").prop("disabled", false).html("Save");
}

var user_email = null;

$(document).ready(function () {

    user_email = usr_email
})
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

    // $('#email_attachment_file').change(function (e) {
    //     attachment_name = e.target.files[0].name;
    // });


});

function updateFileDisplay() {
    const input = document.getElementById('email_attachment_file');
    const display = document.querySelector('.custom-file-display');
    if(input.files.length > 0){
        display.textContent = `Choose File | ${input.files[0].name}`;
        update_remove_attachment = "update"
    }else{
        display.textContent = "Choose a file";
        update_remove_attachment = "remove"
    }
    
}


$('#remove_attachment').on('click', function () {
    const display = document.querySelector('.custom-file-display');
    display.textContent = "Choose a file";
    // $("#uploaded_filename").prop("hidden",true);
    $("#email_attachment_name").val("")
    remove_attachment = "yes";
    $('#email_attachment_file').val('');
    $('#remove_attachment').prop("hidden", true);
    attachment_name = null;
    update_remove_attachment = "remove"
})


$('#email_attachment_file').on('change', function (e) {
    // $("#uploaded_filename").prop("hidden",true)
    if (this.files.length > 0) {
        attachment_name = this.files[0].name
        $('#remove_attachment').prop("hidden", false);
        update_remove_attachment = "update"
    } else {
        $('#remove_attachment').prop("hidden", true);
        attachment_name = null
        update_remove_attachment = "remove"
    }
    
})


window.submit_form = function (id, request_type = null) {

    $('#update_email_template_form').unbind('submit').bind('submit', function (event) {
        event.preventDefault();
    })

    dataObjs = {
        'company_id': $('#template_name').attr('name'),
        'template_name': $('#template_name').val(),
        'template_heading': $('#template_heading').val(),
        'paper_type': $('#paper_type').val(),
        'event': $('#event').val(),
        'sender_label': $('#sender_label').val(),
        'email_subject': $('#email_subject').val(),
        'email_body': $('#email_body').val(),
        'attachment_name': attachment_name,
        'file_name': $('#email_attachment_name').val(),
        'user_email': user_email,
        'request_type': request_type,
        "update_remove_attachment":update_remove_attachment
    }
    console.log("dataObjs",dataObjs);
    
    if (request_type == 'testmail') {
        $("#test_mail").html("Please Wait");
        $("#test_mail").prop("disabled", true);
        $("#save_template").prop("disabled", true);
        $("#clr_data").prop("disabled", true);
        dataObjs["user_email"] = user_email
    }
    if (request_type == 'savetemplate') {
        $("#save_template").html("Please Wait");
        $("#save_template").prop("disabled", true);
        $("#clr_data").prop("disabled", true);

    }

    var final_data = {
        'data': JSON.stringify(dataObjs),
        csrfmiddlewaretoken: CSRF_TOKEN,
    }

    var form = $('#update_email_template_form')[0];
    var data = new FormData(form);
    Object.keys(final_data).forEach(key => data.append(key, final_data[key]));

    $.ajax({
        type: "POST",
        enctype: 'application/json',
        url: CONFIG['acert'] + "/api/update-emailtemp",
        data: data,
        processData: false,
        contentType: false,
        cache: false,
        timeout: 600000,
        success: function (res) {
            if (res.statusCode == 0) {
                $.ajax({
                    type: "POST",
                    enctype: 'application/json',
                    url: CONFIG['portal'] + "/api/update-emailtemp",
                    data: data,
                    processData: false,
                    contentType: false,
                    cache: false,
                    timeout: 600000,
                    success: function (res) {
                        if (res.statusCode == 0) {
                            if (request_type == "testmail") {
                                showSuccessMessage('Test mail sent successfully');
                                $("#update_email_template_form :input").prop("disabled", false);
                                $("#paper_type").prop("disabled",true);
                                $("#event").prop("disabled",true);
                                // setTimeout(function () { window.location.href = '/email-templates' }, 2000);
                            } else {
                                showSuccessMessage('Email Template added successfully');
                                $("#update_email_template_form :input").prop("disabled", true);
                            }
                            $("#save_template").html("Saved");
                            $("#save_template").prop("disabled", true);
                            $("#clr_data").prop("disabled", true);
                            // $("#duplicate_usage").prop("hidden", true);
                            $("#test_mail").prop("disabled", false);
                            $("#test_mail").html("Send Test mail");
                            $("#test_mail").prop("disabled", false);
                            // setTimeout(function () { window.location.href = '/email-templates' }, 2000);
                        }else{
                            showFailureMessage('Error in saving the Email Template. Please try again after some time')
                        }

                    }
                })

            }
            else {
                showFailureMessage('Error in saving the Email Template. Please try again after some time')
            }
        }
    })



}
