
document.getElementById("save_branding").onclick = function () {
    $('#brand_form').unbind('submit').bind('submit', function (event) {
        event.preventDefault();
        $('button').prop("disabled",true);
        $('#save_branding').html("Please Wait...");
        dataObj = {
            'request_type': 'update_branding',
            'branding_id': $('#organization').attr('name'),
            // 'organization': $('#organization').val(),
            'css_content': $('#css_content').val(),
            'social_links': $('#social_links').val(),
            'status': $("input[name='status']:checked").val()
        }

        var final_data = {
            'data': JSON.stringify(dataObj),
            csrfmiddlewaretoken: CSRF_TOKEN,
        }

        var form = $('#brand_form')[0];
        var data = new FormData(form);
        
        Object.keys(final_data).forEach(key => data.append(key, final_data[key]));

        var fileInput = document.getElementById('logo');
        if (fileInput.files.length > 0) {
            data.append('logo', fileInput.files[0]);
        }
        
        $.ajax({
            type: "POST",
            enctype: 'multipart/form-data,application/json',
            url: CONFIG['portal'] + "/api/update-company-branding",
            data: data,
            processData: false,
            contentType: false,
            cache: false,
            timeout: 600000,
            success: function (res) {
                $('button').prop("disabled",false);
                $('#save_branding').html("Save");
                if (res.statusCode == 0) {
                    Swal.fire({
                        icon: 'success',
                        title: 'Branding updated successfully',
                        showConfirmButton:false,
                        // confirmButtonText: 'OK',
                        // confirmButtonColor: '#274699'
                    })
                    setTimeout(function () { window.location.href = "/branding" }, 2000);

                } else {
                    Swal.fire({
                        icon: 'error',
                        title: 'Could not process your request',
                        text: 'Internal Server Error',
                        footer: 'Please contact administrator',
                        confirmButtonText: 'OK',
                        confirmButtonColor: '#274699'
                    })
                }
            },
            error: function (xhr, status, error) {
                $('button').prop("disabled",false);
                $('#save_branding').html("Save");
                        // Handle the error (network issue, server-side error, etc.)
                let errorMessage = "An error occurred while processing your request. Please try again later.";
                
                // You can customize the error message based on the status or error received.
                if (xhr.status === 0) {
                    errorMessage = "Network error. Please check your internet connection.";
                } else if (xhr.status === 500) {
                    errorMessage = "Server error. Please try again later.";
                }
                Swal.fire({
                    icon: 'error',
                    title: 'Request failed',
                    text: errorMessage,
                    footer: 'Please contact administrator if the issue persists.',
                    confirmButtonText: 'OK',
                    confirmButtonColor: '#274699'
                });
            }
        })

    })
}