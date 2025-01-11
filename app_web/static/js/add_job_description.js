// var libraryId
// var selectValidJd
var technologiesList = languages
var jdSelectedSkillsList = []

// document.addEventListener('DOMContentLoaded', function() {
//     // fetchJdLibrarys();

//     const searchInput = document.getElementById('searchNewSkill');
//     const suggestionsBox = document.getElementById('suggestionsBox');
//     // const promptMessage = document.getElementById('promptMessage');

//     // Function to show suggestions based on the search input
//     function showSuggestions() {
//         const query = searchInput.value.trim().toLowerCase();

//         // Display prompt message if less than 3 characters are entered
//         if (query.length < 3) {
//             suggestionsBox.style.display = "none";
//             return;
//         }

//         // Clear previous suggestions
//         suggestionsBox.innerHTML = '';
//         var filteredDescriptions = technologiesList;
//         // Show suggestions or "No job descriptions found" if none match
//         if (filteredDescriptions.length > 0) {
//             let suggestionsHTML = '';

//             // Loop through the filtered descriptions and build the HTML string
//             for (let i = 0; i < filteredDescriptions.length; i++) {
//                 const skill = filteredDescriptions[i];

//                 suggestionsHTML += `
//                     <div class="suggestion-item p-2 search_item" 
//                          style="cursor: pointer;" 
//                          onclick="selectJd(${skill})"
//                          >
//                         ${skill}
//                     </div>
//                 `;
//             }

//             // Insert the suggestions into the suggestions box
//             suggestionsBox.innerHTML = suggestionsHTML;
//         } else {
//             suggestionsBox.innerHTML = `<div class="p-2 text-muted">No job descriptions found</div>`;
//         }

//         // Display the suggestions box
//         suggestionsBox.style.display = "block";
//     }

//     // Trigger suggestions on input and focus
//     searchInput.addEventListener('input', showSuggestions);
//     searchInput.addEventListener('focus', showSuggestions);

//     // Hide suggestions on outside click
//     document.addEventListener('click', function(e) {
//         if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
//             suggestionsBox.style.display = "none";
//         }
//     });

//     // Add click event to select a suggestion
//     suggestionsBox.addEventListener('click', function(e) {
//         if (e.target.classList.contains('suggestion-item')) {
//             searchInput.value = e.target.textContent.trim();
//             searchInput.blur();
//             suggestionsBox.style.display = "none";
//         }
// });

// // Function to append JD libraries
// // function appendJdLibraryToHtml(jdLibrarys) {
// //     JDLibrarys = technologies;
// // }


// // appendJdLibraryToHtml(data.data); 


// // Initialize select2 on jdLibrary
// // $(document).ready(function () {
// //     $('#jdLibrary').select2({
// //             placeholder: "Please Select Job Description",
// //             allowClear: true
// //         });
// //     });
// });

// =====================================
// working for list
// document.addEventListener('DOMContentLoaded', function() {
//     const searchInput = document.getElementById('searchNewSkill');
//     const suggestionsBox = document.getElementById('suggestionsBox');

//     // Function to show suggestions based on the search input
//     function showSuggestions() {
//         const query = searchInput.value.trim().toLowerCase();

//         // Display prompt message if less than 3 characters are entered
//         if (query.length < 1) {
//             suggestionsBox.style.display = "none";
//             return;
//         }

//         // Filter the technologies list based on the query
//         const skillsList = technologiesList.filter(skill =>
//             skill.toLowerCase().includes(query) // Match skill names with query
//         );

//         // Clear previous suggestions
//         suggestionsBox.innerHTML = '';

//         // Show suggestions or "No job descriptions found" if none match
//         if (skillsList.length > 0) {
//             let suggestionsHTML = '';

//             // Loop through the filtered descriptions and build the HTML string
//             for (let i = 0; i < skillsList.length; i++) {
//                 const skill = skillsList[i];

//                 suggestionsHTML += `
//                     <div class="suggestion-item p-2 search_item" 
//                          style="cursor: pointer;" 
//                          onclick="selectedSkill('${skill}')">
//                         ${skill}
//                     </div>
//                 `;
//             }

//             // Insert the suggestions into the suggestions box
//             suggestionsBox.innerHTML = suggestionsHTML;
//         } else {
//             suggestionsBox.innerHTML = `<div class="p-2 text-muted">Skill Not Found</div>`;
//         }

