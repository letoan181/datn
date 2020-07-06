odoo.define('survey.question', function (require) {
    "use strict";
     var the_form = $('.js_surveyform');

    if (!the_form.length) {
        return Promise.reject("DOM doesn't contain '.js_surveyform'");
    }
    var submit_controller = the_form.attr("data-submit");
    $(".preview_submit").click(function (e) {
        var $valObj = $(this);
        e.preventDefault();
        $('<input>').attr({type: 'hidden', name: 'question_page_redirect', value: $valObj.attr('href')}).appendTo('.js_surveyform');
        $('.js_surveyform').submit()
        // $.ajax({
        //         type: "POST",
        //         dataType: 'json',
        //         url: url,
        //         contentType: "application/json; charset=utf-8",
        //         data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": params}),
        //         success: function () {
        //             $(window.location).attr('href', success_page);
        //         },
        //         error: function (data) {
        //             console.log("ERROR ", data);
        //         }
        //     });
    });

});