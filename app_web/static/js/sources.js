document.getElementById("update-sources").onclick = function () {

    $('#sources-data').unbind('submit').bind('submit', function (event) {
        event.preventDefault(); 

        $("#update-sources").prop("disabled", true);

        var sourceDataArray = [];

        $('.sources-cls').each(function() {
            var code = $(this).find('input[id^="code_"]').val();
            var label = $(this).find('input[id^="label_"]').val();
        
            sourceDataArray.push({
                'code': code,
                'label': label
            });

        });

        dataObjs = {
            'sources_data': sourceDataArray,
        }

        var final_data = {
            'data': JSON.stringify(dataObjs),
            csrfmiddlewaretoken: CSRF_TOKEN,
        }

        $.post(CONFIG['portal'] + "/api/update-source-data", final_data, function (res) {

            if (res.statusCode == 0) {

                showSuccessMessage('Sources Data Updated');
                $("#update-sources").prop("disabled", false);
                
            }
            else{
                showFailureMessage('Error in updating  sources data. Please try again after some time');
                $("#update-sources").prop("disabled", false);
            }
        })



    });

}