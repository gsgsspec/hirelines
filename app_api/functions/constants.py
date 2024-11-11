from hirelines.metadata import getConfig


public_email_domains = [
    "gmail.com", "yahoo.com", "hotmail.com", "aol.com", "outlook.com", "icloud.com", "mail.com", "zoho.com", "protonmail.com",
    "yandex.com", "gmx.com", "fastmail.com", "tutanota.com", "mail.ru", "hushmail.com", "airmail.net", "lycos.com", "netcourrier.com",
    "zimbra.com", "rediffmail.com", "mailinator.com"
]

company_types = [
    "Software Development Company", "HR Consultancy", "Software Product Company", "Enterprise", "Others"
]

const_candidate_status = {
    "O": 'Offered',
    "H": 'Hold',
    "R": 'Rejected',
    "P": 'Initiated',
    "S": 'Screened',
    "E": 'Test Done',
    "I": 'Interviewed',
}


const_paper_types = {
    "S": 'Screening Test',
    "E": 'Coding Test',
    "I": 'Interview Test',
}


hirelines_domain = getConfig()['DOMAIN']['hirelines']

hirelines_integration_script = """<!-- hirelines registration script -->
<!-- Script tag to be added under `<head></head>` tag -->
<script src="#hirelines_domain#/api/candidate-registration-cdn/#enc_jdid#/"></script>
""".replace("#hirelines_domain#", hirelines_domain)

hirelines_integration_function = f"""/* function to be added while posting candidate job application (under related .js or script tags) */
hirelinescanreg('#enc_jdid#');
"""



          
hirelines_registration_script ="""
        function hirelinescanreg(encjdid) {
    var inputs = document.querySelectorAll('input');

    var firstName = '';
    var lastName = '';
    var name = '';
    var email = '';
    var mobile = '';

    inputs.forEach(function(input) {
        var inputValue = input.value;
        var inputType = input.type;
        var inputName = input.name;
        var inputId = input.id;

        if (inputType === 'text' && (inputName && (inputName.toLowerCase().includes('first') || inputName.toLowerCase().includes('fname') || inputName.toLowerCase().includes('firstname')) || inputId && (inputId.toLowerCase().includes('first') || inputId.toLowerCase().includes('fname') || inputId.toLowerCase().includes('firstname')))) {
            firstName = inputValue;
        }
        if (inputType === 'text' && (inputName && (inputName.toLowerCase().includes('last') || inputName.toLowerCase().includes('lname') || inputName.toLowerCase().includes('lastname')) || inputId && (inputId.toLowerCase().includes('last') || inputId.toLowerCase().includes('lname') || inputId.toLowerCase().includes('lastname')))) {
            lastName = inputValue;
        }
        if (inputType === 'email' || (inputName && inputName.toLowerCase().includes('mail')) || (inputId && inputId.toLowerCase().includes('mail'))) {
            email = inputValue;
        }
        if (inputType === 'tel' || (inputType === 'text' && (inputName && (inputName.toLowerCase().includes('mobile') || inputName.toLowerCase().includes('contact') || inputName.toLowerCase().includes('phone')) || (inputId && (inputId.toLowerCase().includes('mobile') || inputId.toLowerCase().includes('contact') || inputId.toLowerCase().includes('phone')))))) {
            mobile = inputValue;
        }
        if (firstName || lastName) {
            name = (firstName ? firstName : "") + (lastName ? lastName : "");
        } else {
            if (inputType === 'text' && (inputName && (inputName.toLowerCase().includes('candidatename') || inputName.toLowerCase().includes('applicantname') || inputName.toLowerCase().includes('name')) || (inputId && (inputId.toLowerCase().includes('candidatename') || inputId.toLowerCase().includes('applicantname') || inputId.toLowerCase().includes('name'))))) {
                name = inputValue;
                firstName = name;
                lastName = " ";
            }
        }
    });

    console.log("First Name:", firstName);
    console.log("Last Name:", lastName);
    console.log("Name:", name);
    console.log("Email:", email);
    console.log("Mobile:", mobile);
    
    var payload = {
        "encjdid": encjdid,
        "firstname": firstName,
        "lastname": lastName,
        "email": email,
        "mobile": mobile
    };
    register_candidate(payload);
}

function register_candidate(register_details) {
    fetch("#hirelines_domain#/api/register-candidate", {
        method: "POST",
        body: JSON.stringify(register_details),
        headers: {
            "Content-Type": "application/json; charset=UTF-8"
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.statusCode == 0) {
            // applicationForm.reset()
            // alert('Application submitted successfully. Please check your email.');
        } else {
            // alert('Error while applying for this job. Please reach out to our company email');
            console.log('Error', data.error);
        }
    })
    .catch(error => {
        // alert('Error while applying for this job. Please reach out to our company email');
        console.log('Error', error);
    });
}

""".replace("#hirelines_domain#", hirelines_domain)

          
# hirelines_registration_script ="""
#         function hirelinescanreg(encjdid) {
            
