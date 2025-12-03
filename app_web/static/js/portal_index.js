var currentUrl = window.location.href;

var menuItemsUrls = {
    'dashboard': ['/dashboard'],
    'questionnaire': ['/questionnaire', '/add-category', '/add-report-data', '/edit-category', '/section-edit', '/section-add'],
    'branding': ['/branding'],
    'email-templates': ['/email-templates','/update-emailtemp'],
    'candidates': ['/candidates', '/add-candidate', 'interview-schedule', '/candidate-data','/upload-candidates'],
    'branding': ['/branding'],
    'reports': ['/reports', '/jd'],
    'job-descriptions' : ['/job-descriptions','/add-job-description','/job-description-set-up','/update-job-description','/jd'],
    'interviews': ['/interviews'],
    'evaluation': ['/evaluation'],
    'users': ['/users'],
    'feedback': ['/feedbacks', '/interviewer-feedback'],
    'reports': ['/reports', '/credits-usage'],
    'company': ['/company-data'],
    'sources': ['/sources'],
    'resume-inbox': ['/resume-inbox'],
    'logout': ['/']
};

var menuItems = document.querySelectorAll('.menu-item');

menuItems.forEach(function (item) {
    var link = item.querySelector('a');
    var href = link.getAttribute('href');

    Object.entries(menuItemsUrls).forEach(([menuItem, urls]) => {
        if (urls.some(url => currentUrl.includes(url)) && href.includes(menuItem)) {
            item.classList.add('active');
        }
    });
});


function showSuccessMessage(message) {

    $('.bs-toast.toast.bg-success').removeAttr('hidden');
    $('.bs-toast.toast.bg-success .toast-body').text(message);
    $('.bs-toast.toast.bg-success').toast('show');
    $('.bs-toast.toast.bg-success .toast-timeout').css('width', '100%');

    setTimeout(function () {
        $('.bs-toast.toast.bg-success .toast-timeout').css('width', '');
    }, 1200);
}

function showFailureMessage(message) {

    $('.bs-toast.toast.bg-danger').removeAttr('hidden');
    $('.bs-toast.toast.bg-danger .toast-body').text(message);
    $('.bs-toast.toast.bg-danger').toast('show');
}


$(document).ready(function () {
    getCredits();
    setInterval(function() {
        getCredits()
    }, 30000); // 1000 ms = 1 second
})


function getCredits(){
    $.get(CONFIG['portal'] + "/api/get-credits", function (res) {

        if (res.statusCode == 0) {
            var CREDITS_DATA = res.data;
            if(CREDITS_DATA.credits_avaliabilty == "N"){
                $("#credits_display").prop("hidden",true);
                $("#low_credits_display").prop("hidden",false);
                $("span[name='balance_credits_display']").html("Low Credits("+CREDITS_DATA.balance_credits+"). Auto promote and New Registrations will be stopped. Please Load Credits")
            }else if(CREDITS_DATA.credits_avaliabilty == "L"){
                $("#credits_display").prop("hidden",true);
                $("#low_credits_display").prop("hidden",false);
                $("span[name='balance_credits_display']").html("Low Credits("+CREDITS_DATA.balance_credits+"). Please Load Credits")
            }else{
                $("#low_credits_display").prop("hidden",true);
                $("#credits_display").prop("hidden",false);
                $("span[name='balance_credits_display']").html("Avaliable Credits : "+CREDITS_DATA.balance_credits)
            }
        }
    })
}

function signOut(){

    Swal.fire({
        title: "Do you want to Sign out?",
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#274699',
        cancelButtonColor: '#f25c05',
        confirmButtonText: 'Sign out'
    }).then((result) => {
        if (result.isConfirmed) {
        window.location.href = '/sign-out'
        }
    })
}

function fetchUserName() {
    fetch('/api/get-user-name')
        .then(response => {
            if (!response.ok) {
                alert("User not authenticated");
                throw new Error("User not authenticated");
            }
            return response.json();
        })
        .then(data => {
            // Check if the element exists before updating it
            const userNameMenu = document.getElementById("user-name-menu");
            if (userNameMenu) {
                userNameMenu.innerHTML += data.name;
            }
        })
        .catch(error => {
            console.error("Error fetching user data:", error);
        });
}
    

document.addEventListener("DOMContentLoaded", fetchUserName);

