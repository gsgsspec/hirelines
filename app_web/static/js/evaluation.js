var paper_id = null;
var participant_id = null;
var currentParticipantIndex = 0;
var PARTICIPANT = [];
var hide_reg_number_flag = $("#p_flag").attr('name');
var papers_count = null
var evaluated_papers = null
var is_submission_evaluated = false

$(document).ready(function () {
    $(".papers-card").addClass("loading");
    get_papers_data();

})

function get_papers_data() {

    $.get(CONFIG['portal'] + "/api/evaluation", function (res) {
        $(".all_eval_label").remove();
        if (res.statusCode == 0) {
            var papers_data = res.data;
            papers_count = papers_data.length
            if(papers_count==0){
                $(".papers-card").append("<h5 class='form-label all_eval_label'>No Tests</h5>")
            }
            papers_data.map((paper, index) => {
                if (paper.paper_count == 0) {
                    $("#papers").append(`<p onclick="filter_data(${paper.id},null)" name="papers" id="paper_${paper.id}" class="form-label no_submissions_to_evaluate" style="cursor:pointer;display:none;" >${paper.paper_code} - ${paper.paper_name}  (${paper.paper_count})</p>`)
                    evaluated_papers += 1
                } else {
                    $("#papers").append(`<p onclick="filter_data(${paper.id},null)" name="papers" id="paper_${paper.id}" class="form-label" style="cursor:pointer;" >${paper.paper_code} - ${paper.paper_name}  (${paper.paper_count})</p>`)
                }

            })
            if (papers_count == evaluated_papers) {
                // $('#show_all_papers').click();
                $(".papers-card").append("<h5 class='form-label all_eval_label'>All Tests Evaluated</h5>")
            } else {
                $("p[name='papers']:first").click();
            }
            $(".papers-card").removeClass("loading");

        } else {
            Swal.fire({
                icon: 'error',
                title: 'Could not process your request',
                text: 'Internal Server Error',
                confirmButtonText: 'OK',
                confirmButtonColor: '#274699',
                footer: 'Please contact administrator'
            })
            $(".papers-card").removeClass("loading");
        }
    })

}

$('#show_all_papers').click(function () {
    var paper_status = "all"
    $('.no_submissions_to_evaluate').each(function () {
        if ($(this).css('display') === 'none') {
            $(this).css('display', 'block');
            paper_status = "all"
        } else {
            $(this).css('display', 'none');
            paper_status = "to_be_evaluated"
        }
    })

    if (paper_status == "to_be_evaluated") {
        $('#show_all_papers').text('Show All');
        if (papers_count == evaluated_papers) {
            $(".papers-card").append("<h5 class='form-label all_eval_label'>All Tests Evaluated</h5>")
            $('#participants').html('<div class="loader-overlay">' +
                '<div class="loader"></div>' +
                '</div>');
        } else {
            $(".all_eval_label").remove()
            $("p[name='papers']:first").click();
        }
    } else {
        $(".all_eval_label").remove()
        $('#show_all_papers').text('Hide Evaluated');
        $("p[name='papers']:first").click();
    }
});



