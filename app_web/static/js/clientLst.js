/**************************************************
 * GLOBALS
 **************************************************/
let CURRENT_CLIENT_ID = null;

/**************************************************
 * DATATABLE INIT
 **************************************************/
$(document).ready(function () {
    $.noConflict();

    $('#candidates-table').DataTable({
        pageLength: 50,
        lengthMenu: [10, 25, 50],
        order: [],
        ordering: false,
        language: {
            search: "",
            searchPlaceholder: "Search..."
        },
        pagingType: 'simple_numbers'
    });
});

/**************************************************
 * UTIL HELPERS
 **************************************************/
function el(id) {
    return document.getElementById(id);
}

function hideIfExists(id) {
    if (el(id)) el(id).hidden = true;
}

function showIfExists(id) {
    if (el(id)) el(id).hidden = false;
}

function setValueIfExists(id, value) {
    if (el(id)) el(id).value = value;
}

/**************************************************
 * OPEN CREATE MODAL
 **************************************************/
function openNewUserModal() {

    CURRENT_CLIENT_ID = null; // reset

    hideIfExists('NewUserNameValidation');

    if (el('UserCreateAndEditModal')) {
        el('UserCreateAndEditModal').innerText = 'New Client';
    }

    setValueIfExists('newUserName', '');

    if (el('saveUser_')) {
        el('saveUser_').dataset.updateorcreate = 'create';
    }

    const modalElement = el('AddNewUserModal');
    if (modalElement) {
        new bootstrap.Modal(modalElement).show();
    }
}

/**************************************************
 * OPEN EDIT MODAL
 **************************************************/
function openEditUserModal(clientId) {

    CURRENT_CLIENT_ID = clientId; // ✅ IMPORTANT

    hideIfExists('NewUserNameValidation');

    if (el('UserCreateAndEditModal')) {
        el('UserCreateAndEditModal').innerText = 'Edit Client';
    }

    if (el('saveUser_')) {
        el('saveUser_').dataset.updateorcreate = 'update';
    }

    const clientField = el('userNameField_' + clientId);
    if (!clientField) return;

    setValueIfExists('newUserName', clientField.dataset.username || '');

    const modalElement = el('AddNewUserModal');
    if (modalElement) {
        new bootstrap.Modal(modalElement).show();
    }
}

/**************************************************
 * SAVE (CREATE / UPDATE) CLIENT
 **************************************************/
function addNewUser() {

    const eventType = el('saveUser_').dataset.updateorcreate || 'create';
    const name = el('newUserName').value.trim();

    if (!name) {
        showIfExists('NewUserNameValidation');
        return;
    }

    hideIfExists('NewUserNameValidation');

    const dataObj = {
        event: eventType,
        userName: name
    };

    // ✅ send clientId only for update
    if (eventType === 'update') {
        dataObj.clientId = CURRENT_CLIENT_ID;
    }

    $.post(
        CONFIG['portal'] + "/api/add-new-client",
        {
            data: JSON.stringify(dataObj),
            csrfmiddlewaretoken: CSRF_TOKEN
        },
        function (res) {
            if (res.statusCode === 0) {
                el('close_add_user_modal').click();
                location.reload(); // simple & safe
            }
        }
    );
}

/**************************************************
 * STATUS CHANGE
 **************************************************/
function changeUserStatus(elementid, event) {

    if (event) event.stopPropagation(); // prevent edit popup

    const checkbox = el(elementid);
    if (!checkbox) return;

    const clientId = elementid.split('_')[1];
    const status = checkbox.checked ? 'A' : 'I';

    checkbox.title = checkbox.checked ? 'Active' : 'Inactive';

    $.post(
        CONFIG['portal'] + "/api/change-client-status",
        {
            data: JSON.stringify({
                userid: clientId,
                status: status
            }),
            csrfmiddlewaretoken: CSRF_TOKEN
        }
    );
}c