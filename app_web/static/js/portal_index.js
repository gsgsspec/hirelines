var currentUrl = window.location.href;

var menuItemsUrls = {
    'dashboard': ['/dashboard'],
    'questionnaire': ['/questionnaire', '/add-category', '/add-report-data', '/edit-category', '/section-edit', '/section-add'],
    'branding': ['/branding'],
    'email-templates': ['/email-templates'],
    'candidates': ['/candidates', '/add-candidate', 'interview-schedule', '/candidate-data'],
    'branding': ['/branding'],
    'reports': ['/reports', '/jd'],
    'job-descriptions' : ['/job-descriptions','/add-job-description','/job-description-set-up','/update-job-description','/jd'],
    'interviews': ['/interviews'],
    'evaluation': ['/evaluation'],
    'feedback': ['/feedbacks', '/interviewer-feedback'],
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
            if(CREDITS_DATA.low_credits == "Y"){
                $("#credits_display").prop("hidden",true);
                $("#low_credits_display").prop("hidden",false);
                $("span[name='balance_credits_display']").html("Avaliable Credits : "+CREDITS_DATA.balance_credits)
            }else{
                $("#low_credits_display").prop("hidden",true);
                $("#credits_display").prop("hidden",false);
                $("span[name='balance_credits_display']").html("Avaliable Credits : "+CREDITS_DATA.balance_credits)
            }
        }
    })
}

