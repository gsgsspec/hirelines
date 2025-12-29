function getPidFromUrl() {
    const parts = window.location.pathname.split("/");
    return parts[parts.length - 1];   
}

function tabSwitch(element) {

    const pid = getPidFromUrl();  

    if (element === 'active') {
        $('#active').addClass('activeTab shadow');
        $('#Inactive').removeClass('activeTab shadow');
        window.location.href = "/profileview/" + pid;
    }

    if (element === 'Inactive') {
        $('#Inactive').addClass('activeTab shadow');
        $('#active').removeClass('activeTab shadow');
        window.location.href = "/profileactivity/" + pid;
    }

    if (element === 'addActivity') {
        
        $('#Inactive').removeClass('activeTab shadow');
        $('#activity_details_table').addClass('display-none');
        $('.add-activity').removeClass('display-none');
    

    }

    // if (element === 'sendWelcome') {

    //     window.location.href = "/profileactivity/" + pid;


    // }
   

}
$("#add-activity-details").submit(function (e) {
    e.preventDefault();

    const pid = getPidFromUrl();  // You already have this function

    let activityname = $("select[name='activityname']").val();
    let remarks = $("textarea[name='remarks']").val();
   

    // Prepare inner object
    let dataObj = {
        "activityname": activityname,
        "remarks": remarks,
        "profile_id": pid
    };

    // Prepare final POST object
    let final_data = {
        "data": JSON.stringify(dataObj),
        csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
    };

    console.log("final_data", final_data);

    
    $.post(CONFIG['portal'] + "/api/add-profile-activity", final_data)
        .done(function (res) {
            Swal.fire({
                title: "Saved Successfully!",
                icon: "success",
                timer: 1500,
                showConfirmButton: false
            });

            setTimeout(() => {
                window.location.href = "/profileactivity/" + pid;
            }, 1000);
        })
        .fail(function (err) {
            Swal.fire({
                title: "Error!",
                text: "Something went wrong while saving.",
                icon: "error",
                confirmButtonText: "OK"
            });
        });
});

function sendWelcomeMail() {
    const pid = getPidFromUrl(); 

    let final_data = {
        profile_id: pid,
        csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
    };

    $.post(CONFIG['portal'] + "/api/send-welcome-mail", final_data)
        .done(function (res) {
            console.log(res)
            if (res.statusCode === 0) {
                Swal.fire({
                    icon: "success",
                    title: "Welcome Mail Sent!",
                    timer: 1500,
                    showConfirmButton: false
                });
                
                window.location.reload()
            } else {
                Swal.fire({
                    icon: "error",
                    title: "Failed!",
                    text: res.error || "Unable to send email."
                });
            }
        })
        .fail(function () {
            Swal.fire({
                icon: "error",
                title: "Server Error",
                text: "Unable to send email"
            });
        });
}