function filter_data(pid, ptid) {
    $('body').addClass('cursor-progress');
    $('p[name="papers"]').addClass('cursor-progress')
    $('tr[name="participants"]').addClass('cursor-progress')
    $(".papers-card").addClass("loading");
    $(".participants-card").addClass("loading");
    $(".eval-question-div").html("");
    $("#questions").html('');
    $('.send-result').remove();

    if (pid) {
        paper_id = pid;
    }
    if (ptid) {
        participant_id = ptid;
    }
    dataObj = {
        "request_for": "submissions",
        "paper_id": paper_id,
        "participant_id": participant_id,
    }

    var final_data = {
        'data': JSON.stringify(dataObj),
        csrfmiddlewaretoken: CSRF_TOKEN,
    }
    $.post(CONFIG['portal'] + "/api/evaluation", final_data, function (res) {

        if (res.statusCode == 0) {
            var DATA = res.data;
            PARTICIPANT = DATA.participants;
            var QUESTIONS = DATA.questions;
            var PAPER_NAME = DATA.paper_name;
            var PARTICIPANT_NAME = DATA.name;
            var PARTICIPANT_LAST_NAME = DATA.l_name;
            var MARKS = DATA.total_marks;
            var PAPER_MARKS = DATA.paper_marks;
            var SECURED_MARKS = DATA.secured_marks;


            $('#participants').html('<div class="loader-overlay">' +
                '<div class="loader"></div>' +
                '</div>');
            for (var n = 0; n < PARTICIPANT.length; n++) {

                participant_status = ""
                if (PARTICIPANT[n]["p_status"] === "S" || PARTICIPANT[n]["p_status"] === "P") {

                    participant_status = '';
                }
                else {
                    participant_status = '<i class="fas fa-check" style="color:#73d973"></i>';
                }

                var participantName = (hide_reg_number_flag === "N") ? "**********" : PARTICIPANT[n]["participant"];

                $("#participants").append(
                    '<tr onclick="filter_data(null,' + PARTICIPANT[n]["pid"] + ')" name="participants" id="participant_' + PARTICIPANT[n]["pid"] + '" class="top" style="text-transform: capitalize;cursor:pointer;">'
                    + '<td style="width:100px;" class="form-label">' + PARTICIPANT[n]["registration_code"] + '</td>'
                    + '<td style="width:150px;" class="form-label cust-participant-name">' + participantName + '</td>'
                    + '<td class="form-label cust-participant-date">' + PARTICIPANT[n]["submission_date"] + '</td>'
                    + '<td class="form-label cust-participant-status">' + '&ensp;' + participant_status + '</td>'
                    + '</tr>'
                );
            }

            $('#heading').html('');

            var first_name = (hide_reg_number_flag === "N") ? "**********" : PARTICIPANT_NAME;
            var last_name = (hide_reg_number_flag === "N") ? "" : PARTICIPANT_LAST_NAME;

            $('#heading').append(
                '<label>' + 'Paper:' + '&ensp;' + '</label>' + '<label style="text-transform: capitalize;">' + PAPER_NAME + '&ensp;&ensp;' + '</label>&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;' +
                '<label>' + 'Submitted by:' + '&ensp;' + '</label>' + '<label style="text-transform: capitalize;">' + first_name + '&ensp;' + last_name + '</label>&ensp;&ensp;&ensp;&ensp;&ensp;&ensp;' +
                '<label>' + 'Marks:' + '&ensp;' + '</label>' + '<label style="text-transform: capitalize;" id="total_marks">' + MARKS + '&ensp;&ensp;' + '</label>'
            )

            $("p[name='papers']").removeClass("selection-item")
            $("#paper_" + DATA["selected_papers"]).addClass("selection-item")
            $("p[name='participants']").removeClass("selection-item")
            $("p[name='participants']").each(function () {
                $(this).find('td').removeClass('selection-item');
            });

            $("#participant_" + DATA["selected_participants"]).addClass("selection-item")
            $("#participant_" + DATA["selected_participants"]).each(function () {
                $(this).find('td').addClass('selection-item');
            });

            participant_id = null; 



            var QUESTIONS_LIST = []

            if (PARTICIPANT.length == 0) {
                $("#participants").append("<h5 class='form-label'>No Submissions</h5>")
                $("#questions").html('');
            } else {
                QUESTIONS_LIST = DATA.questionlist
                $("#questions").append('<h5 style="display: flex ;font-weight:bold; justify-content: space-between;"><span>'+PAPER_NAME+'</span><span>'+ first_name + '&ensp;' + last_name +'</span><span>Total Marks: '+PAPER_MARKS+'</span><span id="secured_marks">Secured Marks: '+SECURED_MARKS+'</span></h5>')
            }
            for (var n = 0; n < QUESTIONS_LIST.length; n++) {

                var question_sno = n + 1;

                var OPTIONS = QUESTIONS_LIST[n]["question_options"]
                var SKIP = QUESTIONS_LIST[n]["anser_skip_resp"]

                var question_options_div = ""
                var question_expanswer_div = ""
                var question_image = ""
                var question_audio = ""
                var question_video = ""
                var anser_skip_resp = ""
                var evaluation_btns = ""
                if (QUESTIONS_LIST[n]["question_image"]) {
                    question_image = '<br/><img id="output" src="' + QUESTIONS_LIST[n]["question_image"] + '" width="300" /><br/>'
                }
                if (QUESTIONS_LIST[n]["question_audio"]) {
                    question_audio = '<br/><audio id="play_audio" style="width:500px" controls><source  src="' + QUESTIONS_LIST[n]["question_audio"] + '"/></audio><br/>'
                }
                if (QUESTIONS_LIST[n]["question_video"]) {
                    question_video = '<br/><span id="video span"><video id="play_video"  controls width="300"><source src="' + QUESTIONS_LIST[n]["question_video"] + '"/></video></span><br/>'
                }
                if (QUESTIONS_LIST[n]["anser_skip_resp"]) {
                    anser_skip_resp = '<div style="padding-top:10px;padding-left:12px; color:red;">' + '  ' + QUESTIONS_LIST[n]['anser_skip_resp'] + '</div>';
                }
                if (QUESTIONS_LIST[n]["question_type_code"] == "M") {
                    question_options_div = '<div class="options-grid-container p-10 mt-3 mb-3 custom-ml-3" id="question_options_' + QUESTIONS_LIST[n]['id'] + '"></div>'
                }
                if (QUESTIONS_LIST[n]["question_type_code"] == "B") {
                    question_options_div = '<div class="options-grid-container p-10 mt-3 mb-3 custom-ml-3" id="question_options_' + QUESTIONS_LIST[n]['id'] + '"></div>'
                }
                if (QUESTIONS_LIST[n]['question_type_code'] == "P") {
                    question_options_div = '<p style="padding:13px">' + '<b>Answer :  </b>  ' + QUESTIONS_LIST[n]['question_answer'] + '</p>';
                    question_expanswer_div = '<p style="padding:13px" class="form-label">' + '<b>Expected Answer :  </b>  ' + QUESTIONS_LIST[n]['question_expected_answer'] + '</p>';
                    evaluation_btns = '<div class="float-right mb-3">' +
                        '<button class="mb-1 btn btn-cancel text-white btn_width "  name="update_marks_btns" style="background-color: #73d973 !important;margin-right:10px" id="save" onclick="updateMarks(' + question_sno + ')"><i style="padding-right:10px" class="fas fa-check"></i>Correct</button>' +
                        '<button class="mb-1 btn btn-danger text-white btn_width ml-2 "  name="update_marks_btns" style="background-color:#ff0000bd !important" onclick="Incorrect(' + question_sno + '); updateMarks(' + question_sno + ')" ><i style="padding-right:6px" class="fas fa-times"></i>Incorrect</button>' +
                        '</div>'
                }

                if (QUESTIONS_LIST[n]["question_type_code"] == "C" || QUESTIONS_LIST[n]["question_type_code"] == "R" || QUESTIONS_LIST[n]["question_type_code"] == "O") {

                    answer = QUESTIONS_LIST[n]['question_answer']

                    if (answer) {
                        rows = getTextareaRows(QUESTIONS_LIST[n]['question_answer']);
                    } else {
                        rows = 2
                        answer = ""
                    }
                    answer = `<pre><code style="font-size: 15px;color: #4a556e;">${answer}</code></pre>`
                    question_options_div = '<div style="display:flex;justify-content:space-between;width:100%"><p style="padding-top:13px"> <b>Question Type :</b>  ' + QUESTIONS_LIST[n]['question_type_name'] + ' </p><p style="padding-top:13px"> <b>Time used :</b>  ' + QUESTIONS_LIST[n]['question_time_used'] + ' </p></div>' +
                        '<label>Code :</label><div style="width: 100%;" class="form-control"  disabled>' +
                        answer +
                        '</div> <br>';
                }

                if (QUESTIONS_LIST[n]["question_type_code"] == "A") {
                    question_expanswer_div = '<p style="padding:13px" class="form-label">' + '<b>Expected Answer :  </b>  ' + QUESTIONS_LIST[n]['question_expected_answer'] + '</p>';
                    question_options_div = '<br/><audio id="play_audio" style="width:500px" controls><source  src="' + QUESTIONS_LIST[n]["response_media"] + '"/></audio><br/><br/>'
                    evaluation_btns = '<div class="float-right mb-3">' +
                        '<button class="mb-1 btn btn-cancel btn_width text-white "  name="update_marks_btns" style="background-color: #73d973 !important;margin-right:10px" id="save" onclick="updateMarks(' + question_sno + ')"><i style="padding-right:10px" class="fas fa-check"></i>Correct</button>' +
                        '<button class="mb-1 btn btn-danger btn_width text-white ml-2 "  name="update_marks_btns" style="background-color:#ff0000bd !important" onclick="Incorrect(' + question_sno + '); updateMarks(' + question_sno + ')" ><i style="padding-right:6px" class="fas fa-times"></i>Incorrect</button>' +
                        '</div>'
                }

                if (QUESTIONS_LIST[n]["question_type_code"] == "V") {
                    question_expanswer_div = '<p style="padding:13px"  class="form-label">' + '<b>Expected Answer :  </b>  ' + QUESTIONS_LIST[n]['question_expected_answer'] + '</p>';
                    if (QUESTIONS_LIST[n]["response_media"]) {
                        question_options_div = '<br/>' +
                            '<h4>Response video</h4><video class="video-resp-window" controls><source  src="' + QUESTIONS_LIST[n]["response_media"] + '" width="200"/></video><br/>'
                    } else {
                        question_options_div = '<br/>'
                    }

                    evaluation_btns = '<div class="float-right mb-3">' +
                        '<button class="mb-1 btn btn-cancel text-white btn_width "  name="update_marks_btns" style="background-color: #73d973 !important;margin-right:10px" id="save" onclick="updateMarks(' + question_sno + ')"><i style="padding-right:10px" class="fas fa-check"></i>Correct</button>' +
                        '<button class="mb-1 btn btn-danger text-white btn_width ml-2 " name="update_marks_btns" style="background-color:#ff0000bd !important" onclick="Incorrect(' + question_sno + '); updateMarks(' + question_sno + ')" ><i style="padding-right:6px" class="fas fa-times"></i>Incorrect</button>' +
                        '</div>'
                }


                accord_style = ''
                if (QUESTIONS_LIST[n]["answer_marks"] !== "") {
                    accord_style = '<div class="ans-color-line"></div>'
                }

                else {
                    accord_style = ''
                }

                var star
                star = ('&ensp;&ensp;') // empty
                if(QUESTIONS_LIST[n]['star_question'] == 'Y'){
                    star = ('<i class="fas fa-star" style="color: #f25c05 !important;"></i>')
                }
                
                $("#questions").append(
                    '<button class="accordion" id="questions" name="eval_ques_' + question_sno + '">' + accord_style +
                    '<div class="w-100p text-left " style="font-weight:600">' + star +'&ensp;' + question_sno + '.' + ' ' + QUESTIONS_LIST[n]["question"] +
                    '<i class="float-right acc_icon bx bxs-chevron-right"></i>' +
                    '</div>' +

                    '</button>' +
                    '<div class="panel form-label" id="questions">' +
                    anser_skip_resp +
                    question_image +
                    question_audio +
                    question_video +
                    question_options_div +
                    question_expanswer_div +
                    '<div class="form-group row" style="margin-left:11px">' +
                    '<label class="form-label marks-label">Total Marks:</label>' +
                    '<div class="form-label marks-display">' +
                    '<input class="form-control" type="text" value="' + QUESTIONS_LIST[n]['question_mark'] + '" maxlength="100" id="marks' + question_sno + '" disabled>' +
                    '</div>' +
                    '<label class="form-label marks-label">Given Marks:</label>' +
                    '<div class="form-label marks-display">' +
                    '<input oninput="myFunction(' + question_sno + ')" class="form-control given-marks" name="' + QUESTIONS_LIST[n]['answer_id'] + '" id="ans_mark' + question_sno + '" value="' + QUESTIONS_LIST[n]['answer_marks'] + '" required>' +
                    '</div>' +
                    '</div>' +
                    '<div class="form-group row"  id="textareaContainer' + question_sno + '"  style="display:none;" >' + '<label class="form-label marks-label" style="width: 13em;padding-left: 27px;">Reason for less Marks:</label>' +
                    '<textarea style="width: 400px;" class="form-control exp-ans-text"  id="reason' + question_sno + '"  rows="4" maxlength="256" required>' + QUESTIONS_LIST[n]['reason'] + '</textarea>' +
                    '</div>' +
                    evaluation_btns +
                    '</div>'

                )

                if (parseInt(QUESTIONS_LIST[n]['question_mark']) > parseInt(QUESTIONS_LIST[n]['answer_marks'])) {
                    $("#textareaContainer" + question_sno).show();
                } else {
                    $("#textareaContainer" + question_sno).hide();
                }

                if ((QUESTIONS_LIST[n]["question_type_code"] == "C") || (QUESTIONS_LIST[n]["question_type_code"] == "R") || (QUESTIONS_LIST[n]["question_type_code"] == "O")) {
                    $("#textareaContainer" + question_sno).hide();
                }


                $('.accordion').last().click(accord);

                if (QUESTIONS_LIST[n]["question_type_code"] == "M") {
                    $("#textareaContainer" + question_sno).hide();
                    $("#ans_mark" + question_sno).prop("disabled", true);
                    for (var opt = 0; opt < OPTIONS.length; opt++) {
                        var letter = String.fromCharCode(65 + opt);

                        if (QUESTIONS_LIST[n]['question_answer'] == OPTIONS[opt]["option_name"]) {
                            var correctOptionText = letter + ') ' + OPTIONS[opt]["option_name"];
                            var correctOptionHTML = '<div class="form-label">' + correctOptionText + '&ensp;<i class="fas fa-times" style="color:#ff5e0e "></i></div>';
                            if (OPTIONS[opt]["option_answer"] == "Y") {
                                correctOptionHTML = '<div class="form-label">' + correctOptionText + '&ensp;<i class="fas fa-check" style="color:#73d973"></i><i class="fas fa-check" style="color:#73d973 "></i></div>';
                            }
                            $("#question_options_" + QUESTIONS_LIST[n]['id']).append(correctOptionHTML);
                        } else {
                            var tickMark = "";
                            if (OPTIONS[opt]["option_answer"] == "Y") {
                                tickMark = '<i class="fas fa-check" style="color:#73d973 "></i>';
                            }
                            var optionText = letter + ') ' + OPTIONS[opt]["option_name"];
                            var optionHTML = '<div  class="form-label">' + optionText + '&ensp;' + tickMark;
                            if (QUESTIONS_LIST[n]['question_answer'] == OPTIONS[opt]["option_name"]) {
                                optionHTML += '<i class="fas fa-check" style="color:#73d973 "></i>';
                            }
                            optionHTML += '</div>';
                            $("#question_options_" + QUESTIONS_LIST[n]['id']).append(optionHTML);
                        }
                    }
                }
                if (QUESTIONS_LIST[n]["question_type_code"] == "B") {
                    $("#textareaContainer" + question_sno).hide();
                    $("#ans_mark" + question_sno).prop("disabled", true);
                    for (var opt = 0; opt < OPTIONS.length; opt++) {
                        var letter = String.fromCharCode(65 + opt);
                        if (QUESTIONS_LIST[n]['question_answer'] == OPTIONS[opt]["option_name"]) {
                            var correctOptionText = letter + ') ' + OPTIONS[opt]["option_name"];
                            var correctOptionHTML = '<div  class="form-label">' + correctOptionText + '&ensp;<i class="fas fa-times" style="color:#ff5e0e "></i></div>';
                            if (OPTIONS[opt]["option_answer"] == "Y") {
                                correctOptionHTML = '<div  class="form-label">' + correctOptionText + '&ensp;<i class="fas fa-check" style="color:#73d973"></i><i class="fas fa-check" style="color:#73d973 "></i></div>';
                            }
                            $("#question_options_" + QUESTIONS_LIST[n]['id']).append(correctOptionHTML);
                        } else {
                            var tickMark = "";
                            if (OPTIONS[opt]["option_answer"] == "Y") {
                                tickMark = '<i class="fas fa-check" style="color:#73d973 "></i>';
                            }
                            var optionText = letter + ') ' + OPTIONS[opt]["option_name"];
                            var optionHTML = '<div  class="form-label">' + optionText + '&ensp;' + tickMark;
                            if (QUESTIONS_LIST[n]['question_answer'] == OPTIONS[opt]["option_name"]) {
                                optionHTML += '<i class="fas fa-check" style="color:#73d973 "></i>';
                            }
                            optionHTML += '</div>';
                            $("#question_options_" + QUESTIONS_LIST[n]['id']).append(optionHTML);
                        }
                    }
                }
            }
            if (QUESTIONS_LIST.length > 0) {

                if (DATA['questions_tobe_evaluated'] == 0) {
                    is_submission_evaluated = true
                } else {
                    is_submission_evaluated = false
                }
                if(DATA['questions_tobe_evaluated'] == 0){
                    $(".eval-question-section").append(`<button type="button" class="btn btn-primary mt-3 float-right send-result" id="send_result_pid_${DATA['selected_participants']}" onclick="confirm_and_RESEND_result(${DATA['selected_participants']})" >Resend Result</button>`)
                }else{
                    $(".eval-question-section").append(`<button type="button" class="btn btn-primary mt-3 float-right send-result" id="send_result_pid_${DATA['selected_participants']}" onclick="confirm_and_SEND_result(${DATA['selected_participants']})" disabled>Send Result</button>`)
                }
                
                // ${DATA['questions_tobe_evaluated'] == 0 ? '' : 'disabled'}
            }
            $('body').removeClass('cursor-progress');
            $('p[name="papers"]').removeClass('cursor-progress')
            $('tr[name="participants"]').removeClass('cursor-progress')
            $(".papers-card").removeClass("loading");
            $(".participants-card").removeClass("loading");


        } else {
            Swal.fire({
                icon: 'error',
                title: 'Could not process your request',
                text: 'Internal Server Error',
                footer: 'Please contact administrator',
                confirmButtonText: 'OK',
                confirmButtonColor: '#274699'
            })
            $('body').removeClass('cursor-progress');
            $('p[name="papers"]').removeClass('cursor-progress')
            $('tr[name="participants"]').removeClass('cursor-progress')
            $(".papers-card").removeClass("loading");
            $(".participants-card").removeClass("loading");
        }
    })
}


