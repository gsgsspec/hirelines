document.getElementById('demo-btn').onclick=function(){

    $('#demo-form').unbind('submit').bind('submit',function(event){
        event.preventDefault();

       
        dataObj = {
            'company-name': $('#company-name').val(),
            'contact-person': $('#contact-person').val(),
            'email': $('#email').val(),
            'location': $('#location').val(),
        }

        var final_data = {
            'data': JSON.stringify(dataObj),
            csrfmiddlewaretoken: CSRF_TOKEN,
        }

        $.post(CONFIG['portal'] + "/api/demo-user", final_data, function (res) {
        
            if (res.statusCode == 0){   

                $('#demo-btn').hide();
                
                $('.demo-txt').show();
               
                // $('.re-demo-sec').show();
                
                // demo_id = res.data

                // $('#req-demo-btn').attr('onclick', `reqDemo(${demo_id})`)

            }

        })
    })

}


function reqDemo(id) {
   
    dataObj = {
        'demo-id': id
    }

    var final_data = {
        'data': JSON.stringify(dataObj),
        csrfmiddlewaretoken: CSRF_TOKEN,
    }


    $.post(CONFIG['portal'] + "/api/req-demo", final_data, function (res) {
        
        if (res.statusCode == 0){   
           
            $('.demo-video').hide();
            $('.demo-txt').show();

        }

    })

}