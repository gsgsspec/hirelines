/**
 * Perfect Scrollbar
 */
'use strict';

document.addEventListener('DOMContentLoaded', function () {
  (function () {
    var verticalExample = document.getElementById('sectionTitlesContainer')
    var ques_container_verti_scroll = document.getElementById('question_container_vertical_scroll')
    var skillsListScroll = document.getElementById('skillListScroll'),
      horizontalExample = document.getElementById('horizontal-example'),
      horizVertExample = document.getElementById('both-scrollbars-example');

    // Vertical Example
    // --------------------------------------------------------------------
    if (verticalExample) {
      new PerfectScrollbar(verticalExample, {
        wheelPropagation: false
      });
    }

    

    if (ques_container_verti_scroll) {
      new PerfectScrollbar(ques_container_verti_scroll, {
        wheelPropagation: false
      });
    }

    // Horizontal Example
    // --------------------------------------------------------------------
    if (horizontalExample) {
      new PerfectScrollbar(horizontalExample, {
        wheelPropagation: false,
        suppressScrollY: true
      });
    }

      // skillsListScroll 
    // --------------------------------------------------------------------
    if (skillsListScroll) {
      new PerfectScrollbar(skillsListScroll, {
        wheelPropagation: false,
        suppressScrollY: true
      });
    }

    // Both vertical and Horizontal Example
    // --------------------------------------------------------------------
    if (horizVertExample) {
      new PerfectScrollbar(horizVertExample, {
        wheelPropagation: false
      });
    }
  })();
});