function confirm_and_SEND_result(pid_){
    const primaryColor = getComputedStyle(document.documentElement).getPropertyValue('--primary-color').trim();
    const secondaryColor = getComputedStyle(document.documentElement).getPropertyValue('--secondary-color').trim();
    Swal.fire({
        title: "Confirm to send results to candidate",
        text: "Based on promote level the furthur process is carried out.",
        icon: "info",
        showCancelButton: true,
        confirmButtonColor: primaryColor,
        cancelButtonColor: secondaryColor,
        confirmButtonText: "Confirm"
      }).then((result) => {
        if (result.isConfirmed) {
            send_evaluation_result(pid_)
        }
      });
}



function confirm_and_RESEND_result(pid_){
    const primaryColor = getComputedStyle(document.documentElement).getPropertyValue('--primary-color').trim();
    const secondaryColor = getComputedStyle(document.documentElement).getPropertyValue('--secondary-color').trim();
    Swal.fire({
        title: "Results are already sent to candidate. Confirm to Resend.",
        text: "The applicant is already proceeded to next level based on promote level. Resending may distrub the application workflow",
        icon: "warning",
        showCancelButton: true,
        confirmButtonColor: primaryColor,
        cancelButtonColor: secondaryColor,
        confirmButtonText: "Confirm",
        cancelButtonText:"Cancel"
        
      })
      .then((result) => {
        if (result.isConfirmed) {
            send_evaluation_result(pid_)
        }
      });
}


