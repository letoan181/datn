odoo.define('web.fix_menu_js', function (require) {
    "use strict";
    var core = require('web.core');
    var menu = require('web.Menu');

    menu.include({
        change_menu_section: function (primary_menu_id) {
            if (!this.$menu_sections[primary_menu_id]) {
                return; // unknown menu_id
            }
            if (this.current_primary_menu === primary_menu_id) {
                return; // already in that menu
            }
            if (this.current_primary_menu) {
                this.$menu_sections[this.current_primary_menu].detach();
            }
            // Get back the application name
            for (var i = 0; i < this.menu_data.children.length; i++) {
                if (this.menu_data.children[i].id === primary_menu_id) {
                    this.$menu_brand_placeholder.text(this.menu_data.children[i].name);
                    break;
                }
            }
            this.$menu_sections[primary_menu_id].appendTo(this.$section_placeholder);
            this.current_primary_menu = primary_menu_id;
            core.bus.trigger('resize');
        },
    })
});