//         // Display the suggestions box
//         suggestionsBox.style.display = "block";
//     }

//     // Trigger suggestions on input and focus
//     searchInput.addEventListener('input', showSuggestions);
//     searchInput.addEventListener('focus', showSuggestions);

//     // Hide suggestions on outside click
//     document.addEventListener('click', function(e) {
//         if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
//             suggestionsBox.style.display = "none";
//         }
//     });

//     // Add click event to select a suggestion
//     suggestionsBox.addEventListener('click', function(e) {
//         if (e.target.classList.contains('suggestion-item')) {
//             searchInput.value = e.target.textContent.trim();
//             searchInput.blur();
//             suggestionsBox.style.display = "none";
//             document.getElementById('searchNewSkill').value = '';
//             document.getElementById('searchNewSkill').focus()
//         }
//     });

//     // hide and unhide the empty skills container
//     emptySkillsContainer()

// });


document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchNewSkill');
    const suggestionsBox = document.getElementById('suggestionsBox');

    // Function to show suggestions based on the search input
    function showSuggestions() {
        const query = searchInput.value.trim().toLowerCase();

        // Display prompt message if less than 1 character is entered
        if (query.length < 1) {
            suggestionsBox.style.display = "none";
            return;
        }

        // Filter the object keys based on the query
        const skillsList = Object.keys(technologiesList).filter(skill =>
            skill.toLowerCase().includes(query) // Match skill names (keys) with query
        );

        // Clear previous suggestions
        suggestionsBox.innerHTML = '';

        // Show suggestions or "Skill Not Found" if none match
        if (skillsList.length > 0) {
            let suggestionsHTML = '';

            // Loop through the filtered skills (keys) and build the HTML string
            for (let i = 0; i < skillsList.length; i++) {
                const skill = skillsList[i];

                suggestionsHTML += `
                    <div class="suggestion-item p-2 search_item" 
                         style="cursor: pointer;" 
                         onclick="selectedSkill('${skill}')">
                        ${skill}
                    </div>
                `;
            }

            // Insert the suggestions into the suggestions box
            suggestionsBox.innerHTML = suggestionsHTML;
        } else {
            suggestionsBox.innerHTML = `<div class="p-2 text-muted">Skill Not Found</div>`;
        }

        // Display the suggestions box
        suggestionsBox.style.display = "block";
    }

    // Trigger suggestions on input and focus
    searchInput.addEventListener('input', showSuggestions);
    searchInput.addEventListener('focus', showSuggestions);

    // Hide suggestions on outside click
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.style.display = "none";
        }
    });

    // Add click event to select a suggestion
    suggestionsBox.addEventListener('click', function(e) {
        if (e.target.classList.contains('suggestion-item')) {
            searchInput.value = e.target.textContent.trim();
            searchInput.blur();
            suggestionsBox.style.display = "none";
            document.getElementById('searchNewSkill').value = '';
            document.getElementById('searchNewSkill').focus()
        }
    });

    // hide and unhide the empty skills container
    emptySkillsContainer();
});




// hide and unhide the empty skills container
function emptySkillsContainer(){
    var skillscontainer = document.getElementById('skillsListMainContainer')
    if(skillscontainer.childNodes.length == 1){
        document.getElementById('jdSkillsContainer').hidden = true
    }
    else{
        document.getElementById('jdSkillsContainer').hidden = false
    }
}

// // selected jd skill 
// function selectedSkill(skillIteam) {

//     // Create a new skill iteam container div
//     var skillContainer = document.createElement('div');
//     skillContainer.className = 'skillIteamContainer';
    
//     skillContainer.id = skillIteam.replace('.','_');
//     skillContainer.innerHTML = `
//         <div class="skillTitle">${skillIteam}</div>
//         <div id="removeSkill">
//             &nbsp;&nbsp;&nbsp; 
//             <i class="fas fa-times customremovecls" onclick="removeSkill(${skillIteam.replace('.','_')})"></i>
//         </div>`;
    
//     jdSelectedSkillsList.push(skillIteam)

//     document.getElementById('skillsListMainContainer').appendChild(skillContainer);

//     // Find the Skill Index number
//     let index = technologiesList.indexOf(skillIteam);

//     // Check if skill index number was not less than -1
//     if (index !== -1) {
//         technologiesList.splice(index, 1); // Remove 'Skill' from Technologys List
//     }

