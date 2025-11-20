/** @odoo-module **/

export class AcsChart {

    async acsCreateAm4Chart(container, options = {}) {
        const { useAnimatedTheme = true, disableLogo = true } = options;
        if (useAnimatedTheme) {
            am4core.useTheme(am4themes_animated);
        }

        // Dispose existing chart first
        await this.acsDisposeChart(container);

        const chart = am4core.create(container, am4charts.XYChart);
        if (disableLogo) chart.logo.disabled = true;

        // Save reference to container
        container.chart = chart;
        return chart;
    }

    async acsDisposeChart(container) {
        if (container && container.chart) {
            try {
                container.chart.dispose();
            } catch (e) {
                console.warn("Error disposing chart:", e);
            }
            container.chart = null;
            await new Promise(r => setTimeout(r, 0));
        }
    }

    async acsAddScrollbar(chart, options = {}) {
        const scrollbar = new am4core.Scrollbar();
        if (options.opacity) scrollbar.opacity = options.opacity;
        chart.scrollbarX = scrollbar;
        return scrollbar;
    }

    // Bar Chart Helpers
    async acsCreateCategoryAxis(chart, options) {
        const categoryAxis = chart.xAxes.push(new am4charts.CategoryAxis());
        categoryAxis.dataFields.category = options.category;
        categoryAxis.renderer.grid.template.location = options.location;
        categoryAxis.renderer.minGridDistance = options.distance;
        categoryAxis.renderer.labels.template.horizontalCenter = options.horizontal;
        categoryAxis.renderer.labels.template.verticalCenter = options.verticalCenter;
        categoryAxis.renderer.labels.template.wrap = true;
        categoryAxis.renderer.labels.template.maxWidth = options.maxWidth || 120;
        categoryAxis.renderer.labels.template.rotation = options.rotation ?? 270;
        categoryAxis.renderer.labels.template.fill = am4core.color(options.labelColor || "#1B1833");
        categoryAxis.tooltip.disabled = true;
        
        const visibleCount = options.visibleCount || 10;
        categoryAxis.start = Math.max(0, 1 - visibleCount / (chart.data?.length || visibleCount));
        categoryAxis.end = 1;
        categoryAxis.keepSelection = true;
        return categoryAxis;
    }
    
    async acsCreateValueAxis(chart, options = {}) {
        const { minWidth = 50, labelColor = "#1B1833", strictMinMax = false } = options;
        const valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
        valueAxis.renderer.minWidth = minWidth;
        valueAxis.renderer.labels.template.fill = am4core.color(labelColor);
        if (strictMinMax) {
            valueAxis.strictMinMax = true;
        }
        return valueAxis;
    }

    async acsCreateColumnSeries(chart, options) {
        const {
            valueY,
            categoryX,
            tooltipText = `{${valueY}}`,
            cornerRadiusTopLeft = 10,
            cornerRadiusTopRight = 10,
            fillOpacity = 0.8,
            strokeWidth = 0,
            useDefaultColor = false
        } = options;

        const series = chart.series.push(new am4charts.ColumnSeries());
        series.sequencedInterpolation = true;
        series.dataFields.valueY = valueY;
        series.dataFields.categoryX = categoryX;
        series.tooltipText = tooltipText;
        series.columns.template.strokeWidth = strokeWidth;
        series.tooltip.pointerOrientation = "vertical";
        series.columns.template.column.cornerRadiusTopLeft = cornerRadiusTopLeft;
        series.columns.template.column.cornerRadiusTopRight = cornerRadiusTopRight;
        series.columns.template.column.fillOpacity = fillOpacity;
        if (!options.useDefaultColor) {
            series.columns.template.adapter.add("fill", (fill, target) => {
                return chart.colors.getIndex(target.dataItem.index);
            });
        }
        return series;
    }

    async acsSetColumnHoverState(series, options = {}) {
        const { cornerRadiusTopLeft = 0, cornerRadiusTopRight = 0, fillOpacity = 1 } = options;
        const hoverState = series.columns.template.column.states.create("hover");
        hoverState.properties.cornerRadiusTopLeft = cornerRadiusTopLeft;
        hoverState.properties.cornerRadiusTopRight = cornerRadiusTopRight;
        hoverState.properties.fillOpacity = fillOpacity;
        return hoverState;
    }

    // Line Chart Helpers
    async acsCreateDateAxis(chart, options = {}) {
        const {
            fillColor = "#1B1833",
            timeUnit = "day",
            count = 1,
            groupData = true,
            skipEmptyPeriods = true,
            dateFormats = { month: "MMM yyyy" },
            periodChangeDateFormats = { month: "MMM yyyy" },
        } = options;
        const dateAxis = chart.xAxes.push(new am4charts.DateAxis());
        dateAxis.renderer.labels.template.fill = am4core.color(fillColor);
        dateAxis.baseInterval = { timeUnit, count };
        dateAxis.groupData = groupData;
        dateAxis.skipEmptyPeriods = skipEmptyPeriods;
        for (const key in dateFormats) {
            dateAxis.dateFormats.setKey(key, dateFormats[key]);
        }
        for (const key in periodChangeDateFormats) {
            dateAxis.periodChangeDateFormats.setKey(key, periodChangeDateFormats[key]);
        }
        return dateAxis;
    }

