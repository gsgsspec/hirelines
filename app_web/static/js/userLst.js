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
  
  var newUserName_ = document.getElementById('newUserName').value;
  var newUserPassword_ = document.getElementById('newUserPassword').value;
  var newUserEmail_ = document.getElementById('newUserEmail').value;
  var newUserRole_ = document.getElementById('newUserRole').value;
  var newUserLocation_ = document.getElementById('newUserLocation').value;
  
  var NewUserDataValidation = true;  // Initialize as true, and set to false if any validation fails

  // Username validation
  if (newUserName_ === "") {
    NewUserDataValidation = false;
    document.getElementById('NewUserNameValidation').hidden = false;
  } else {
    document.getElementById('NewUserNameValidation').hidden = true;
  }

  // Password validation
  var newUserPasswordValid = document.getElementById('NewUserpasswordValidation');
  if (newUserPassword_ === "") {
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

  // Email validation
  var emailValidation = document.getElementById('newUserEmailValidation');
  if (newUserEmail_ === "") {
    NewUserDataValidation = false;
    emailValidation.innerText = 'Email address is required';
    emailValidation.hidden = false;
  } else {
    var checkMail = validateEmail(newUserEmail_);
    if (checkMail === false) {
      NewUserDataValidation = false;
      emailValidation.innerText = 'Valid email is required';
      emailValidation.hidden = false;
    } else {
      emailValidation.hidden = true;
    }
  }

  // Role validation
  if (newUserRole_ === "Select Role") {
    NewUserDataValidation = false;
    document.getElementById('newUserRoleValidation').hidden = false;
  } else {
    document.getElementById('newUserRoleValidation').hidden = true;
  }

  // Check final validation status
  if (NewUserDataValidation == true) {
    
    var dataObj = {
    "userName" :  newUserName_,
    "userPswd" :  newUserPassword_,
    "userEmail" :  newUserEmail_,
    "userRole" :  newUserRole_,
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

                var newUser = document.createElement('tr');
                newUser.innerHTML = `
                <td><strong>${newUserName_}</strong></td>
                <td>${newUserRole_}</td>
                <td>${newUserLocation_}</td>
                <td>
                    <span class="badge bg-label-success me-1">
                        Active 
                    </span>
                </td>
                `;

                var userListTable = document.getElementById('userListTabelList');
                userListTable.insertBefore(newUser, userListTable.firstChild);

                $('#close_add_user_modal').click();

              }
          }
        }
        
    }).fail(function (error) {
    });
    
  }
}


function openEditUserModal(){
  
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


function openNewUserModal() {
  
  // var passwordInpt = document.getElementById('newUserPassword')
  // if(passwordInpt.value == ""){
    document.getElementById('newUserPassword').value = generateStrongPassword()
  // }

  const modalElement = document.getElementById('AddNewUserModal');
  const modal = new bootstrap.Modal(modalElement);
  modal.show();
}


function generateStrongPassword() {
  length = 15
  const upperCase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
  const lowerCase = "abcdefghijklmnopqrstuvwxyz";
  const numbers = "0123456789";
  const symbols = "!@#$%^&*()_+[]{}|;:,.<>?";

  const allCharacters = upperCase + lowerCase + numbers + symbols;

  let password = "";
  
  // Ensure the password contains at least one character from each set
  password += upperCase[Math.floor(Math.random() * upperCase.length)];
  password += lowerCase[Math.floor(Math.random() * lowerCase.length)];
  password += numbers[Math.floor(Math.random() * numbers.length)];
  password += symbols[Math.floor(Math.random() * symbols.length)];

  // Fill the rest of the password length with random characters
  for (let i = password.length; i < length; i++) {
      password += allCharacters[Math.floor(Math.random() * allCharacters.length)];
  }

  // Shuffle the password to avoid a predictable pattern
  password = password.split('').sort(() => Math.random() - 0.5).join('');

  return password;
}
