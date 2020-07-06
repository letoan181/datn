odoo.define('error_management.crash_manager', function (require) {
    var CrashManager = require('web.CrashManager');
    CrashManager.include({
        show_error: function (error) {
            return;
        },
    })
    return CrashManager;
});