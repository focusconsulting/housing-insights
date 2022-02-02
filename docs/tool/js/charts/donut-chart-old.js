'use strict';
/*

Note, this chart does not inherit from the newer chart prototype - see template-inherited-chart for the preferred approach

*/

var DonutChartOld = function (chartOptions) {
  this.extendPrototype(DonutChartOld.prototype, DonutChartOldExtension);
  PieChartProto.call(this, chartOptions);
};

DonutChartOld.prototype = Object.create(PieChartProto.prototype);

var DonutChartOldExtension = {
  setup: function (chartOptions) {
    var chart = this;

    this.countType = chartOptions.count;

    this.totalUnits = this.countTotalUnits();

    chart.foreground = chart.svgCentered
      .append('path')
      .style('fill', '#fd8d3c')
      .datum({ endAngle: Math.PI });

    chart.percentage = chart.svgCentered
      .append('text')
      .attr('text-anchor', 'middle')
      .attr('class', 'pie_number')
      .attr('y', 5)
      .text(d3.format('.0%')(1));

    chart.label.text(chart.countType);

    chart.foreground
      .transition()
      .duration(750)
      .attrTween('d', chart.arcTween(Math.PI * 2));
  },
  countTotalUnits: function () {
    var units = 0;
    this.data.forEach(function (datum) {
      units += datum.proj_units_tot;
    });
    return units;
  },
  updateSubscriber: function (msg, data) {
    resultsView.charts.forEach(function (chart) {
      DonutChartOld.prototype.update.call(chart, data);
    });
  },
  update: function (filterData) {
    var chart = this;
    var factor;
    let filterUnitsCount;
    if (this.countType === 'Projects') {
      factor = filterData.length / this.data.length;
      chart.label.text(
        `${filterData.length.toLocaleString()} ${chart.countType}`
      );
    } else {
      [factor, filterUnitsCount] = returnUnitFactor();
      chart.label.text(
        `${filterUnitsCount.toLocaleString()} ${chart.countType}`
      );
    }

    this.foreground
      .transition()
      .duration(750)
      .attrTween('d', this.arcTween(factor * Math.PI * 2));

    this.percentage.text(d3.format('.0%')(factor));

    function returnUnitFactor() {
      var filteredProjects = chart.data.filter(function (datum) {
        return filterData.indexOf(datum.nlihc_id) !== -1;
      });
      var unitCounts = 0;
      filteredProjects.forEach(function (project) {
        unitCounts += project.proj_units_tot;
      });
      return [unitCounts / chart.totalUnits, unitCounts];
    }
  },
};
