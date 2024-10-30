var start_today = new Date();
var start_date = start_today.getFullYear() + '-' + (start_today.getMonth() + 1) + '-' + start_today.getDate();
var start_time = start_today.getHours() + ":" + start_today.getMinutes() + ":" + start_today.getSeconds();
var start_dateTime = start_date + ' ' + start_time;

function done() {

  $("#done_btn").prop('hidden', true);
  $("#ini_div").prop('hidden', true);
  $("#end_div").prop('hidden', false);
  $("#submit_btn").prop('hidden', false);
  $("#resch").prop('hidden', false);
  $("#fcs").focus();
}


function show_ref(qid) {
  $('#ref_' + qid).prop("hidden", false);
}
function hide_ref(qid) {

  $('#ref_' + qid).prop("hidden", true);
}

var DATA = null;
var time_lapsed = document.getElementById("time_lapsed");
var secondsLabel = document.getElementById("seconds");
var totalSeconds = 0;

setInterval(setTime, 1000);
function setTime() {
  ++totalSeconds;
  time_lapsed.innerHTML = "Time Lapsed : " + pad(parseInt(totalSeconds / 60)) + ":" + pad(totalSeconds % 60);
}

function pad(val) {
  var valString = val + "";
  if (valString.length < 2) {
    return "0" + valString;
  } else {
    return valString;
  }
}
$(document).ready(function () {

  questions_resp()

  $("#sidenav-main").prop("hidden", true);
  $("#meeting_main").css({ "margin-left": "0%" });

})


function questions_resp() {

  dataObj = {
    "candid__id": candid__id,
    "candid_call_sched_id": candid_call_shed_id,
  }

  var final_data = {
    'data': JSON.stringify(dataObj),
    csrfmiddlewaretoken: CSRF_TOKEN,
  }

  $.post(CONFIG['portal'] + "/api/questions-response", final_data, function (res) {

    if (res.statusCode == 0) {

      if (res.data) {

        var ques_lst = res.data

        if (ques_lst['remark_note']) {

          $('#interviewRemarkNote').val(ques_lst['remark_note'])

        }

        for (var req_qus = 0; req_qus < ques_lst['q_lst'].length; req_qus++) {

          $('#qr_' + ques_lst['q_lst'][req_qus]['q_id']).val(ques_lst['q_lst'][req_qus]['q_res']);
          $('#qs_' + ques_lst['q_lst'][req_qus]['q_id']).text(ques_lst['q_lst'][req_qus]['q_res'])
        }

      }
    }

  })

}



var verified = []
function verify(id) {

  var resp = $('#' + id).val()
  var applicant_details = DATA[0].applicant_details;

  if (id == "partner_name") {
    if (resp.toString().toLowerCase() == applicant_details.partner_name.toString().toLowerCase()) {
      verified.push("partner_name")
      $('#er_' + id).prop("hidden", true);
      $('#cr_' + id).prop("hidden", false);
    } else {

      const index = verified.indexOf('partner_name');
      if (index > -1) {
        verified.splice(index, 1); // 2nd parameter means remove one item only
      }
      $('#er_' + id).prop("hidden", false);
      $('#cr_' + id).prop("hidden", true);
    }

  }
  if (verified.length >= 3) {
    $('span[name="vs"]').prop("hidden", false);
    $('.aplv_next').prop("hidden", false);

  } else {
    $('span[name="vs"]').prop("hidden", true);
    $('.aplv_next').prop("hidden", true);
  }
}


function showCandidateInfo() {  // it shows the jod details
  $("div[name='secs']").removeClass('sec_selected');
  $('.apl_sec').prop("hidden", false);
  //$('.ins').prop("hidden",true);
  $('#sec').prop("hidden", true);
  $('.ins').prop("hidden", true);
  $("#verif_sec").addClass("sec_selected");
  $("#ins_sec").removeClass('sec_selected');
}

function show_ins() { // it shows the candidate details
  $("div[name='secs']").removeClass('sec_selected');
  $('.apl_sec').prop("hidden", true);
  //$('.ins').prop("hidden",true);
  $('#sec').prop("hidden", true);
  $('.ins').prop("hidden", false);
  $("#verif_sec").removeClass("sec_selected");
  $("#ins_sec").addClass('sec_selected');
}




function show_section(sec_id) {  // it shows and hides the sections

  $("div[name='secs']").removeClass('sec_selected');
  $("#" + sec_id).addClass("sec_selected");

  $('#sec').prop("hidden", false);
  $('.apl_sec').prop("hidden", true);
  $("#ins_sec").removeClass('sec_selected');
  $('.ins').prop("hidden", true);


  let elements = document.querySelectorAll('span[name="vs"]');

  elements.forEach(element => {

    let children = element.children;

    for (let child of children) {

      if (child.id == sec_id) {

        $('.sec_' + sec_id).prop("hidden", false)

        break

      }
      else {

        $('.sec_' + child.id).prop("hidden", true)

      }
    }
  });

}



function answer(quest_data) { // each question answer submites the after value updates. 


  var input_val = $("#" + quest_data['inpt_id']).val()

  dataObj = {
    "qid": quest_data['question_id'],
    "candid_id": quest_data['candid_id'],
    "call_sch_id": quest_data['call_shud_id'],
    "qrate": input_val,

  }

  $("#qs_" + quest_data['question_id']).text(input_val);

  var final_data = {
    'data': JSON.stringify(dataObj),
    csrfmiddlewaretoken: CSRF_TOKEN,
  }


  $.post(CONFIG['portal'] + "/api/interview-response", final_data, function (res) {

  })

}


function fill_data() {

  if ($("#toggle").val() == null || $("#notes").val() == null || $("#notes").val() == "") {
    $("#submit_btn").prop("disabled", true);
  } else {
    $("#submit_btn").prop("disabled", false);
  }

}


$("#submit_btn").click(function () {

  $("#submit_btn").prop("disabled", true);

  gonogo = document.getElementById('toggle').checked ? 'Y' : 'N';

  dataObj_ = {
    "sch_id": candid_call_shed_id,
    'notes': $('#notes').val(),
    'gonogo':gonogo

  }

  var final_data_ = {
    'data': JSON.stringify(dataObj_),
    csrfmiddlewaretoken: CSRF_TOKEN,
  }

  $.post(CONFIG['portal'] + "/api/interview-completion", final_data_, function (res_) {

    if (res_.statusCode == 0) {
      Swal.fire({
        position: 'center',
        icon: 'success',
        title: 'Interview Completed',
        showConfirmButton: false,
        timer: 1500
      })
      setTimeout(function () { window.location.href = '/interviews' }, 1000);
    } else {
      $("#submit_btn").prop("disabled", false);
    }

  })

})



function remarks() {
  dataObj = {
    "sch_id": candid_call_shed_id,
    "remarks": $("#interviewRemarkNote").val(),
  }

  var final_data = {
    'data': JSON.stringify(dataObj),
    csrfmiddlewaretoken: CSRF_TOKEN,
  }


  $.post(CONFIG['domain'] + "/api/interview-remarks", final_data, function (res) {

  })

}