//     // hide and unhide the empty skills container
//     emptySkillsContainer()

// }


function selectedSkill(skillIteam) {
    // Create a new skill item container div
    var skillContainer = document.createElement('div');
    skillContainer.className = 'skillIteamContainer';

    skillContainer.id = skillIteam.replace('.', '_');
    skillContainer.innerHTML = `
        <div class="skillTitle">${skillIteam}</div>
        <div id="removeSkill">
            &nbsp;&nbsp;&nbsp; 
            <i class="fas fa-times customremovecls" onclick="removeSkill('${skillIteam.replace('.', '_')}')"></i>
        </div>`;

    // creating dictionary to put in list
    var addNewSkill = {[skillIteam] : languages[skillIteam]}
    
    // Add to selected skills list
    jdSelectedSkillsList.push(addNewSkill);
    
    document.getElementById('skillsListMainContainer').appendChild(skillContainer);

    delete technologiesList[skillIteam];

    // Remove the skill from the languages object (equivalent to removing from the technologiesList)
    // if (technologiesList.hasOwnProperty(skillIteam)) {
    //     delete technologiesList[skillIteam]; // Remove selected skill from languages object
    // }

    // hide and unhide the empty skills container
    emptySkillsContainer();
}



// // remove skill from the jd skills
// function removeSkill(rmSkill) {
//     // Find the element to remove
//     var rmElement = document.getElementById(rmSkill.id);
//     var skillTitle = rmSkill.querySelectorAll('.skillTitle')[0].innerText

//     if (rmElement) {
//         // Remove the element from the DOM
//         rmElement.remove();

//         // Remove the skill from the selected skills list
//         var rmJdSkill = jdSelectedSkillsList.indexOf(skillTitle);
//         if (rmJdSkill !== -1) {
             
//             // Remove the skill from the selected jD skills
//             jdSelectedSkillsList.splice(rmJdSkill, 1); 
            
//             // Adding skill to technologies list 
//             technologiesList.push(skillTitle)

//         }
//     }

//     // hide and unhide the empty skills container
//     emptySkillsContainer();
// }


// function removeSkill(rmSkill) {
//     // Find the element to remove
//     var rmElement = document.getElementById(rmSkill);

//     var skillTitle = rmElement.querySelectorAll('.skillTitle')[0].innerText;

//     if (rmElement) {
//         // Remove the element from the DOM
//         rmElement.remove();
        
//         // adding the skill again to technologys list
//         // dictionary   key            value
//         technologiesList[skillTitle] = languages[skillTitle]
//     }

//     console.log('before :: ',jdSelectedSkillsList);

//     for (let skillCount = 0; skillCount < jdSelectedSkillsList.length; skillCount++) {
//         const skillItem = jdSelectedSkillsList[skillCount];
//         console.log('fnndd',skillItem, 'skillTitle :: ',skillTitle, skillItem[skillTitle])
//     }

//     console.log('after :: ',jdSelectedSkillsList, );

//     // Hide and unhide the empty skills container
//     emptySkillsContainer();
// }


function removeSkill(rmSkill) {
    // Find the element to remove
    var rmElement = document.getElementById(rmSkill);

    var skillTitle = rmElement.querySelectorAll('.skillTitle')[0].innerText;

    if (rmElement) {
        // Remove the element from the DOM
        rmElement.remove();
        
        // adding the skill again to technologies list
        // dictionary   key            value
        technologiesList[skillTitle] = languages[skillTitle];
    }

    // Iterate over the jdSelectedSkillsList
    for (let skillCount = 0; skillCount < jdSelectedSkillsList.length; skillCount++) {
        const skillItem = jdSelectedSkillsList[skillCount];
        
        // Check if skillTitle exists in skillItem
        if (skillItem && skillItem.hasOwnProperty(skillTitle)) {
            delete skillItem[skillTitle];
        }
    }

    // Remove empty dictionaries from jdSelectedSkillsList
    jdSelectedSkillsList = jdSelectedSkillsList.filter(skillItem => Object.keys(skillItem).length > 0);

    // Hide and unhide the empty skills container
    emptySkillsContainer();
}



