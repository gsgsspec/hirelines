$(document).ready(function() {
    $.noConflict();
    $('#candidates-table').DataTable({
        "order": [],
        "ordering": false,
        language: { search: "",searchPlaceholder: "Search..." } ,
        pagingType: 'simple_numbers'
    });
    
});


function addNewUser() {

  console.log('called');

  var event = document.getElementById('saveUser_').dataset.updateorcreate;

  if(event == 'update'){
    NewUserDataValidation = true
  }

  var newUserName_ = document.getElementById('newUserName').value;
  var newUserPassword_ = document.getElementById('newUserPassword').value;
  var newUserEmail_ = document.getElementById('newUserEmail').value;
  // var newUserRole_ = document.getElementById('newUserRole').value;
  var newUserLocation_ = document.getElementById('newUserLocation').value;
  
  var select = document.getElementById('newUserRole');
  var selectedOption = select.options[select.selectedIndex];
  var selectedRoleIdvalue = selectedOption.value;
  var newUserRole_ = selectedOption.text;

  var NewUserDataValidation = true;  // Initialize as true, and set to false if any validation fails

  // Username validation
  if (newUserName_ === "") {
    NewUserDataValidation = false;
    document.getElementById('NewUserNameValidation').hidden = false;
  } else {
    document.getElementById('NewUserNameValidation').hidden = true;
  }

 

  // Email validation
  var emailValidation = document.getElementById('newUserEmailValidation');

  if(event == 'create'){
    if (newUserEmail_ == "") {
      NewUserDataValidation = false;
      emailValidation.innerText = 'Email address is required';
      emailValidation.hidden = false;
    } else {
      var checkMail = validateEmail(newUserEmail_);
      if (checkMail == false) {
        NewUserDataValidation = false;
        emailValidation.innerText = 'Valid email is required';
        emailValidation.hidden = false;
      } else {
        emailValidation.hidden = true;
      }
    }
  }

  // Password validation
  var newUserPasswordValid = document.getElementById('NewUserpasswordValidation');
  if (newUserPassword_ == "") {
    NewUserDataValidation = false;
    newUserPasswordValid.innerText = 'Password is required';
    newUserPasswordValid.hidden = false;
  } else if (newUserPassword_.length <= 7) {
    NewUserDataValidation = false;
    newUserPasswordValid.innerText = 'Password is too short';
    newUserPasswordValid.hidden = false;
  } else {
    newUserPasswordValid.hidden = true;
  }

  if(event == 'create'){
    // Role validation Only for new users
    if (newUserRole_ === "Select Role") {
      NewUserDataValidation = false;
      document.getElementById('newUserRoleValidation').hidden = false;
    } else {
      document.getElementById('newUserRoleValidation').hidden = true;
    }
  }
   
  

  // Check final validation status
  if (NewUserDataValidation == true) {
    
    var dataObj = {
    'event'     :  event,
    "userName"  :  newUserName_,
    "userPswd"  :  newUserPassword_,
    "userEmail" :  newUserEmail_,
    "userRole"  :  selectedRoleIdvalue,
    "newUserLocation": newUserLocation_,
    };

    var final_data = {
        'data': JSON.stringify(dataObj),
        csrfmiddlewaretoken: CSRF_TOKEN,
    };

    $.post(CONFIG['portal'] + "/api/add-new-user", final_data, function (res) {
        if (res.statusCode == 0) {
          if(res.data){
              if(res.data['userAlreadyExisted'] == 'Y'){
                document.getElementById('userAlreadyExistedValidation').hidden = false;
              }
              else{
                if(res.data['event'] == 'created'){
                  
                  var newUsrId = res.data['userid']
                  // document.getElementById('successMsg').hidden = false
                  // document.getElementById('successMsg').innerHTML = '<i class="far fa-check-circle"></i> User Created'

                  var newUser = document.createElement('tr');
                  newUser.innerHTML = `
                  <td onclick="openEditUserModal('${newUsrId}')" ><strong id="userNameField_${newUsrId}" data-username="${newUserName_}" data-userpwd="${newUserPassword_}" data-useremail="${newUserEmail_}">${newUserName_}</strong></td>
                  <td onclick="openEditUserModal('${newUsrId}')" >${newUserEmail_}</td>
                  <td onclick="openEditUserModal('${newUsrId}')"  id="userRoleField_${newUsrId}" data-userrole="${newUserRole_}">${newUserRole_}</td>
                  <td onclick="openEditUserModal('${newUsrId}')" id="userLocation_${newUsrId}" data-userlocation="${newUserLocation_}">${newUserLocation_}</td>
                  <td id="userStatus_${newUsrId}" data-userstatus="A">
                      <div class="form-check form-switch mb-2">
                        <input class="form-check-input" type="checkbox" id="useractiveorinactive_${newUsrId}" checked="" onclick="changeUserStatus(this.id)">
                      </div>
                  </td>
                  `;
  
                  var userListTable = document.getElementById('userListTabelList');
                  userListTable.insertBefore(newUser, userListTable.firstChild);
                  // showSuccessMessage('User created');
                  
                  // setInterval(function() {
                    // Your code here
                    $('#close_add_user_modal').click();
                  // }, 2000);
                  
                }

                if(res.data['event'] == 'update'){
                  // document.getElementById('successMsg').hidden = false
                  // document.getElementById('successMsg').innerHTML = '<i class="far fa-check-circle"></i> User Updated'

                  var userData = document.getElementById('userNameField_'+ res.data['userid'])
                  var userLocation = document.getElementById('userLocation_'+ res.data['userid'])
                  userData.innerText = res.data['name']
                  userData.dataset.username = res.data['name']
                  userData.dataset.userpwd = res.data['pswd']
                  userLocation.dataset.userlocation = res.data['location']
                  // newUserLocation = location

                  // showSuccessMessage('User Updated');

                  // setInterval(function() {
                    $('#close_add_user_modal').click();
                  // }, 2000);

                }

              }
          }
        }
        
    }).fail(function (error) {
    });
    
  }
}


