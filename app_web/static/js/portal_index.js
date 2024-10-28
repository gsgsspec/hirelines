var currentUrl = window.location.href;

var menuItemsUrls = {
    'dashboard': ['/dashboard'],
    'questionnaire': ['/questionnaire', '/add-category', '/add-report-data', '/edit-category', '/section-edit', '/section-add'],
    'email-templates': ['/email-templates'],
    'candidates': ['/candidates', '/add-candidate','interview-schedule'],
    'branding': ['/branding'],
    'reports': ['/reports','/jd'],
    'job-descriptions' : ['/job-descriptions','/add-job-description','/job-description-set-up'],
    'interviews': ['/interviews'],
    'evaluation': ['/evaluation'],
    'feedback': ['/feedbacks','/interviewer-feedback'],
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

    setTimeout(function() {
        $('.bs-toast.toast.bg-success .toast-timeout').css('width', '');
    }, 1200);
}

function showFailureMessage(message) {

    $('.bs-toast.toast.bg-danger').removeAttr('hidden');
    $('.bs-toast.toast.bg-danger .toast-body').text(message);
    $('.bs-toast.toast.bg-danger').toast('show');
}