function send_evaluation_result(pid_) {

    if (is_submission_evaluated) {
        $(".send-result").prop("disabled",true);
        $("#send_result_pid_"+pid_).text("Please Wait...");

        dataObj = {
            "request_for": "send_evaluation_result",
            "paper_id": paper_id,
            "participant_id": pid_
        }

        var final_data = {
            'data': JSON.stringify(dataObj),
            csrfmiddlewaretoken: CSRF_TOKEN,
        }
        $.post(CONFIG['portal'] + "/api/evaluation", final_data, function (res) {

            $(".send-result").prop("disabled",false);
            $("#send_result_pid_"+pid_).text("Send Result");

            if (res.statusCode == 0) {
                if (res.data == "insufficent_credits"){
                    Swal.fire({
                        icon: 'warning',
                        title: 'Insufficent Credits',
                        text: 'Please load the credits and try again',
                        footer: 'Please contact hirelines support',
                        confirmButtonText: 'OK',
                        confirmButtonColor: '#274699'
                    })
                }else{
                    $("#send_result_pid_" + pid_).text("Resend Result");
                    $("#send_result_pid_" + pid_).attr("onclick", "confirm_and_RESEND_result(" + pid_ + ")");
                    Swal.fire({
                        icon: 'success',
                        title: 'Result mail sent to candidate successfully',
                        confirmButtonText: 'OK',
                        confirmButtonColor: '#274699'
                    })
                }
                
            }else{
                Swal.fire({
                    icon: 'error',
                    title: 'Could not process your request',
                    text: 'Internal Server Error',
                    footer: 'Please contact administrator',
                    confirmButtonText: 'OK',
                    confirmButtonColor: '#274699'
                })
            }
        })

    }
    else {
        console.log("is_submission_evaluated:", is_submission_evaluated);
    }
}







