require([
    'underscore',
    'jquery',
    'splunkjs/mvc',
    'splunkjs/mvc/tableview',
    'splunkjs/mvc/simplexml/ready!'
], function(_, $, mvc, TableView) {
    var CustomIconRenderer = TableView.BaseCellRenderer.extend({
        canRender: function(cell) {
            return cell.field === 'average_price';
        },
        render: function($td, cell) {
            var price = cell.value;
            // Compute the icon base on the field value
            var icon;
            if(price > 70000) {
                icon = 'alert-circle';
            } else {
                icon = 'check';
            }
            $td.addClass('icon-inline numeric').html(_.template('<%- text %> <i class="icon-<%-icon%>"></i>', {
                icon: icon,
                text: cell.value
            }));
            // } else if(count > 1000) {
            //     icon = 'alert';
            // } else {
            //     icon = 'check';
            // }
            // Create the icon element and add it to the table cell
        }
    });
    mvc.Components.get('price_comparison').getVisualization(function(tableView){
        // Register custom cell renderer, the table will re-render automatically
        tableView.addCellRenderer(new CustomIconRenderer());
    });
});