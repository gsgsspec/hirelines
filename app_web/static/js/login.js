document.getElementById('login-btn').onclick=function(){

    $('#login-form').unbind('submit').bind('submit',function(event){
        event.preventDefault();

       
        dataObj = {
            'email': $('#email').val(),
            'password': $('#password').val(),
        }

        var final_data = {
            'data': JSON.stringify(dataObj),
            csrfmiddlewaretoken: CSRF_TOKEN,
        }

        $.post(CONFIG['portal'] + "/api/login-user", final_data, function (res) {
        
            if (res.statusCode == 0){   
                if (res.token == 'token_generated'){
                    if(res.data == 'HR-Admin'){
                        window.location.href = '/job-descriptions'
                    } else if(res.data == 'Interviewer'){
                        window.location.href = '/interviews' 
                    }
                }
                else{
                    $('#invalid_cred').removeAttr('hidden');
                }
            }

        })
    })

}