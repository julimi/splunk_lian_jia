require([
    'splunkjs/mvc/utils',
    'splunkjs/mvc/tokenutils',
    'splunkjs/mvc/tableview',
    'splunkjs/mvc/chartview',
    'splunkjs/mvc/searchmanager',
    'splunkjs/mvc',
    'underscore',
    'jquery',
    "splunkjs/mvc/simplexml/urltokenmodel",
    'splunkjs/mvc/simplexml/ready!'],function(
    utils,
    TokenUtils,
    TableView,
    ChartView,
    SearchManager,
    mvc,
    _,
    $,
    UrlTokenModel
    ){
    // 
    // TOKENS
    //
        
    // Create token namespaces
    var urlTokenModel = mvc.Components.getInstance('url', {create: true});
    var defaultTokenModel = mvc.Components.getInstance('default', {create: true});
    var submittedTokenModel = mvc.Components.getInstance('submitted', {create: true});

    urlTokenModel.on('url:navigate', function() {
        defaultTokenModel.set(urlTokenModel.toJSON());
        if (!_.isEmpty(urlTokenModel.toJSON()) && !_.all(urlTokenModel.toJSON(), _.isUndefined)) {
            submitTokens();
        } else {
            submittedTokenModel.clear();
        }
    });

    // Initialize tokens
    defaultTokenModel.set(urlTokenModel.toJSON());

    function submitTokens() {
        // Copy the contents of the defaultTokenModel to the submittedTokenModel and urlTokenModel
        FormUtils.submitForm({ replaceState: pageLoading });
    }

    function setToken(name, value) {
        defaultTokenModel.set(name, value);
        submittedTokenModel.set(name, value);
    }

    function unsetToken(name) {
        defaultTokenModel.unset(name);
        submittedTokenModel.unset(name);
    }
    var EventSearchBasedRowExpansionRenderer = TableView.BaseRowExpansionRenderer.extend({
        initialize: function(args) {
            // initialize will run once, so we will set up a search and a chart to be reused.
            this._searchManager = new SearchManager({
                id: 'details-search-manager',
                preview: false,
                earliest_time: '-1y@y',
                latest_time: 'now',
            });
            this._searchManager1 = new SearchManager({
                id: 'details-search-manager1',
                preview: false,
                earliest_time: '-1y@y',
                latest_time: 'now',
            });
            this._chartView = new ChartView({
                managerid: 'details-search-manager',
                'charting.legend.placement': 'none',
                'charting.chart': 'column',
                'charting.chart.showDataLabels': 'minmax',
                'charting.drilldown': 'none'
            });
            this._tableView = new TableView({
                managerid: 'details-search-manager1',
                'dataOverlayMode': 'none',
                'wrap': 'true',
                'drilldown': 'cell',
                'pageSize': 20
            });
            this._tableView.on("click", function(e) {
                if (e.field !== undefined) {
                    e.preventDefault();
                    var url = TokenUtils.replaceTokenNames("/app/lian_jia_simple/jing_an_test?address=$click.value$", _.extend(submittedTokenModel.toJSON(), e.data), TokenUtils.getEscaper('url'), TokenUtils.getFilters(mvc.Components));
                    utils.redirect(url, false, "_blank");
                }
            });
        },
        canRender: function(rowData) {
            // Since more than one row expansion renderer can be registered we let each decide if they can handle that
            // data
            // Here we will always handle it.
            return true;
        },
        render: function($container, rowData) {
            // rowData contains information about the row that is expanded.  We can see the cells, fields, and values
            // We will find the sourcetype cell to use its value
            var districtCell = _(rowData.cells).find(function (cell) {
               return cell.field === 'district_name';
            });
            //update the search with the sourcetype that we are interested in
            console.log("search manager: ", this._searchManager.earliest_time)
            this._searchManager.set({ search: 'index="lianjia" district_name=' + districtCell.value + ' second_hand_unit_price!=0'
            + ' | stats avg(second_hand_unit_price) as average_price by biz_circle_name'
            + ' | eval average_price=round(average_price)'});
            // $container is the jquery object where we can put out content.
            // In this case we will render our chart and add it to the $container
            $container.append(this._chartView.render().el);
            this._searchManager1.set({ search: 'index="lianjia" district_name=' + districtCell.value + ' second_hand_unit_price!=0'
            + ' | table name, biz_circle_name, second_hand_unit_price'});
            // $container is the jquery object where we can put out content.
            // In this case we will render our chart and add it to the $container
            $container.append(this._tableView.render().el);
        }
    });
    var tableElement = mvc.Components.getInstance("price_comparison");
    tableElement.getVisualization(function(tableView) {
        // Add custom cell renderer, the table will re-render automatically.
        tableView.addRowExpansionRenderer(new EventSearchBasedRowExpansionRenderer());
    });
});