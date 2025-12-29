
document.addEventListener("DOMContentLoaded", () => {

    const saveBtn = document.getElementById("save_branding");
    const form = document.getElementById("brand_form");

    saveBtn.addEventListener("click", function () {

        form.addEventListener("submit", function (e) {
            e.preventDefault();

            $("button").prop("disabled", true);
            $("#save_branding").html("Please Wait...");

           
            let cssVariables = "";

            document.querySelectorAll(".color-code").forEach(input => {
                let variableName = input.dataset.var;
                let value = input.value.trim();
                cssVariables += `${variableName}: ${value};\n`;
            });

           
            let fontInput = document.querySelector(".font-input");

            if (fontInput) {
                cssVariables += `--font-family: ${fontInput.value.trim()};\n`;
            }

            
            let cssContent = `:root {\n${cssVariables}\n}`;
           

         
            let dataObj = {
                request_type: "update_branding",
                branding_id: $("#colorSettings").data("company-id"),
                css_content: cssContent,
                'status': "A"
            };
            

            let finalData = {
                data: JSON.stringify(dataObj),
                csrfmiddlewaretoken: CSRF_TOKEN
            };

         
            let formData = new FormData(form);

            Object.keys(finalData).forEach(key => formData.append(key, finalData[key]));

            let logoInput = document.getElementById("logo");
            if (logoInput.files.length > 0) {
                formData.append("logo", logoInput.files[0]);
            }

            $.ajax({
                type: "POST",
                enctype: "multipart/form-data",
                url: CONFIG["portal"] + "/api/update-company-branding",
                data: formData,
                processData: false,
                contentType: false,
                cache: false,
                timeout: 600000,

                success: function (res) {
                    $("button").prop("disabled", false);
                    $("#save_branding").html("Save");

                    if (res.statusCode == 0) {
                        Swal.fire({
                            icon: "success",
                            title: "Branding updated successfully",
                            showConfirmButton: false,
                        });
                        setTimeout(() => {
                            window.location.href = "/branding";
                        }, 2000);
                    } else {
                        Swal.fire({
                            icon: "error",
                            title: "Could not process your request",
                            text: "Internal Server Error",
                            footer: "Please contact administrator",
                        });
                    }
                },

                error: function (xhr) {
                    $("button").prop("disabled", false);
                    $("#save_branding").html("Save");

                    let msg = "An error occurred. Please try again.";

                    if (xhr.status === 0) msg = "Network error. Check internet.";
                    else if (xhr.status === 500) msg = "Server error";

                    Swal.fire({
                        icon: "error",
                        title: "Request failed",
                        text: msg,
                        footer: "Please contact administrator",
                    });
                }
            });

        }, { once: true });

    });

});


document.addEventListener("DOMContentLoaded", () => {

    const script = document.getElementById("email-template-data");
    if (!script) return;

    let data;
    try {
        data = JSON.parse(script.textContent);
    } catch (e) {
        console.error("Invalid email template JSON", e);
        return;
    }

    let body = data.email_body || "";

    function safeReplace(html, placeholder, value) {
        if (!value) return html;
        return html.split(placeholder).join(value);
    }

 
    body = safeReplace(body, "[clr_primary]", "var(--brand-primary-color)");
    body = safeReplace(body, "[heading]", data.template_heading);
    body = safeReplace(body, "[company_name]", data.company_name);
    body = safeReplace(body, "[company_website]", data.company_website);
    body = safeReplace(body, "[recruitment_email_address]", data.company_email);

    
    

    const logo = data.branding?.logourl || "";
    body = body.replace(
        /<img[^>]*\[logo\][^>]*>/i,
        `<div style="text-align:center;">
                <img id="previewLogo" src="${logo}" style="width:150px;height:auto;" alt="Company Logo">
            </div>`
    );

   
    const previewEl = document.getElementById("preview_body");
    if (!previewEl) return;

    previewEl.innerHTML = body;
    
    applySocialIconToggle();
    


    
   
    const iconToggle = document.getElementById("toggle_social_icons");
    if (iconToggle) {
        iconToggle.addEventListener("change", applySocialIconToggle);
    }

    enableLiveColorPreview();
});


function enableLiveColorPreview() {

    const preview = document.getElementById("preview_body");
    if (!preview) return;

  
    document.querySelectorAll(".color-code").forEach(input => {
        input.addEventListener("input", function () {
            preview.style.setProperty(this.dataset.var, this.value.trim());
            
         
            const picker = document.querySelector(`.color-picker[data-var="${this.dataset.var}"]`);
            if (picker) picker.value = this.value;
        });
    });

    document.querySelectorAll(".color-input").forEach(picker => {
        picker.addEventListener("input", function () {
            preview.style.setProperty(this.dataset.var, this.value);

            const codeBox = document.querySelector(`.color-code[data-var="${this.dataset.var}"]`);
            if (codeBox) codeBox.value = this.value;
        });
    });
    
}


function applySocialIconToggle() {
    const iconToggle = document.getElementById("toggle_social_icons");
    const previewEl = document.getElementById("preview_body");
    if (!iconToggle || !previewEl) return;

    const socialLinks = previewEl.querySelectorAll("#previewSocialIcons a");
    if (!socialLinks.length) return;

    socialLinks.forEach(link => {
        link.style.display = iconToggle.checked ? "inline-block" : "none";
    });
}


