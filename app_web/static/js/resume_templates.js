$(document).ready(function () {

    $("#saveTemplateBtn").on("click", function () {

        let selectedTemplateId = $("input[name='resume_template']:checked").val();

        if (!selectedTemplateId) {
            Swal.fire({
                position: 'center',
                icon: 'warning',
                title: 'Please select a template',
                showConfirmButton: false,
                timer: 2000
            });
            return;
        }


        dataObjs = {
            'template_id': selectedTemplateId,
        }

        var final_data = {
            'data': JSON.stringify(dataObjs),
            csrfmiddlewaretoken: CSRF_TOKEN,
        }

        $.post(CONFIG['portal'] + "/api/update-resume-template", final_data, function (res) {
            if (res.statusCode == 0) {
                Swal.fire({
                    position: 'center',
                    icon: 'success',
                    title: 'Resume template updated',
                    showConfirmButton: false,
                    timer: 2000
                })
            } else {
                Swal.fire({
                    position: 'center',
                    icon: 'error',
                    title: 'Error in Updating resume template',
                    text: 'Please try again after some time',
                    showConfirmButton: false,
                    timer: 2000
                })
            }
           
        }).fail(function (xhr, status, error) {
            Swal.fire({
                position: 'center',
                icon: 'error',
                title: 'Error in Updating resume template',
                text: 'Please try again after some time',
                showConfirmButton: false,
                timer: 2000
            })
        })

    });

});