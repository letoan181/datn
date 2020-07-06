odoo.define('course.overview.toggle', function (require) {
    var publicWidget = require('web.public.widget');
    publicWidget.registry.websiteSlidesAllList = publicWidget.Widget.extend({
        selector: '.caret',
        xmlDependencies: ['/advanced_slide/views/survey_template.xml'],
        events: {
            'click': '_onClick',
        },
        _onClick: function (ev) {
            ev.preventDefault();
            ev.currentTarget.parentElement.querySelector(".nested").classList.toggle("active");
            ev.currentTarget.classList.toggle("caret-down");
        },

    });
});