    async acsCreateLineSeries(chart, options = {}) {
        const {
            valueY = "value",
            dateX = null,
            categoryX = null,
            tooltipText = `{${valueY}}`,
            strokeWidth = 2,
            minBulletDistance = 15,
            tooltipCornerRadius = 20,
        } = options;

        const series = chart.series.push(new am4charts.LineSeries());
        series.dataFields.valueY = valueY;
        if (dateX) series.dataFields.dateX = dateX;
        if (categoryX) series.dataFields.categoryX = categoryX;
        series.tooltipText = tooltipText;
        series.strokeWidth = strokeWidth;
        series.minBulletDistance = minBulletDistance;
        series.tooltip.background.cornerRadius = tooltipCornerRadius;
        series.tooltip.background.strokeOpacity = 0;
        series.tooltip.pointerOrientation = "vertical";
        series.tooltip.label.minWidth = 40;
        series.tooltip.label.minHeight = 40;
        series.tooltip.label.textAlign = "middle";
        series.tooltip.label.textValign = "middle";
        return series;
    }

    async acsAddCircleBullet(series, options = {}) {
        const {
            radius = 4,
            strokeWidth = 2,
            fillColor = "#fff",
            hoverScale = 1.3,
        } = options;
        const bullet = series.bullets.push(new am4charts.CircleBullet());
        bullet.circle.radius = radius;
        bullet.circle.strokeWidth = strokeWidth;
        bullet.circle.fill = am4core.color(fillColor);
        const bulletHover = bullet.states.create("hover");
        bulletHover.properties.scale = hoverScale;
        return bullet;
    }

    async acsConfigureChartCursor(chart, options = {}) {
        const {
            behavior = "panXY",
            xAxis = null,
            snapToSeries = null,
        } = options;
        const cursor = new am4charts.XYCursor();
        cursor.behavior = behavior;
        if (xAxis) cursor.xAxis = xAxis;
        if (snapToSeries) cursor.snapToSeries = snapToSeries;
        chart.cursor = cursor;
        return cursor;
    }

    // Radar(Guage) Chart Helpers
    async acsCreateRadarChart(container, options = {}) {
        const { 
            useAnimatedTheme = true, 
            disableLogo = true, 
            startAngle = -90, 
            endAngle = 180, 
            innerRadiusPercent = 20, 
            numberFormat = "#.#'%'" 
        } = options;
        if (useAnimatedTheme) am4core.useTheme(am4themes_animated);
        const chart = am4core.create(container, am4charts.RadarChart);
        if (disableLogo) chart.logo.disabled = true;
        chart.startAngle = startAngle;
        chart.endAngle = endAngle;
        chart.innerRadius = am4core.percent(innerRadiusPercent);
        chart.numberFormatter.numberFormat = numberFormat;
        return chart;
    }

    async acsCreateRadarCategoryAxis(chart, options = {}) {
        const { 
            categoryField = "age_group", 
            minGridDistance = 10, 
            labelColor = null, 
            fontWeight = 500 
        } = options;
        const categoryAxis = chart.yAxes.push(new am4charts.CategoryAxis());
        categoryAxis.dataFields.category = categoryField;
        categoryAxis.renderer.grid.template.location = 0;
        categoryAxis.renderer.grid.template.strokeOpacity = 0;
        categoryAxis.renderer.labels.template.horizontalCenter = "right";
        categoryAxis.renderer.labels.template.fontWeight = fontWeight;
        categoryAxis.renderer.minGridDistance = minGridDistance;
        if (!labelColor) {
            categoryAxis.renderer.labels.template.adapter.add("fill", (fill, target) => (target.dataItem.index >= 0 ? chart.colors.getIndex(target.dataItem.index) : fill));
        } else {
            categoryAxis.renderer.labels.template.fill = am4core.color(labelColor);
        }
        return categoryAxis;
    }

    async acsCreateRadarValueAxis(chart, options = {}) {
        const { 
            min = 0, 
            max = 100, 
            strictMinMax = true, 
            labelColor = "#9aa0ac" 
        } = options;
        const valueAxis = chart.xAxes.push(new am4charts.ValueAxis());
        valueAxis.renderer.grid.template.strokeOpacity = 0;
        valueAxis.min = min;
        valueAxis.max = max;
        valueAxis.strictMinMax = strictMinMax;
        valueAxis.renderer.labels.template.fill = am4core.color(labelColor);
        return valueAxis;
    }

