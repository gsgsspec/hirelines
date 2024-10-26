var paper_id = null;
var participant_id = null;
var currentParticipantIndex = 0;
var PARTICIPANT = [];
var hide_reg_number_flag = $("#p_flag").attr('name');
$(document).ready(function () {
    
    get_papers_data();
    
})
function get_papers_data() {
    $.get("http://localhost:8001" + "/api/evaluation-papers", function (res) {
        console.log("res",res);
        
        if (res.statusCode == 0){
            var papers_data = res.data;
            console.log("papers_data",papers_data);
            papers_data.map((paper, index) => {
                
                $("#papers").append(`<p onclick="filter_data(${paper.id},null)" name="papers" id="paper_${paper.id}" class=" form-label cursor-pointer" >${paper.paper_code} - ${paper.paper_name}  (${paper.paper_count})</p>`)
            })
            
            $("p[name='papers']:first").click();
        }else{
            Swal.fire({
                icon: 'error',
                title: 'Could not process request',
                text: 'Internal Server Error',
                footer: 'Please contact administrator'
              })
        }
        // 
    })
}




function filter_data(pid, ptid) {
    if (pid) {
        paper_id = pid;
    }
    if (ptid) {
        participant_id = ptid;
    }
    dataObj = {
        "paper_id": paper_id,
        "participant_id": participant_id,
    }

    var final_data = {
        'data': JSON.stringify(dataObj),
        csrfmiddlewaretoken: CSRF_TOKEN,
    }
    $.post("http://localhost:8001" + "/api/evaluation-papers", final_data, function (res) {
        console.log("res",res);
        
        if (res.statusCode == 0) {  
            var DATA = res.data;
            // console.log('Data',DATA)
            PARTICIPANT = DATA.participants;
            // console.log('participants',PARTICIPANT)
            var QUESTIONS = DATA.questions;
            var PAPER_NAME = DATA.paper_name;
            var PARTICIPANT_NAME = DATA.name;
            var PARTICIPANT_LAST_NAME = DATA.l_name;
            var MARKS = DATA.total_marks;


            $('#participants').html('');
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
                    '<tr onclick="filter_data(null,' + PARTICIPANT[n]["pid"] + ')" name="participants" id="participant_' + PARTICIPANT[n]["pid"] + '" class="top cursor-pointer" style="text-transform: capitalize">'
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
            $("#participant_" + DATA["selected_participants"]).addClass("selection-item")

            participant_id = null;

            $("#questions").html('');
            var QUESTIONS_LIST = DATA.questionlist


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
                    question_options_div = '<div class="options-grid-container p-10" id="question_options_' + QUESTIONS_LIST[n]['id'] + '"></div>'
                }
                if (QUESTIONS_LIST[n]["question_type_code"] == "B") {
                    question_options_div = '<div class="options-grid-container p-10" id="question_options_' + QUESTIONS_LIST[n]['id'] + '"></div>'
                }
                if (QUESTIONS_LIST[n]['question_type_code'] == "P") {
                    question_options_div = '<p style="padding:13px">' + '<b>Answer :  </b>  ' + QUESTIONS_LIST[n]['question_answer'] + '</p>';
                    question_expanswer_div = '<p style="padding:13px">' + '<b>Expected Answer :  </b>  ' + QUESTIONS_LIST[n]['question_expected_answer'] + '</p>';
                    evaluation_btns = '<div class="float-right">' +
                        '<button class="mb-1 btn btn-cancel btn_width" style="background-color: #73d973 !important" id="save" onclick="DisplayValue(' + question_sno + ')"><i style="padding-right:10px" class="fas fa-check"></i><b>Correct</b></button>' +
                        '<button class="mb-1 btn btn-primary btn_width ml-2" style="background-color:#ff0000bd !important" onclick="Incorrect(' + question_sno + '); DisplayValue(' + question_sno + ')" ><i style="padding-right:6px" class="fas fa-times"></i><b>Incorrect</b></button>' +
                        '</div>'
                }
                
                if (QUESTIONS_LIST[n]["question_type_code"] == "C" || QUESTIONS_LIST[n]["question_type_code"] == "R"  || QUESTIONS_LIST[n]["question_type_code"] == "O" ) {

                    answer = QUESTIONS_LIST[n]['question_answer']

                    if(answer){
                        rows = getTextareaRows(QUESTIONS_LIST[n]['question_answer']);
                    }else {
                        rows = 2
                        answer = ""
                    }

                    question_options_div = '<div style="display:flex;justify-content:space-between;width:700px"><p style="padding-top:13px"> <b>Question Type :</b>  '+ QUESTIONS_LIST[n]['question_type_name'] +' </p><p style="padding-top:13px"> <b>Time used :</b>  '+ QUESTIONS_LIST[n]['question_time_used'] +' </p></div>' +
                        '<label>Code :</label><textarea style="width: 700px;" class="form-control" rows="'+ rows +'" disabled>' + 
                        answer + 
                        '</textarea> <br>';

                }

                if (QUESTIONS_LIST[n]["question_type_code"] == "A") {
                    question_expanswer_div = '<p style="padding:13px">' + '<b>Expected Answer :  </b>  ' + QUESTIONS_LIST[n]['question_expected_answer'] + '</p>';
                    question_options_div = '<br/><audio id="play_audio" style="width:500px" controls><source  src="' + QUESTIONS_LIST[n]["response_media"] + '"/></audio><br/><br/>'
                    evaluation_btns = '<div class="float-right">' +
                        '<button class="mb-1 btn btn-cancel btn_width" style="background-color: #73d973 !important" id="save" onclick="DisplayValue(' + question_sno + ')"><i style="padding-right:10px" class="fas fa-check"></i><b>Correct</b></button>' +
                        '<button class="mb-1 btn btn-primary btn_width ml-2" style="background-color:#ff0000bd !important" onclick="Incorrect(' + question_sno + '); DisplayValue(' + question_sno + ')" ><i style="padding-right:6px" class="fas fa-times"></i><b>Incorrect</b></button>' +
                        '</div>'
                }

                if (QUESTIONS_LIST[n]["question_type_code"] == "V") {
                    question_expanswer_div = '<p style="padding:13px">' + '<b>Expected Answer :  </b>  ' + QUESTIONS_LIST[n]['question_expected_answer'] + '</p>';
                    if(QUESTIONS_LIST[n]["response_media"]){
                        question_options_div = '<br/>' +
                        '<h4>Response video</h4><video class="video-resp-window" controls><source  src="' + QUESTIONS_LIST[n]["response_media"] + '" width="200"/></video><br/>'
                    }else{
                        question_options_div = '<br/>'
                    }
                    
                    evaluation_btns = '<div class="float-right">' +
                        '<button class="mb-1 btn btn-cancel btn_width" style="background-color: #73d973 !important" id="save" onclick="DisplayValue(' + question_sno + ')"><i style="padding-right:10px" class="fas fa-check"></i><b>Correct</b></button>' +
                        '<button class="mb-1 btn btn-primary btn_width ml-2" style="background-color:#ff0000bd !important" onclick="Incorrect(' + question_sno + '); DisplayValue(' + question_sno + ')" ><i style="padding-right:6px" class="fas fa-times"></i><b>Incorrect</b></button>' +
                        '</div>'
                }


                accord_style = ''
                if (QUESTIONS_LIST[n]["answer_marks"] !== "") {
                    accord_style = '<div class="ans-color-line"></div>'
                }

                else {
                    accord_style = ''
                }
                

                $("#questions").append(
                    '<button class="accordion" id="questions">' + accord_style +
                    '<div class="w-100p text-left " style="font-weight:600">' + question_sno + '.' + ' ' + QUESTIONS_LIST[n]["question"] + '</div>' +

                    '</button>' +
                    '<div class="panel" id="questions">' +
                    anser_skip_resp +
                    question_image +
                    question_audio +
                    question_video +
                    question_options_div +
                    question_expanswer_div +
                    '<div class="form-group row" style="margin-left:11px">' +
                    '<label class="marks-label">Total Marks:</label>' +
                    '<div class="marks-display">' +
                    '<input class="form-control" type="text" value="' + QUESTIONS_LIST[n]['question_mark'] + '" maxlength="100" id="marks' + question_sno + '" disabled>' +
                    '</div>' +
                    '<label class="marks-label">Given Marks:</label>' +
                    '<div class="marks-display">' +
                    '<input oninput="myFunction(' + question_sno + ')" class="form-control given-marks" name="' + QUESTIONS_LIST[n]['answer_id'] + '" id="ans_mark' + question_sno + '" value="' + QUESTIONS_LIST[n]['answer_marks'] + '" required>' +
                    '</div>' +
                    '</div>' +
                    '<div class="form-group row"  id="textareaContainer' + question_sno + '"  style="display:none;" >' + '<label class="marks-label" style="width: 13em;padding-left: 27px;">Reason for less Marks:</label>' +
                    '<textarea style="width: 400px;" class="form-control exp-ans-text"  id="reason' + question_sno + '"  rows="4" maxlength="256" required>'+ QUESTIONS_LIST[n]['reason'] +'</textarea>' +
                    '</div>' +
                    evaluation_btns +
                    '</div>'
                    
                )

                if (parseInt(QUESTIONS_LIST[n]['question_mark']) > parseInt(QUESTIONS_LIST[n]['answer_marks'])) {
                    $("#textareaContainer" + question_sno).show();
                } else {
                    $("#textareaContainer" + question_sno).hide();
                }

                if ((QUESTIONS_LIST[n]["question_type_code"] == "C") || (QUESTIONS_LIST[n]["question_type_code"] == "R") || (QUESTIONS_LIST[n]["question_type_code"] == "O")  ){
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
                            var correctOptionHTML = '<div>' + correctOptionText + '&ensp;<i class="fas fa-times" style="color:#ff5e0e "></i></div>';
                            if (OPTIONS[opt]["option_answer"] == "Y") {
                                correctOptionHTML = '<div>' + correctOptionText + '&ensp;<i class="fas fa-check" style="color:#73d973"></i><i class="fas fa-check" style="color:#73d973 "></i></div>';
                            }
                            $("#question_options_" + QUESTIONS_LIST[n]['id']).append(correctOptionHTML);
                        } else {
                            var tickMark = "";
                            if (OPTIONS[opt]["option_answer"] == "Y") {
                                tickMark = '<i class="fas fa-check" style="color:#73d973 "></i>';
                            }
                            var optionText = letter + ') ' + OPTIONS[opt]["option_name"];
                            var optionHTML = '<div>' + optionText + '&ensp;' + tickMark;
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
                            var correctOptionHTML = '<div>' + correctOptionText + '&ensp;<i class="fas fa-times" style="color:#ff5e0e "></i></div>';
                            if (OPTIONS[opt]["option_answer"] == "Y") {
                                correctOptionHTML = '<div>' + correctOptionText + '&ensp;<i class="fas fa-check" style="color:#73d973"></i><i class="fas fa-check" style="color:#73d973 "></i></div>';
                            }
                            $("#question_options_" + QUESTIONS_LIST[n]['id']).append(correctOptionHTML);
                        } else {
                            var tickMark = "";
                            if (OPTIONS[opt]["option_answer"] == "Y") {
                                tickMark = '<i class="fas fa-check" style="color:#73d973 "></i>';
                            }
                            var optionText = letter + ') ' + OPTIONS[opt]["option_name"];
                            var optionHTML = '<div>' + optionText + '&ensp;' + tickMark;
                            if (QUESTIONS_LIST[n]['question_answer'] == OPTIONS[opt]["option_name"]) {
                                optionHTML += '<i class="fas fa-check" style="color:#73d973 "></i>';
                            }
                            optionHTML += '</div>';
                            $("#question_options_" + QUESTIONS_LIST[n]['id']).append(optionHTML);
                        }
                    }
                }
            }
        }
    })
}








