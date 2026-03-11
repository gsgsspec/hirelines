$('#registerForm').on('submit', function (event) {
event.preventDefault();

    $('#register').prop('disabled', true);

    // Reset all errors
    $('#email-invalid, #company-invalid, #companytype-invalid, #name-invalid, #location-invalid').addClass('hidden');
    $('#domain-check, #existing-email, #error-existing, #error-sec, #success-sec').addClass('hidden');

    $('#reg-bemail, #reg-company, #reg-companytype, #reg-name, #reg-location').css('border-color', '');

    let hasError = false;

    if (!$('#reg-bemail').val()) {
        $('#email-invalid').removeClass('hidden');
        $('#reg-bemail').css('border-color', 'red');
        hasError = true;
    }

    if (!$('#reg-company').val()) {
        $('#company-invalid').removeClass('hidden');
        $('#reg-company').css('border-color', 'red');
        hasError = true;
    }

    if (!$('#reg-companytype').val()) {
        $('#companytype-invalid').removeClass('hidden');
        $('#reg-companytype').css('border-color', 'red');
        hasError = true;
    }

    if (!$('#reg-name').val()) {
        $('#name-invalid').removeClass('hidden');
        $('#reg-name').css('border-color', 'red');
        hasError = true;
    }

    if (!$('#reg-location').val()) {
        $('#location-invalid').removeClass('hidden');
        $('#reg-location').css('border-color', 'red');
        hasError = true;
    }

    if (hasError) {
        $('#register').prop('disabled', false);
        return;
    }

    let dataObj = {
        'reg-bemail': $('#reg-bemail').val(),
        'reg-company': $('#reg-company').val(),
        'reg-location': $('#reg-location').val(),
        'reg-name': $('#reg-name').val(),
        'reg-companytype': $('#reg-companytype').val()
    };

    let final_data = {
        'data': JSON.stringify(dataObj),
        csrfmiddlewaretoken: CSRF_TOKEN,
    };

    $.post(CONFIG['portal'] + "/api/register-user", final_data, function (res) {

        if (res.statusCode == 0) {

            $('#success-sec').removeClass('hidden');
            $('#register').hide();

        } 
        else if (res.statusCode == 1) {

            $('#reg-bemail').css('border-color', 'red');
            $('#domain-check').removeClass('hidden');
            $('#register').prop('disabled', false);

        } 
        else if (res.statusCode == 2) {

            $('#reg-bemail').css('border-color', 'red');
            $('#existing-email').removeClass('hidden');
            $('#register').prop('disabled', false);

        } 
        else if (res.statusCode == 3) {

            $('#reg-bemail').css('border-color', 'red');
            $('#error-existing').removeClass('hidden');
            $('#register').prop('disabled', false);

        } 
        else {

            $('#error-sec').removeClass('hidden');
            $('#register').prop('disabled', false);

        }

    });

});



// document.getElementById("register").onclick = function () {
//     $('#registerForm').unbind('submit').bind('submit', function (event) {
//         event.preventDefault();

//         $('#register').prop('disabled', true);

//         $('#reg-bemail').css('border-color', '');
//         $('.domain-check').css('display', 'none');
//         $('.existing-email').css('display', 'none');
//         $('.error-existing').css('display', 'none');


        
//         dataObj = {
//             'reg-bemail': $('#reg-bemail').val(),
//             'reg-company':$('#reg-company').val(),
//             'reg-location': $("#reg-location").val(),
//             'reg-name': $("#reg-name").val(),
//             'reg-companytype': $("#reg-companytype").val()
//         }

//         var final_data = {
//             'data': JSON.stringify(dataObj),
//             csrfmiddlewaretoken: CSRF_TOKEN,
//         }

//         $.post(CONFIG['portal'] + "/api/register-user", final_data, function (res) {
//             if (res.statusCode == 0) {

//                 $('.success-sec').show()
//                 $('#register').hide();

//             }else if (res.statusCode == 1){

//                 $('#reg-bemail').css('border-color', 'red');
//                 $('.domain-check').css('display', 'block');

//                 $('#register').prop('disabled', false);
                
//             }
//             else if (res.statusCode == 2){

//                 $('#reg-bemail').css('border-color', 'red');
//                 $('.existing-email').css('display', 'block');

//                 $('#register').prop('disabled', false);
                
//             }
//             else if (res.statusCode == 3){

//                 $('#reg-bemail').css('border-color', 'red');
//                 $('.error-existing').css('display', 'block');

//                 $('#register').prop('disabled', false);
                
//             }

//             else {
//                 $('.error-sec').show()
//             }
//         })
        
//     })
// }



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

