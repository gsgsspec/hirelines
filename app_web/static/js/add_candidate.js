document.getElementById("save-data").onclick = function () {
    // $('#candidate-data').unbind('submit').bind('submit', function (event) {
    //     event.preventDefault(); 
    // })

    // dataObjs = {
    //     'firstname': $('#firstname').val(),
    //     'lastname': $('#lastname').val(),
    //     'email': $('#email').val(),
    //     'mobile': $('#mobile').val(),
    //     'jd': $('#jd').val(),
    //     'begin-from': $('#begin-from').val(),
    // }

    // console.log('dataObjs',dataObjs);

    window.location.href='/interview-schedule'
    
    

}


$(document).ready(function () {
    $('#jd').change(function() {
        let jobid = $(this).val();
        $('#begin-from').html('');
        $.get(CONFIG['portal'] + "/api/get-jd-workflow?jid="+jobid, function (res) {
            if(res.statusCode==0){
                var TOPICS = res.data
                $("#question_topic").html('')
                $("#question_topic").append('<option value="" disabled selected></option>')
                for (var i = 0; i < TOPICS.length; i++) {
                    $("#question_topic").append('<option value='+TOPICS[i]["id"]+'>' + TOPICS[i]["topic_code"] + ' - ' + TOPICS[i]["topic_name"] + '</option>')
                }
            }else{
                alert("Internal server error")
            }
                
        })

    });
});