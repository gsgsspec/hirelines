function handleCreateWorkspace(){
    $('#workspace-add-form').unbind('submit').bind('submit', function (event) {
        event.preventDefault();

        dataObjs = {
            'client':  $('#client').val(),
            'project':  $('#project').val(),
            'startdate':  $('#startdate').val(),
            'notes':  $('#notes').val()
        }

        var final_data = {
            'data': JSON.stringify(dataObjs),
            csrfmiddlewaretoken: CSRF_TOKEN,
        }

        $.post(CONFIG['portal'] + "/api/add-workspace", final_data, function (res) {
            if (res.statusCode == 0) {
                Swal.fire({
                    position: 'center',
                    icon: 'success',
                    title: 'Workspace Created',
                    showConfirmButton: false,
                    timer: 1500
                })

                setTimeout(function () { window.location.reload() }, 1500);
            }

        })

    })
}