#             var inputs = $('input');

#             var firstName = '';
#             var lastName = '';
#             var name = '';
#             var email = '';
#             var mobile = '';

            
#             inputs.each(function() {
#             var inputValue = $(this).val();  
#             var inputType = $(this).attr('type');
#             var inputName = $(this).attr('name');
#             var inputId = $(this).attr('id');
#             var inputValue = $(this).val();

            
#             if (inputType === 'text' && (inputName && (inputName.toLowerCase().includes('first') || inputName.toLowerCase().includes('fname') || inputName.toLowerCase().includes('firstname')) || inputId && (inputId.toLowerCase().includes('first') || inputId.toLowerCase().includes('fname') || inputId.toLowerCase().includes('firstname')))) {
#                 firstName = inputValue; 

            
#             } 
#             if (inputType === 'text' && (inputName && (inputName.toLowerCase().includes('last')  || inputName.toLowerCase().includes('lname') || inputName.toLowerCase().includes('lastname')) || inputId && (inputId.toLowerCase().includes('last') || inputId.toLowerCase().includes('lname') || inputId.toLowerCase().includes('lastname')))) {
#                 lastName = inputValue; 

            
#             } 
                
#             if (inputType === 'email' || inputName && inputName.toLowerCase().includes('mail') || inputId && inputId.toLowerCase().includes('mail')) {
#                 email = inputValue; 

            
#             } 
#             if (inputType === 'tel' || inputType === 'text' && (inputName && (inputName.toLowerCase().includes('mobile') || inputName.toLowerCase().includes('contact') || inputName.toLowerCase().includes('phone')) || inputId && (inputId.toLowerCase().includes('mobile') || inputId.toLowerCase().includes('contact') || inputId.toLowerCase().includes('phone')))) {
#                 mobile = inputValue; 
#             }
#             if (firstName || lastName) {
#                 name = (firstName ? firstName : "") + (lastName ? lastName : "");
#             // console.log("f&l",name);
            
#             } else {
#                 if (inputType === 'text' && (inputName && (inputName.toLowerCase().includes('candidatename') || inputName.toLowerCase().includes('applicantname') || inputName.toLowerCase().includes('name'))  || inputId && (inputId.toLowerCase().includes('candidatename') || inputId.toLowerCase().includes('applicantname') || inputId.toLowerCase().includes('name')))) {
#                     name = inputValue; 
#                     firstName= name;
#                     lastName = " "
#                 }
            
#             }
#             });

            
            
#             console.log("First Name:", firstName); 
#             console.log("Last Name:", lastName); 
#             console.log("Name:", name); 
#             console.log("Email:", email);
#             console.log("Mobile:", mobile);
#             payload = {
#                 "encjdid":encjdid,
#                 "firstname":firstName,
#                 "lastname":lastName,
#                 "email":email,
#                 "mobile":mobile
#             }
#             register_candidate(payload);
#         }

#         function register_candidate(register_details){
#             fetch("#hirelines_domain#/api/register-candidate", {       
#                 method: "POST",
#                 body: JSON.stringify(register_details),
#                 headers: {
#                     "Content-type": "application/json; charset=UTF-8"
#                 }
#             }).then(response => {
#                 if (!response.ok) {
#                     throw new Error('Network response was not ok');
                    
#                 }
#                 return response.json();
#             })
            
#             .then(data => {
#                 if(data.statusCode == 0){
#                     // applicationForm.reset()
#                     // alert('Application submitted successfully. Please check your email.');
#                 }
#                 else{
#                 // alert('Error while appling for this job. Please reach out our company email');
#                 console.log('Error', + error.error)
                
#                 }
                
#             })
#             .catch(error => {
#                 // alert('Error while appling for this job. Please reach out our company email');
#                 console.log('Error', + error.error)
                
#             });
#         }
# """.replace("#hirelines_domain#", hirelines_domain)