// Function to fill JD on Inputs
// function selectJd(jdId) {
//     selectValidJd = true
//     var hrSelectedValue = jdId
//     if (hrSelectedValue) {  // Check HR value
//         if (JDLibrarys.length > 0) {  // Check JD library data
//             for (var jd = 0; jd < JDLibrarys.length; jd++) {
//                 if (hrSelectedValue == JDLibrarys[jd].id) {
//                     libraryId = hrSelectedValue
//                     document.getElementById('JobDescription').innerText = JDLibrarys[jd].description ? JDLibrarys[jd].description : "";
//                     document.getElementById('min_experince').value = JDLibrarys[jd].minexp ? JDLibrarys[jd].minexp : "";
//                     document.getElementById('max_experince').value = JDLibrarys[jd].maxexp ? JDLibrarys[jd].maxexp : "";
//                     document.getElementById('jdSkills').innerText = JDLibrarys[jd].skill ? JDLibrarys[jd].skill : "";

//                     // Get the role value from the JDLibrarys object
//                     const roleValue = JDLibrarys[jd].role ? JDLibrarys[jd].role : "";

//                     // Get the select element
//                     const roleSelect = document.getElementById('jdRole');

//                     // Iterate through all options in the select element
//                     for (let i = 0; i < roleSelect.options.length; i++) {
//                         // If the option value matches the roleValue, select it
//                         if (roleSelect.options[i].value === roleValue) {
//                             roleSelect.selectedIndex = i; // Set the selected index
//                             break; // Exit the loop once the matching option is found
//                         }
//                     }
//                     break
//                 }
               
//             }

//         }
//     }
// }


// Clear all input fields in JD
function resetJd(){
    // selectValidJd = false
    // libraryId = ''
    document.querySelectorAll("input").forEach(input => input.value = "");
    document.querySelectorAll("select").forEach(select => select.selectedIndex = 0);
    document.querySelectorAll("textarea").forEach(textarea => textarea.value = "");
    showSuccessMessage('Jd cleared');
}


// saving JD
document.getElementById('addJD').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    // if (selectValidJd){ // verifying jd is selected or not selected
        
        const jdValues = {
            title: document.getElementById('jdTitle').value,
            // jdLibraryId : libraryId,
            jobDesc: document.getElementById('JobDescription').value,
            role: document.getElementById('jdRole').value,
            minExp: document.getElementById('min_experince').value,
            maxExp: document.getElementById('max_experince').value,
            budget: document.getElementById('jdBudget').value,
            noPositions: document.getElementById('jdNoPositions').value,
            workLocation: document.getElementById('jdWorkLocation').value,
            skills: jdSelectedSkillsList,
            anySpecialNote: document.getElementById('JdanySpecialNotes').value
        };

        // Prepare data to be sent to the backend
        var final_data = {
            "data": JSON.stringify(jdValues),
            csrfmiddlewaretoken: CSRF_TOKEN,
        };

        try {
            $.post(CONFIG['portal'] + "/api/add-jd", final_data, function(res) {
                if (res.statusCode == 0) {
                    var newjdid = res.data['newJdId']
                    document.getElementById('validater').hidden = false;
                    setInterval(3000)
                    window.location.href = '/job-description-set-up/'+newjdid;
                }
            });
        } catch (error) {
            console.error('Failed to send data to backend:', error);
        }

    // }
    
});


// function autocomplete(inp, arr) {
//     /*the autocomplete function takes two arguments,
//     the text field element and an array of possible autocompleted values:*/
//     var currentFocus;
//     /*execute a function when someone writes in the text field:*/
//     inp.addEventListener("input", function(e) {
//         var a, b, i, val = this.value;
//         /*close any already open lists of autocompleted values*/
//         closeAllLists();
//         if (!val) { return false;}

//         currentFocus = -1;
//         /*create a DIV element that will contain the items (values):*/
//         a = document.createElement("DIV");
//         a.setAttribute("id", this.id + "autocomplete-list");
//         a.setAttribute("class", "autocomplete-items");
//         /*append the DIV element as a child of the autocomplete container:*/
//         this.parentNode.appendChild(a);

