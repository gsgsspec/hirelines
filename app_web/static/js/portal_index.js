var currentUrl = window.location.href;

var menuItemsUrls = {
    'dashboard': ['/dashboard'],
    'questionnaire': ['/questionnaire', '/add-category', '/add-report-data', '/edit-category', '/section-edit', '/section-add'],
    'email-templates': ['/email-templates'],
    'candidates': ['/candidates', '/add-candidate'],
    'branding': ['/branding'],
    'reports': ['/reports','/jd'],
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
