
            const CONFIG = {
                'portal': '' 
            };
           function extractCandidateIdFromCurrentUrl() {
            // Get the current path (e.g., /candidate-schedule-interview/yqxNWI6cifM8iNOLExKzcg==/)
            const path = window.location.pathname; 
            const prefix = "/candidate-schedule-interview/";

            if (path.includes(prefix)) {
                // Split by the prefix and take the second part (the ID)
                let id = path.split(prefix)[1]; 
                
                // Remove trailing slash if it exists
                if (id && id.endsWith('/')) {
                    id = id.slice(0, -1);
                }
                
                return id;
            }
            return null;
        }

        // Example of how to use this function in the browser:
        const candidateID = extractCandidateIdFromCurrentUrl();

        if (candidateID !== null) {
            console.log(`Successfully extracted ID from the browser URL: ${candidateID}`);
            // You can now use this ID to make an API call, update the UI, etc.
            
            // --- Example of updating an element on the page ---
            const element = document.getElementById('candidate-id-display');
            if (element) {
                element.textContent = candidateID;
            }
            // ----------------------------------------------------

        } else {
            console.log("Could not find a valid candidate ID in the current URL.");
        }

            // --- ASSUMED Django Context Variables (Must be set in your Django View) ---
            // const slots_available_api = {{ slots_available|safe }}; 
            // const candidate_id_api = "{{ candidate_id_from_url|safe }}"; // <-- Candidate ID from URL (e.g., '393')
            // -----------------------------------------------------------------------
            const candidate_id = candidateID

            let processedSlots = {};

            let state = {
                currentMonth: new Date(), 
                selectedDateKey: null, 
                selectedTime: null,
                isSubmitting: false,
                isConfirmed: false,
            };

            // --- 1. THE FIXED DATE PARSER (Storing the whole raw slot object for full context) ---
            function processApiSlots(slots) {
                const groupedSlots = {};
                const monthNames = ["January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"
                ];
                const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

                const now = new Date();
                // Set "Today" to midnight to ensure accurate comparison
                const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());

                const limitDate = new Date(today);
                limitDate.setDate(today.getDate() + 3);

                slots.forEach(slot => {
                    // Manually parse ISO string to avoid Browser Timezone shifts
                    let [rawDate, rawTime] = slot.start_time.split('T'); 

                    const slotDateObj = new Date(rawDate + 'T00:00:00');

                    // --- NEW LOGIC: Filter the dates ---
                    // If slot is in the past OR slot is beyond 3 days, skip it
                    if (slotDateObj < today || slotDateObj >= limitDate) {
                        return; 
                    }
                    
                    let timePart = rawTime.substring(0, 5); // "19:00"
                    let [hour, minute] = timePart.split(':');
                    
                    const dateKey = rawDate; // YYYY-MM-DD

                    // Create a date object JUST for getting the Day Name (Mon, Tue)
                    const dateObj = new Date(rawDate + 'T00:00:00'); 
                    const fullDate = `${dayNames[dateObj.getDay()]}, ${monthNames[dateObj.getMonth()]} ${dateObj.getDate()}`;

                    // Format Time (19:00 -> 07:00 PM)
                    let hourInt = parseInt(hour);
                    const ampm = hourInt >= 12 ? 'PM' : 'AM';
                    hourInt = hourInt % 12;
                    hourInt = hourInt ? hourInt : 12; 
                    const timeString = `${hourInt}:${minute} ${ampm}`;

                    if (!groupedSlots[dateKey]) {
                        groupedSlots[dateKey] = {
                            fullDate: fullDate,
                            slots: [],
                            rawSlots: {} 
                        };
                    }
                    
                    groupedSlots[dateKey].slots.push(timeString);
                    
                    // Store the entire raw slot object for easy access later
                    groupedSlots[dateKey].rawSlots[timeString] = slot; 
                });

                // Sort time slots
                for (const dateKey in groupedSlots) {
                    groupedSlots[dateKey].slots.sort((a, b) => {
                        return new Date('1970/01/01 ' + a) - new Date('1970/01/01 ' + b);
                    });
                }

                return groupedSlots;
            }

            const formatDate = (date, format) => {
                if (format === 'key') { // YYYY-MM-DD
                    const y = date.getFullYear();
                    const m = String(date.getMonth() + 1).padStart(2, '0');
                    const d = String(date.getDate()).padStart(2, '0');
                    return `${y}-${m}-${d}`;
                }
                if (format === 'full') { 
                    return date.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' });
                }
                return date.toLocaleDateString('en-US', { month: 'long', year: 'numeric' });
            };

            function renderCalendar() {
                const container = document.getElementById('calendar-container');
                if (!container) return;

                const startOfMonth = new Date(state.currentMonth.getFullYear(), state.currentMonth.getMonth(), 1);
                const endOfMonth = new Date(state.currentMonth.getFullYear(), state.currentMonth.getMonth() + 1, 0);
                const daysInMonth = endOfMonth.getDate();
                const startDayOfWeek = startOfMonth.getDay(); 

                const todayKey = formatDate(new Date(), 'key');
                
                let calendarHtml = `
                    <div class="d-flex align-items-center justify-content-between mb-3">
                        <button type="button" onclick="navigateMonth(-1)" class="btn btn-sm">
                            <i class="fas fa-chevron-left p-clr"></i>
                        </button>
                        <h3 class="fs-6 fw-bold text-dark mb-0 p-clr">${formatDate(state.currentMonth)}</h3>
                        <button type="button" onclick="navigateMonth(1)" class="btn btn-sm">
                            <i class="fas fa-chevron-right p-clr"></i>
                        </button>
                    </div>
                    <div class="calendar-grid text-center text-secondary fw-semibold mb-2">
                        ${['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => 
                            `<span class="text-uppercase">${day}</span>`
                        ).join('')}
                    </div>
                    <div class="calendar-grid text-center">
                `;

                for (let i = 0; i < startDayOfWeek; i++) {
                    calendarHtml += `<div class="day-cell"></div>`;
                }

                for (let day = 1; day <= daysInMonth; day++) {
                    const date = new Date(state.currentMonth.getFullYear(), state.currentMonth.getMonth(), day);
                    const dateKey = formatDate(date, 'key');
                    const isAvailable = processedSlots[dateKey];
                    const isSelected = dateKey === state.selectedDateKey;
                    const isToday = dateKey === todayKey;

                    let classes = `day-cell `;
                    let title = isAvailable ? `Available slots on ${formatDate(date, 'full')}` : 'No slots available';
                    
                    if (isAvailable) {
                        classes += ' text-dark btn-link p-0 available';
                    } else {
                        classes += ' text-muted ';
                    }

                    if (isSelected) {
                        classes += ' day-selected';
                    } else if (isToday) {
                        classes += ' border border-primary text-primary';
                    }

                    calendarHtml += `
                        <button type="button"
                            ${isAvailable ? `onclick="selectDate('${dateKey}')"` : 'disabled'}
                            class="${classes}"
                            title="${title}"
                        >
                            ${day}
                        </button>
                    `;
                }

                calendarHtml += `</div>`;
                container.innerHTML = calendarHtml;
            }

            function renderTimeSlots() {
                const slotsContainer = document.getElementById('time-slots-container');
                const header = document.getElementById('slots-header');
                const confirmBtn = document.getElementById('confirm-button');

                const activeDayData = processedSlots[state.selectedDateKey];
                if (!activeDayData) {
                    header.textContent = 'Please select an available date.';
                    slotsContainer.innerHTML = '<p class="text-muted fst-italic p-3 text-center w-100">No available time slots for the selected date.</p>';
                    confirmBtn.disabled = true;
                    return;
                }

                header.textContent = `Slots for ${activeDayData.fullDate}`;

                let slotsHtml = activeDayData.slots.map(time => {
                    const isSelected = state.selectedTime === time;
                    let classes = `
                        time-slot btn shadow-sm border
                        ${isSelected ? 'btn-primary border-primary' : 'btn-light text-dark'}
                        ${state.isSubmitting ? 'opacity-75 disabled' : ''}
                    `;
                    
                    return `
                        <button type="button"
                            onclick="selectTime('${time}')"
                            ${state.isSubmitting ? 'disabled' : ''}
                            class="${classes} slot-btn"
                        >
                            ${time}
                        </button>
                    `;
                }).join('');
                
                slotsContainer.innerHTML = slotsHtml;
                confirmBtn.disabled = !state.selectedTime || state.isSubmitting;
                confirmBtn.onclick = handleSubmit;
                
                confirmBtn.innerHTML = state.isSubmitting 
                    ? `<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Booking...` 
                    : 'Confirm Selection';
            }

            function renderConfirmationView() {
                const schedulingView = document.getElementById('scheduling-view');
                const confirmationView = document.getElementById('confirmation-view');
                
                if (state.isConfirmed) {
                    const activeDayData = processedSlots[state.selectedDateKey];
                    confirmationView.innerHTML = `
                        <div class="card p-4 p-md-5 text-center border-top border-success border-5 shadow-sm">
                            <i class="fas fa-check-circle fa-4x text-success mx-auto mb-4 animate-pulse"></i>
                            <h1 class="fs-2 fw-bold text-dark mb-3">Interview Scheduled!</h1>
                            <p class="text-secondary mb-4">Your 30-minute block has been successfully booked.</p>
                            <div class="text-start bg-success-subtle p-3 rounded-3 border border-success-subtle">
                                <p class="d-flex align-items-center fw-semibold text-success mb-2">
                                    <i class="fas fa-calendar-alt me-3"></i>
                                    ${activeDayData.fullDate}
                                </p>
                                <p class="d-flex align-items-center fw-semibold text-success mb-0">
                                    <i class="fas fa-clock me-3"></i>
                                    ${state.selectedTime}
                                </p>
                            </div>
                           
                        </div>
                    `;
                    schedulingView.classList.add('d-none');
                    confirmationView.classList.remove('d-none');
                } else {
                    schedulingView.classList.remove('d-none');
                    confirmationView.classList.add('d-none');
                    confirmationView.innerHTML = '';
                }
            }

            // --- ACTION HANDLERS ---
            function navigateMonth(direction) {
                state.currentMonth = new Date(state.currentMonth.getFullYear(), state.currentMonth.getMonth() + direction, 1);
                updateUI();
            }

            function selectDate(dateKey) {
                state.selectedDateKey = dateKey;
                state.selectedTime = null; 
                updateUI();
            }

            function selectTime(time) {
                state.selectedTime = state.selectedTime === time ? null : time;
                renderTimeSlots(); 
            }

            function generateSlotId(dateKey, time, rawSlotData) {
    // 1. Reconstruct the date part (e.g., Fri-12-Dec-2025)
    const dateObj = new Date(dateKey + 'T00:00:00');
    // Ensure day/month names are capitalized for consistency, though short form is fine
    const dayNameShort = dateObj.toLocaleDateString('en-US', { weekday: 'short' });
    const monthNameShort = dateObj.toLocaleDateString('en-US', { month: 'short' });
    const dayNum = String(dateObj.getDate()).padStart(2, '0'); // Pad day number for consistency
    const year = dateObj.getFullYear();
    
    // Example: Fri-12-Dec-2025
    const dateString = `${dayNameShort}-${dayNum}-${monthNameShort}-${year}`; 
    
    // 2. Reconstruct the time part (e.g., 03_00_PM) from the `time` variable ("03:00 PM")
    // Target format: HH_MM_AMPM (e.g., 03_00_PM)
    
    // Separate time and AM/PM: ["03:00", "PM"]
    const [timeOnly, ampm] = time.split(' ');
    
    // Replace colon with underscore: "03_00"
    const timeClean = timeOnly.replace(':', '_');
    
    // Combine: "03_00_PM"
    const timeStringClean = `${timeClean}_${ampm}`; 
    
    // 3. Get the unique suffix
    // Using the same logic as before, assuming 'available_interviewers' holds the ID
    const uniqueSuffix = rawSlotData.available_interviewers ? rawSlotData.available_interviewers[0] : '';
    
    // 4. Combine all parts with the double underscore separator
    const slotId = `${dateString}__${timeStringClean}__${uniqueSuffix}`;
    
    console.log("Generated Slot ID:", slotId); // Log for verification
    
    return slotId; 
}
            function handleSubmit() {
                if (!state.selectedTime || !state.selectedDateKey) return;
                
                state.isSubmitting = true;
                renderTimeSlots(); 

                const rawSlotData = processedSlots[state.selectedDateKey].rawSlots[state.selectedTime];

                // Generate the required 'slot_id' string
                const finalSlotId = generateSlotId(state.selectedDateKey, state.selectedTime, rawSlotData);

                // *** MODIFICATION: Update dataObj to match the required format ***
                let dataObj = {
                    "candidate_id": String(candidate_id), // Uses the assumed candidate_id from Django context
                    "slot_id": finalSlotId, 
                    "instructions": "",
                    "schedule_type": "N",
                };
                // *** END MODIFICATION ***

                let final_data = {
                    "data": JSON.stringify(dataObj),
                    csrfmiddlewaretoken: CSRF_TOKEN,
                };

                // Log the final payload for debugging
                console.log("Final Payload Data:", dataObj);
                
                const API_URL = CONFIG['portal'] + "/api/schedule-candidiate-interview";

               $.post(API_URL, final_data)
    .done(function (res) {
        console.log("API Response:", res); // Debugging

        // 1. CHECK SPECIFIC "SLOT TAKEN" ERROR
        if (res.data === "Please select another slot") {
            Swal.fire({
                title: "Error!",
                text: "Please Select another Slot.",
                icon: "error",
                confirmButtonText: 'OK'
            }).then(() => {
                window.location.reload();
            });
        }
        
        // 2. SUCCESS CASE (Check both 'responseCode' and 'statusCode' to be safe)
        // Usually 0 means success
        else if (res.responseCode === 0 || res.statusCode === 0) {
            Swal.fire({
                icon: 'success',
                title: 'Scheduled!',
                text: 'Your interview slot has been successfully booked.',
                timer: 2000,
                showConfirmButton: false
            }).then(() => {
                state.isSubmitting = false;
                state.isConfirmed = true;
                updateUI();
            });
        }

        // 3. ERROR CASE (statusCode is 1 or success is false)
        else {
            // Use the specific error message from the API if available
            let errorMsg = res.error || res.data || "Unknown error occurred";
            
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: errorMsg, 
            }).then(() => {
                state.isSubmitting = false; // <--- THIS STOPS THE ROTATION
                updateUI(); 
            });
        }
    })
    .fail(function (err) {
        Swal.fire({
            icon: 'error',
            title: 'Network Error',
            text: 'Could not connect to the server.',
        }).then(() => {
            state.isSubmitting = false; // <--- THIS STOPS THE ROTATION
            updateUI();
        });
    });
            }

            function resetState() {
                state.isConfirmed = false;
                state.selectedTime = null;
                updateUI();
            }

            function updateUI() {
                if (state.isConfirmed) {
                    renderConfirmationView();
                } else {
                    renderConfirmationView(); 
                    renderCalendar();
                    renderTimeSlots();
                }
            }

            // Export functions to window
            window.navigateMonth = navigateMonth;
            window.selectDate = selectDate;
            window.selectTime = selectTime;
            window.handleSubmit = handleSubmit;
            window.resetState = resetState;

            // --- MAIN INITIALIZATION (Merged) ---
            window.onload = () => {
                // 1. Debug Log
                console.log("Raw API Data:", slots_available_api); 
                

                // 2. Process Data
                if (slots_available_api && slots_available_api.length > 0) {
                    processedSlots = processApiSlots(slots_available_api);
                    
                    const firstAvailableKey = Object.keys(processedSlots)[0];
                    if (firstAvailableKey) {
                        state.selectedDateKey = firstAvailableKey;
                        const parts = firstAvailableKey.split('-').map(Number);
                        state.currentMonth = new Date(parts[0], parts[1] - 1, 1);
                    }
                } else {
                    processedSlots = {};
                }

                // 3. Render
                updateUI();
            };
     