function accord() {
    $(this).toggleClass("sel-eval-question");
    const icon = $(this).find('.acc_icon');

    // Toggle classes for the icon
    if (icon.hasClass('bxs-chevron-right')) {
        icon.removeClass('bxs-chevron-right').addClass('bxs-chevron-down');
    } else {
        icon.removeClass('bxs-chevron-down').addClass('bxs-chevron-right');
    }
    var panel = $(this).next();
    if (panel.css("display") === "block") {
        panel.css("display", "none");
    } else {
        panel.css("display", "block");
    }
}

function myFunction(question_sno) {
    var givenMarks = document.getElementById('ans_mark' + question_sno).value
    var totalMarks = document.getElementById("marks" + question_sno).value
    if (parseInt(totalMarks) > parseInt(givenMarks)) {
        $("#textareaContainer" + question_sno).show();
    } else {
        $("#textareaContainer" + question_sno).hide();
    }

}

function updateMarks(q_no) {


    var marks = document.getElementById('ans_mark' + q_no).value
    var reason_for_less_marks = document.getElementById('reason' + q_no).value
    var totalMarks = parseInt(document.getElementById("marks" + q_no).value);

    var trimmedString = reason_for_less_marks.trim();

    if (!marks) {

        Swal.fire({
            icon: 'warning',
            title: 'Please enter marks',
            confirmButtonText: 'OK',
            confirmButtonColor: '#274699'
        })
    }

    else if (marks < totalMarks && !trimmedString) {

        Swal.fire({
            icon: 'warning',
            title: 'Enter reason for less marks',
            confirmButtonText: 'OK',
            confirmButtonColor: '#274699'
        })
    }


    else {
        dataObj = {
            "request_for": "update_marks",
            'answer_marks': marks,
            'reason_for_less_marks': reason_for_less_marks,
            'answer_id': $('#ans_mark' + q_no).attr('name')
        };

        var final_data = {
            'data': JSON.stringify(dataObj),
            csrfmiddlewaretoken: CSRF_TOKEN,
        };

        if (marks > totalMarks) {

            Swal.fire({
                icon: 'warning',
                title: 'Please enter valid Marks',
                confirmButtonText: 'OK',
                confirmButtonColor: '#274699'
            })
        } else {
            $('body').addClass('cursor-progress');
            $('button[name="update_marks_btns"]').prop('disabled', true);
            $.post(CONFIG['portal'] + "/api/evaluation", final_data, function (res) {
                var marks = res.answer_data.secured_marks;
                $('#total_marks').html('');
                $('#total_marks').append(
                    '<label style="text-transform: capitalize;" id="total_marks">' + marks + '&ensp;&ensp;' + '</label>'
                );
                $("#secured_marks").html("");
                $("#secured_marks").html("Secured Marks: "+ marks);

                if (res.statusCode == 0) {
                    notifyNow($('[data-notify]'));
                    $('body').removeClass('cursor-progress');
                    $('button[name="update_marks_btns"]').prop('disabled', false);
                    $('button[name="update_marks_btns"]').prop('disabled', false);

                    var $eval_ques_div_element = $('button[name="eval_ques_' + q_no + '"');
                    var $ans_line = $('<div class="ans-color-line"></div>');
                    $eval_ques_div_element.prepend($ans_line);
                    if (res.answer_data.questions_tobe_evaluated == 0) {
                        is_submission_evaluated = true
                        $("#send_result_pid_" + res.answer_data.participant_id).prop("disabled", false);
                    } else {
                        is_submission_evaluated = false
                        $("#send_result_pid_" + res.answer_data.participant_id).prop("disabled", true);
                    }
                } else {

                    Swal.fire({
                        icon: 'error',
                        title: 'Could not process your request',
                        text: 'Internal Server Error',
                        confirmButtonText: 'OK',
                        confirmButtonColor: '#274699',
                        footer: 'Please contact administrator'
                    })
                    $('body').removeClass('cursor-progress');
                    $('button[name="update_marks_btns"]').prop('disabled', false);
                }
            });
        }
    }
}

