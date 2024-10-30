document.getElementById("register").onclick = function () {
    $('#registerForm').unbind('submit').bind('submit', function (event) {
        event.preventDefault();

        $('#register').prop('disabled', true);

        $('#reg-bemail').css('border-color', '');
        $('.domain-check').css('display', 'none');
        $('.existing-email').css('display', 'none');
        $('.error-existing').css('display', 'none');


        
        dataObj = {
            'reg-bemail': $('#reg-bemail').val(),
            'reg-company':$('#reg-company').val(),
            'reg-location': $("#reg-location").val(),
            'reg-name': $("#reg-name").val(),
            'reg-companytype': $("#reg-companytype").val()
        }

        var final_data = {
            'data': JSON.stringify(dataObj),
            csrfmiddlewaretoken: CSRF_TOKEN,
        }

        $.post(CONFIG['portal'] + "/api/register-user", final_data, function (res) {
            if (res.statusCode == 0) {

                $('.success-sec').show()
                $('#register').hide();

            }else if (res.statusCode == 1){

                $('#reg-bemail').css('border-color', 'red');
                $('.domain-check').css('display', 'block');

                $('#register').prop('disabled', false);
                
            }
            else if (res.statusCode == 2){

                $('#reg-bemail').css('border-color', 'red');
                $('.existing-email').css('display', 'block');

                $('#register').prop('disabled', false);
                
            }
            else if (res.statusCode == 3){

                $('#reg-bemail').css('border-color', 'red');
                $('.error-existing').css('display', 'block');

                $('#register').prop('disabled', false);
                
            }

            else {
                $('.error-sec').show()
            }
        })
        
    })
}



$('#reg-bemail').on('keyup', function() {

    var classesToCheck = ['.invalid-feedback', '.domain-check', '.existing-email'];

    classesToCheck.forEach(function(className) {
        $(className).each(function() {
            if ($(this).css('display') === 'block') {
                $(this).hide();
            }
        });
    });

});