//         /*for each item in the array...*/
//         var matchingString = 0
//         for (i = 0; i < arr.length; i++) {
//             /*check if the item starts with the same letters as the text field value:*/
//             if (arr[i].substr(0, val.length).toUpperCase() == val.toUpperCase()) {
//                 /*create a DIV element for each matching element:*/
//                 b = document.createElement("DIV");
//                 /*make the matching letters bold:*/
//                 b.innerHTML = "<strong>" + arr[i].substr(0, val.length) + "</strong>";
//                 b.innerHTML += arr[i].substr(val.length);
//                 /*insert a input field that will hold the current array item's value:*/
//                 b.innerHTML += "<input type='hidden' value='" + arr[i] + "'>";
//                 /*execute a function when someone clicks on the item value (DIV element):*/
//                 b.addEventListener("click", function(e) {
//                     /*insert the value for the autocomplete text field:*/
//                     inp.value = this.getElementsByTagName("input")[0].value;
//                     /*close the list of autocompleted values,
//                     (or any other open lists of autocompleted values:*/
//                     closeAllLists();
//                 });
//                 matchingString += 1

//                 if(matchingString > 3){
//                     const items = document.getElementsByClassName('autocomplete-items');
//                     for (let item of items) {
//                         item.style.height = '130px';
//                         item.style.overflowY = 'scroll';
//                     }
//                 } 
//                 else{
//                     const items = document.getElementsByClassName('autocomplete-items');
//                     for (let item of items) {
//                         item.style.height = 'max-content';
//                         item.style.overflowY = 'hidden';
//                     }
//                 }

//                 a.appendChild(b);
//             }
//             else{
//                 console.log('Nothing Found');
//             }
//         }
//     });

//     /*execute a function presses a key on the keyboard:*/
//     inp.addEventListener("keydown", function(e) {
//         var x = document.getElementById(this.id + "autocomplete-list");
//         if (x) x = x.getElementsByTagName("div");
//         if (e.keyCode == 40) {
//           /*If the arrow DOWN key is pressed,
//           increase the currentFocus variable:*/
//           currentFocus++;
//           /*and and make the current item more visible:*/
//           addActive(x);
//         } else if (e.keyCode == 38) { //up
//           /*If the arrow UP key is pressed,
//           decrease the currentFocus variable:*/
//           currentFocus--;
//           /*and and make the current item more visible:*/
//           addActive(x);
//         } else if (e.keyCode == 13) {
//           /*If the ENTER key is pressed, prevent the form from being submitted,*/
//           e.preventDefault();
//           if (currentFocus > -1) {
//             /*and simulate a click on the "active" item:*/
//             if (x) x[currentFocus].click();
//           }
//         }
//     });

//     function addActive(x) {
//       /*a function to classify an item as "active":*/
//       if (!x) return false;
//       /*start by removing the "active" class on all items:*/
//       removeActive(x);
//       if (currentFocus >= x.length) currentFocus = 0;
//       if (currentFocus < 0) currentFocus = (x.length - 1);
//       /*add class "autocomplete-active":*/
//       x[currentFocus].classList.add("autocomplete-active");
//     }
//     function removeActive(x) {
//       /*a function to remove the "active" class from all autocomplete items:*/
//       for (var i = 0; i < x.length; i++) {
//         x[i].classList.remove("autocomplete-active");
//       }
//     }
//     function closeAllLists(elmnt) {
//       /*close all autocomplete lists in the document,
//       except the one passed as an argument:*/
//       var x = document.getElementsByClassName("autocomplete-items");
//       for (var i = 0; i < x.length; i++) {
//         if (elmnt != x[i] && elmnt != inp) {
//           x[i].parentNode.removeChild(x[i]);
//         }
//       }
//     }

//     /*execute a function when someone clicks in the document:*/
//     document.addEventListener("click", function (e) {
//         closeAllLists(e.target);
//     });
// }
  
//   /*initiate the autocomplete function on the "myInput" element, and pass along the countries array as possible autocomplete values:*/
//   autocomplete(document.getElementById("searchNewSkill"), technologiesList);


// Function to fetch data from the Django API
// async function fetchJdLibrarys() {
//     try {
//         // Send a GET request to the API endpoint
//         const response = await fetch(CONFIG['acert'] + "/api/jd-librarys", {
//             method: 'GET',
//             headers: {
//                 'Content-Type': 'application/json'
//             }
//         });

//         if (!response.ok) {
//             throw new Error(`Error: ${response.status}`);
//         }

//         const data = await response.json();

//         // Call appendJdLibraryToHtml with the fetched data
//         appendJdLibraryToHtml(data.data);  // Assuming `data.data` holds the actual array of JD libraries

//     } catch (error) {
//         console.error('Failed to fetch jd-libraries:', error);
//     }
// }