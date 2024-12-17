
function deleteSelectedCandidates() {

    const selectedIds = Array.from(document.querySelectorAll('.cd-check:checked')).map(input => input.value);

    if (selectedIds.length === 0) {
        Swal.fire({
            position: 'center',
            icon: 'warning',
            title: 'No candidates selected',
            showConfirmButton: true,
            confirmButtonColor: '#274699',
        })
        return;
    }

    Swal.fire({
        title: 'Are you sure?',
        text: `You are about to delete ${selectedIds.length} candidate(s).`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#274699',
        cancelButtonColor: '#f25c05',
        confirmButtonText: 'Yes, Delete'
    }).then((result) => {
        if (result.isConfirmed) {

            dataObj = {
                'cid': selectedIds,
            }
    
            var final_data = {
                'data': JSON.stringify(dataObj),
                csrfmiddlewaretoken: CSRF_TOKEN,
            }

            $.post(CONFIG['portal'] + "/api/delete-candidate", final_data, function (res) { 

                if (res.statusCode == 0) {
                    Swal.fire({
                        position: 'center',
                        icon: 'success',
                        title: 'Canididates Deleted',
                        showConfirmButton: false,
                        timer: 2000
                    })

                    setTimeout(function () {window.location.reload();}, 2000);
                }

            })
        }
    });
}

function handleCheckboxChange() {
    const checkboxes = document.querySelectorAll('.cd-check');
    const filterSec = document.querySelector('.filter-sec');

    const isAnyChecked = Array.from(checkboxes).some(checkbox => checkbox.checked);

    if (isAnyChecked) {
        filterSec.style.display = 'block';
    } else {
        filterSec.style.display = 'none';
    }
}

document.addEventListener('DOMContentLoaded', function () {

    handleCheckboxChange();

    const checkboxes = document.querySelectorAll('.cd-check');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', handleCheckboxChange);
    });
});


document.addEventListener('DOMContentLoaded', () => {
    const loader = document.getElementById('candidates-loader');

    window.addEventListener('load', () => {
        loader.style.display = 'none';
    });
});
