document.getElementById("register").onclick = function () {
    $('#registerForm').unbind('submit').bind('submit', function (event) {
        event.preventDefault();

        $('#reg-bemail').css('border-color', '');
        $('.domain-check').css('display', 'none');
        $('.existing-email').css('display', 'none');

        
        dataObj = {
            'reg-bemail': $('#reg-bemail').val(),
            'reg-company':$('#reg-company').val(),
            'reg-location': $("#reg-location").val(),
            'reg-name': $("#reg-name").val(),
        }

        var final_data = {
            'data': JSON.stringify(dataObj),
            csrfmiddlewaretoken: CSRF_TOKEN,
        }

        $.post(CONFIG['portal'] + "/api/add-companydata", final_data, function (res) {
            if (res.statusCode == 0) {

                $('.success-sec').show()
                $('#register').hide();

            }else if (res.statusCode == 1){

                $('#reg-bemail').css('border-color', 'red');
                $('.domain-check').css('display', 'block');
                
            }
            else if (res.statusCode == 2){

                $('#reg-bemail').css('border-color', 'red');
                $('.existing-email').css('display', 'block');
                
            }

            else {
                // swal("Internal Server Error", "", "error");
            }
        })
        
    })
}





