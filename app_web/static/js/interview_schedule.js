$('#position').on('change', function () {
  var candidate_id = $('#cid').html()
  var int_id = $(this).val()

  $("#thead").empty();
  $("#tbody").empty();

  $.get(CONFIG['domain'] + "/api/call-scheduling/" + candidate_id + "?int_id=" + int_id, function (res) {

    var DATA = res.data;
    console.log('Data', DATA)
    $("#thead").append('<th class="text-uppercase text-xxs font-weight-bolder opacity-7 ps-2">Time</th>')

    for (var i = 0; i < DATA.length; i++) {
      $("#thead").append('<th class="text-uppercase text-xxs font-weight-bolder opacity-7 text-center" style="padding: 7px;">' + DATA[i]['day'].slice(0, 10) + '</th>')
    }

    for (var n = 0; n < DATA[0]['hours_list'].length; n++) {
      $("#tbody").append('<tr>' +
        '<td><h6 class="text-sm">' + DATA[0]['hours_list'][n] + '</h6></td>' +
        '<td name="' + DATA[0]['status'][n] + '" class="data-center ' + DATA[0]['status'][n] + '" id="' + DATA[0]['day'] + '__' + DATA[0]['hours_list'][n].replace(/:/gi, "_").replace(/ /gi, "_") + '__' + DATA[0]['ids'][n].filter(Boolean).join(",").replace(/ /gi, "").replace(/,/gi, "_") + '" onclick="selected(this.id);"></td>' +
        '<td name="' + DATA[1]['status'][n] + '" class="data-center ' + DATA[1]['status'][n] + '" id="' + DATA[1]['day'] + '__' + DATA[0]['hours_list'][n].replace(/:/gi, "_").replace(/ /gi, "_") + '__' + DATA[1]['ids'][n].filter(Boolean).join(",").replace(/ /gi, "").replace(/,/gi, "_") + '" onclick="selected(this.id);"></td>' +
        '<td name="' + DATA[2]['status'][n] + '" class="data-center ' + DATA[2]['status'][n] + '" id="' + DATA[2]['day'] + '__' + DATA[0]['hours_list'][n].replace(/:/gi, "_").replace(/ /gi, "_") + '__' + DATA[2]['ids'][n].filter(Boolean).join(",").replace(/ /gi, "").replace(/,/gi, "_") + '" onclick="selected(this.id);"></td>' +
        '<td name="' + DATA[3]['status'][n] + '" class="data-center ' + DATA[3]['status'][n] + '" id="' + DATA[3]['day'] + '__' + DATA[0]['hours_list'][n].replace(/:/gi, "_").replace(/ /gi, "_") + '__' + DATA[3]['ids'][n].filter(Boolean).join(",").replace(/ /gi, "").replace(/,/gi, "_") + '" onclick="selected(this.id);"></td>' +
        '<td name="' + DATA[4]['status'][n] + '" class="data-center ' + DATA[4]['status'][n] + '" id="' + DATA[4]['day'] + '__' + DATA[0]['hours_list'][n].replace(/:/gi, "_").replace(/ /gi, "_") + '__' + DATA[4]['ids'][n].filter(Boolean).join(",").replace(/ /gi, "").replace(/,/gi, "_") + '" onclick="selected(this.id);"></td>' +
        '<td name="' + DATA[5]['status'][n] + '" class="data-center ' + DATA[5]['status'][n] + '" id="' + DATA[5]['day'] + '__' + DATA[0]['hours_list'][n].replace(/:/gi, "_").replace(/ /gi, "_") + '__' + DATA[5]['ids'][n].filter(Boolean).join(",").replace(/ /gi, "").replace(/,/gi, "_") + '" onclick="selected(this.id);"></td>' +
        '<td name="' + DATA[6]['status'][n] + '" class="data-center ' + DATA[6]['status'][n] + '" id="' + DATA[6]['day'] + '__' + DATA[0]['hours_list'][n].replace(/:/gi, "_").replace(/ /gi, "_") + '__' + DATA[6]['ids'][n].filter(Boolean).join(",").replace(/ /gi, "").replace(/,/gi, "_") + '" onclick="selected(this.id);"></td>' +
        '<td name="' + DATA[7]['status'][n] + '" class="data-center ' + DATA[7]['status'][n] + '" id="' + DATA[7]['day'] + '__' + DATA[0]['hours_list'][n].replace(/:/gi, "_").replace(/ /gi, "_") + '__' + DATA[7]['ids'][n].filter(Boolean).join(",").replace(/ /gi, "").replace(/,/gi, "_") + '" onclick="selected(this.id);"></td>' +
        '<td name="' + DATA[8]['status'][n] + '" class="data-center ' + DATA[8]['status'][n] + '" id="' + DATA[8]['day'] + '__' + DATA[0]['hours_list'][n].replace(/:/gi, "_").replace(/ /gi, "_") + '__' + DATA[8]['ids'][n].filter(Boolean).join(",").replace(/ /gi, "").replace(/,/gi, "_") + '" onclick="selected(this.id);"></td>' +
        '<td name="' + DATA[9]['status'][n] + '" class="data-center ' + DATA[9]['status'][n] + '" id="' + DATA[9]['day'] + '__' + DATA[0]['hours_list'][n].replace(/:/gi, "_").replace(/ /gi, "_") + '__' + DATA[9]['ids'][n].filter(Boolean).join(",").replace(/ /gi, "").replace(/,/gi, "_") + '" onclick="selected(this.id);"></td>' +
        '<td name="' + DATA[10]['status'][n] + '" class="data-center ' + DATA[10]['status'][n] + '" id="' + DATA[10]['day'] + '__' + DATA[0]['hours_list'][n].replace(/:/gi, "_").replace(/ /gi, "_") + '__' + DATA[10]['ids'][n].filter(Boolean).join(",").replace(/ /gi, "").replace(/,/gi, "_") + '" onclick="selected(this.id);"></td>' +
        '<td name="' + DATA[11]['status'][n] + '" class="data-center ' + DATA[11]['status'][n] + '" id="' + DATA[11]['day'] + '__' + DATA[0]['hours_list'][n].replace(/:/gi, "_").replace(/ /gi, "_") + '__' + DATA[11]['ids'][n].filter(Boolean).join(",").replace(/ /gi, "").replace(/,/gi, "_") + '" onclick="selected(this.id);"></td>' +
        '<td name="' + DATA[12]['status'][n] + '" class="data-center ' + DATA[12]['status'][n] + '" id="' + DATA[12]['day'] + '__' + DATA[0]['hours_list'][n].replace(/:/gi, "_").replace(/ /gi, "_") + '__' + DATA[12]['ids'][n].filter(Boolean).join(",").replace(/ /gi, "").replace(/,/gi, "_") + '" onclick="selected(this.id);"></td>' +
        '<td name="' + DATA[13]['status'][n] + '" class="data-center ' + DATA[13]['status'][n] + '" id="' + DATA[13]['day'] + '__' + DATA[0]['hours_list'][n].replace(/:/gi, "_").replace(/ /gi, "_") + '__' + DATA[13]['ids'][n].filter(Boolean).join(",").replace(/ /gi, "").replace(/,/gi, "_") + '" onclick="selected(this.id);"></td>' +
        '<td name="' + DATA[14]['status'][n] + '" class="data-center ' + DATA[14]['status'][n] + '" id="' + DATA[14]['day'] + '__' + DATA[0]['hours_list'][n].replace(/:/gi, "_").replace(/ /gi, "_") + '__' + DATA[14]['ids'][n].filter(Boolean).join(",").replace(/ /gi, "").replace(/,/gi, "_") + '" onclick="selected(this.id);"></td>' +
        '</tr>')
    }

  })

  const getNext15Days = (date, day, month, year) =>
    Array.from(
      { length: new Date(year, month, 15).getDate() }, // get next month, zeroth's (previous) day
      (_, i) => new Date(year, month, i + date, day))    // get current month (0 based index);;

  var today = new Date();
  day = today.getDay();
  date = today.getDate();
  month = today.getMonth();
  year = today.getFullYear();

  const next15Days = getNext15Days(date, day, month, year)

  var nxt15days = next15Days.map(x => x.toLocaleDateString("en-GB", { day: "numeric", month: "short", weekday: 'short' }).replace(', ', '-').replace(' ', '-'));

})