    async acsCreateRadarColumnSeries(chart, options = {}) {
        const { 
            valueX, 
            categoryY, 
            cornerRadius = 20, 
            fillOpacity = 1, 
            fillColor = null, 
            tooltipText = `{${valueX}}` 
        } = options;
        const series = chart.series.push(new am4charts.RadarColumnSeries());
        series.dataFields.valueX = valueX;
        series.dataFields.categoryY = categoryY;
        series.clustered = false;
        series.columns.template.radarColumn.cornerRadius = cornerRadius;
        series.columns.template.strokeWidth = 0;
        series.columns.template.fillOpacity = fillOpacity;
        series.tooltipText = tooltipText;
        if (fillColor) {
            series.columns.template.fill = am4core.color(fillColor);
        } else {
            series.columns.template.adapter.add("fill", (fill, target) => chart.colors.getIndex(target.dataItem.index));
        }
        return series;
    }

    async acsConfigureRadarCursor(chart) {
        chart.cursor = new am4charts.RadarCursor();
        return chart.cursor;
    }

    // Pie Chart Helpers
    async acsCreatePieChart(container, method) {
        am4core.useTheme(am4themes_animated);
        if (container.chart) {
            container.chart.dispose();
        }
        var chart = am4core.create(container, am4charts.PieChart);
        chart.logo.disabled = true;
        const result = await method();
        return { chart, result };
    }

    async acsPieChartSeries(chart, valueField, categoryField, options = {}) {
        const pieSeries = chart.series.push(new am4charts.PieSeries());
        pieSeries.dataFields.value = valueField;
        pieSeries.dataFields.category = categoryField;
        pieSeries.slices.template.stroke = am4core.color("#fff");
        pieSeries.slices.template.strokeWidth = 2;
        pieSeries.slices.template.strokeOpacity = 1;
        pieSeries.labels.template.fill = am4core.color("#9aa0ac");
        pieSeries.slices.template.tooltipText = "{category}: {value.percent.formatNumber('#.0')}% ({value})";
        pieSeries.labels.template.disabled = true;
        pieSeries.ticks.template.disabled = true;
        pieSeries.hiddenState.properties.opacity = 1;
        pieSeries.hiddenState.properties.endAngle = -90;
        pieSeries.hiddenState.properties.startAngle = -90;

        chart.legend = new am4charts.Legend();
        if (options.legendPosition) chart.legend.position = options.legendPosition;
        if (options.legendMaxHeight) chart.legend.maxHeight = options.legendMaxHeight;
        if (options.legendMaxWidth) chart.legend.maxWidth = options.legendMaxWidth;
        if (options.legendScrollable) chart.legend.scrollable = true;
        if (options.legendFontSize) {
            chart.legend.labels.template.fontSize = options.legendFontSize;
            chart.legend.valueLabels.template.fontSize = options.legendFontSize;
        }
        if (options.legendMarkerSize) {
            chart.legend.markers.template.width = options.legendMarkerSize;
            chart.legend.markers.template.height = options.legendMarkerSize;
        }
        if (options.legendItemPadding !== undefined) {
            chart.legend.itemContainers.template.paddingTop = options.legendItemPadding;
            chart.legend.itemContainers.template.paddingBottom = options.legendItemPadding;
        }
        if (options.legendLabelWrap) {
            chart.legend.labels.template.wrap = true;
            chart.legend.labels.template.maxWidth = options.legendLabelWidth || 120;
        }
        chart.legend.width = am4core.percent(100);
        chart.legend.labels.template.fill = am4core.color("#9aa0ac");
        chart.legend.valueLabels.template.fill = am4core.color("#9aa0ac");
    }

    // Donut Chart Helpers
    async acsCreateDonutChart(container, innerRadiusPercent = 50) {
        am4core.useTheme(am4themes_animated);
        if (container.chart) {
            container.chart.dispose();
        }
        const chart = am4core.create(container, am4charts.PieChart);
        chart.logo.disabled = true;
        chart.innerRadius = am4core.percent(innerRadiusPercent);
        container.chart = chart;
        return chart;
    }

    async acsDonutChartSeries(chart, valueField, categoryField) {
        const pieSeries = chart.series.push(new am4charts.PieSeries());
        pieSeries.dataFields.value = valueField;
        pieSeries.dataFields.category = categoryField;
        pieSeries.slices.template.stroke = am4core.color("#fff");
        pieSeries.slices.template.strokeWidth = 2;
        pieSeries.slices.template.strokeOpacity = 1;
        pieSeries.labels.template.fill = am4core.color("#333");
        pieSeries.labels.template.fontSize = 16;
        pieSeries.labels.template.wrap = true;
        pieSeries.labels.template.truncate = false;
        pieSeries.labels.template.maxWidth = 140;
        pieSeries.hiddenState.properties.opacity = 1;
        pieSeries.hiddenState.properties.endAngle = -90;
        pieSeries.hiddenState.properties.startAngle = -90;
        return pieSeries;
    }
}