function accord() {
    $(this).toggleClass("active");
    var panel = $(this).next();
    if (panel.css("display") === "block") {
        panel.css("display", "none");
    } else {
        panel.css("display", "block");
    }
}

function myFunction(question_sno) {
    var givenMarks = document.getElementById('ans_mark'+question_sno).value
    var totalMarks = document.getElementById("marks"+question_sno).value
    if (parseInt(totalMarks) > parseInt(givenMarks)) {
        $("#textareaContainer"+question_sno).show();
    } else {
        $("#textareaContainer"+question_sno).hide();
    }

}

function DisplayValue(q_no) {
    var marks = document.getElementById('ans_mark' + q_no).value
    var reason_for_less_marks = document.getElementById('reason' + q_no).value
    var totalMarks = parseInt(document.getElementById("marks" + q_no).value);

    var trimmedString = reason_for_less_marks.trim();
    
    if (!marks) {
        swal("Please enter marks", "", "error");
    }

   else if (marks < totalMarks && !trimmedString) {
        swal("Enter reason for less marks", "", "error");
    } 
     
    
    else {
        dataObj = {
            'answer_marks': marks,
            'reason_for_less_marks': reason_for_less_marks,
            'answer_id': $('#ans_mark' + q_no).attr('name')
        };
    
        var final_data = {
            'data': JSON.stringify(dataObj),
            csrfmiddlewaretoken: CSRF_TOKEN,
        };
    
        if (marks > totalMarks) {
            swal("Please enter valid Marks", "", "error");
        } else {
            $.post(CONFIG['domain'] + "/api/evaluationmarks", final_data, function (res) {
                var marks = res.answer_data;
                $('#total_marks').html('');
                $('#total_marks').append(
                    '<label style="text-transform: capitalize;" id="total_marks">' + marks + '&ensp;&ensp;' + '</label>'
                );
    
                if (res.statusCode == 0) {
                    notifyNow($('[data-notify]'));
                } else {
                    swal("Internal Server Error", "", "error");
                }
            });
        }
    }
}

function notifyNow() {
    var $button = $('[data-notify]');
    var message = 'Marks Saved';
    var options = $button.data('options') || {};

    options = $.extend({}, options, { pos: 'center-right' , timeout: 1500});

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
            acc[i].classList.toggle("active");
            acc[i].nextElementSibling.style.display = "none";
            showing[i] = 0;
            var nextIndex = (i + 1) % acc.length;
            acc[nextIndex].classList.toggle("active");
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