function openNewUserModal() {

  // Hide all validations initially
  document.getElementById('NewUserNameValidation').hidden = true
  document.getElementById('newUserEmailValidation').hidden = true
  document.getElementById('NewUserpasswordValidation').hidden = true
  document.getElementById('newUserRoleValidation').hidden = true

  document.getElementById('UserCreateAndEditModal').innerText = 'New User'
  document.getElementById('newUserName').value = ''
  document.getElementById('newUserEmail').value = ''
  document.getElementById('newUserLocation').value = ''

  document.getElementById('saveUser_').dataset.updateorcreate = 'create'
  document.getElementById('newUserEmail').disabled = false
  document.getElementById('newUserRoleContainer').hidden = false
  document.getElementById('userRoleEditContainer').hidden = true
  document.getElementById('newUserPassword').value = generateStrongPassword()

  const modalElement = document.getElementById('AddNewUserModal');
  const modal = new bootstrap.Modal(modalElement);
  modal.show();

}


function openEditUserModal(editUserId){
  document.getElementById('UserCreateAndEditModal').innerText = 'Edit User'
  // Hide all validations initially
  document.getElementById('NewUserNameValidation').hidden = true
  document.getElementById('newUserEmailValidation').hidden = true
  document.getElementById('NewUserpasswordValidation').hidden = true

  document.getElementById('saveUser_').dataset.updateorcreate = 'update'
  document.getElementById('newUserRoleContainer').hidden = true;

  // Extraction data from HTML INPUTS
  var editUserName = document.getElementById('userNameField_' + editUserId).dataset.username;
  var editUserEmail = document.getElementById('userNameField_' + editUserId).dataset.useremail;
  var editUserpswd = document.getElementById('userNameField_'+editUserId).dataset.userpwd;
  var editUserRole = document.getElementById('userRoleField_'+editUserId).dataset.userrole;
  var editUserLocation = document.getElementById('userLocation_'+editUserId).dataset.userlocation;
  // var editUserStatus = document.getElementById('userStatus_'+editUserId).dataset.userstatus;

  editUserRole = editUserRole.trim();

  document.getElementById('newUserEmail').disabled = true
  var editRoleInpt = document.getElementById('userRoleEdit')
  editRoleInpt.disabled = true
  editRoleInpt.value = editUserRole
  document.getElementById('userRoleEditContainer').hidden = false

  document.getElementById('newUserName').value = editUserName
  document.getElementById('newUserEmail').value = editUserEmail
  document.getElementById('newUserPassword').value = editUserpswd
  document.getElementById('newUserLocation').value = editUserLocation
  // document.getElementById('newUserRole').value = editUserStatus

  const modalElement = document.getElementById('AddNewUserModal');
  const modal = new bootstrap.Modal(modalElement);
  modal.show();
}


function validateEmail(email) {
  // Regular expression pattern for basic email validation
  const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  // Return true if the email matches the pattern, otherwise false
  return emailPattern.test(email);
}


function sanitizePassword() {
  const inputField = document.getElementById("newUserPassword");
  inputField.value = inputField.value.replace(/\s+/g, ''); // Removes all spaces
}


function generateStrongPassword() {
  length = 15
  const upperCase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  const lowerCase = "abcdefghijklmnopqrstuvwxyz";
  const numbers = "0123456789";
  // const symbols = "!@#$%^&*()_+[]{}|;:,.<>?";

  // const allCharacters = upperCase + lowerCase + numbers + symbols;
  const allCharacters = upperCase + lowerCase + numbers;

  let password = "";
  
  // Ensure the password contains at least one character from each set
  password += upperCase[Math.floor(Math.random() * upperCase.length)];
  password += lowerCase[Math.floor(Math.random() * lowerCase.length)];
  password += numbers[Math.floor(Math.random() * numbers.length)];
  // password += symbols[Math.floor(Math.random() * symbols.length)];

  // Fill the rest of the password length with random characters
  for (let i = password.length; i < length; i++) {
      password += allCharacters[Math.floor(Math.random() * allCharacters.length)];
  }

  // Shuffle the password to avoid a predictable pattern
  password = password.split('').sort(() => Math.random() - 0.5).join('');

  return password;
}

function changeUserStatus(elementid){
  var element = document.getElementById(elementid)
  var userStatusChange = ''
  userId = elementid.split('_')[1]
  var userStatus = document.getElementById(elementid).checked
  
  if(userStatus){
    userStatusChange = 'A'
    element.title = 'Active';
  }
  else{
    userStatusChange = 'I'
    element.title = 'Inactive';
  }

  var dataObj = {
    "userid"  :  userId,
    "status": userStatusChange,
    };

  var final_data = {
      'data': JSON.stringify(dataObj),
      csrfmiddlewaretoken: CSRF_TOKEN,
  };

  $.post(CONFIG['portal'] + "/api/change-user-status", final_data, function (res) {

  });


}