function notifyNow() {
    var $button = $('[data-notify]');
    var message = 'Marks Saved';
    var options = $button.data('options') || {};

    options = $.extend({}, options, { pos: 'center-right', timeout: 1500 });

    $.notify(message, options);
}


function Incorrect(s_no) {
    document.getElementById('ans_mark' + s_no).value = 0;
    $("#textareaContainer" + s_no).show();
    var reasonValue = document.getElementById('reason' + s_no).value;

    if (!reasonValue) {
        document.getElementById('reason' + s_no).value = "Incorrect Answer";
    }
}

// var showing = [1, 0, 0];
// var questions = ["questions"];
// function nextquestion() {
//     var questionsElems = [];
//     for (var i = 0; i < questions.length; i++) {
//         questionsElems.push(document.getElementById(questions[i]));   
//     }
//     for (var i = 0; i < showing.length; i++) {
//         if (showing[i] == 1) {
//             questionsElems[i].style.display = 'none';
//             showing[i] = 0;
//             if (i == showing.length - 1) {
//                 questionsElems[0].style.display = 'block';
//                 showing[0] = 1;
//             } else {
//                 qElems[i + 1].style.display = 'block';
//                 showing[i + 1] = 1;
//             }
//             break;
//         }
//     }      
// }


var acc = document.getElementsByClassName("accordion");
var showing = new Array(acc.length).fill(0);
showing[0] = 1;

function nextquestion() {
    var questionsElems = [];
    for (var i = 0; i < acc.length; i++) {
        questionsElems.push(acc[i]);
    }
    for (var i = 0; i < showing.length; i++) {
        if (showing[i] == 1) {
            acc[i].classList.toggle("sel-eval-question");
            acc[i].nextElementSibling.style.display = "none";
            showing[i] = 0;
            var nextIndex = (i + 1) % acc.length;
            acc[nextIndex].classList.toggle("sel-eval-question");
            acc[nextIndex].nextElementSibling.style.display = "block";
            showing[nextIndex] = 1;
            break;
        }
    }
}

function showNextParticipant() {
    currentParticipantIndex++;
    if (currentParticipantIndex >= PARTICIPANT.length) {
        currentParticipantIndex = 0;
    }
    var nextParticipantPid = PARTICIPANT[currentParticipantIndex]["pid"];
    filter_data(null, nextParticipantPid);
}

function getTextareaRows(text) {
    const lines = text.split('\n').length;
    const additionalRows = 2;
    return lines + additionalRows;
}