var sch = null;
function selected(id) {
  $("td[name='Available']").removeClass('selected_');

  $("#sel_slot").prop("hidden", false);
  $("#sel_slot").html("Slot selected on " + (id).split("__")[0] + ", " + (id).split("__")[1].replace("_", ":").replace("_", " "));
  sch = id;

  $("#" + id).addClass("selected_");
}


$('#schedule_btn').on('click', function () {
  console.log('sch',sch)
  if (!sch) {
    alert("Please Select a Slot.");
  } else {
    // $('#schedule_btn').prop("disabled", true);
    $('#cancel_btn').prop("disabled", true);
    dataObj = {
      "candidate_id": $('#cid').html(),
      "slot_id": sch,
      "instructions": $("#instructions").val()
    }

    var final_data = {
      'data': JSON.stringify(dataObj),
      csrfmiddlewaretoken: CSRF_TOKEN,
    }

    $.post(CONFIG['domain'] + "/api/schedule-call", final_data, function (res) {
      if (res.statusCode == 0) {
        if (res.data == 'Slot Booked') {
        
          swal("Call Scheduled Successfully", "", "success");
          setTimeout(function () { window.location.href = '/web/candidates' }, 1000);
        }
        if (res.data == 'Slot Not Available') {
          $('#cancel_btn').prop("disabled", false);
          $('#schedule_btn').prop("disabled", false);
         
          swal("Slot Not Available", "", "error");
        }
        if (res.data == 'No Applicant') {
          $('#cancel_btn').prop("disabled", false);
          $('#schedule_btn').prop("disabled", false);
          Swal.fire({
            icon: 'error',
            title: 'No Applicant Details',
            //                                          text: 'Please Add Applicant',
            confirmButtonColor: '#e11e1e'
          })
        }
      } else {
        $('#schedule_btn').prop("disabled", false);
        $('#cancel_btn').prop("disabled", false);
        swal("Internal Server Error", "", "error");
      }
    })


  }
})

$('#cancel_btn').on('click', function () {
  $("td[name='Available']").removeClass('selected_');
  sch = null;
  $("#sel_slot").prop("hidden", true);
})