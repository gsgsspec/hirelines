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


function openEditWorkspace(id, clientId, project, startdate, notes) {
    document.getElementById("edit_workspace_id").value = id;
    document.getElementById("edit_client").value = clientId;
    document.getElementById("edit_project").value = project;
    document.getElementById("edit_startdate").value = startdate;
    document.getElementById("edit_notes").value = notes || "";

    new bootstrap.Modal(document.getElementById("editWorkspaceModal")).show();
}

function handleUpdateWorkspace() {
    event.preventDefault();

    const dataObjs = {
        workspaceid: document.getElementById("edit_workspace_id").value,
        client: document.getElementById("edit_client").value,
        project: document.getElementById("edit_project").value,
        startdate: document.getElementById("edit_startdate").value,
        notes: document.getElementById("edit_notes").value
    };

    var final_data = {
        'data': JSON.stringify(dataObjs),
        csrfmiddlewaretoken: CSRF_TOKEN,
    }

    $.post(CONFIG['portal'] + "/api/update-workspace", final_data, function (res) {
        if (res.statusCode == 0) {
            Swal.fire({
                position: 'center',
                icon: 'success',
                title: 'Workspace Updated',
                showConfirmButton: false,
                timer: 1500
            })

            setTimeout(function () { window.location.reload() }, 1500);
        }

    })

}