$( document ).ready(function() {
    // Run initialization code
    init()

    function init() {
        $.ajax({
            url: '/api/statistics/photos',
            method: 'get',
            success: function(data) {
                setUpD3(data.results);
            }
        });
    }

    // This function maps data to graph
    function setUpD3(data) {
        // Convert dates in data
        for (var d in data) {
            data[d].date = new Date(Date.parse(data[d].date));
        }

        // Basic settings
        var margin = {top: 25, right: 50, bottom: 25, left: 50},
            width = $('#photo-stats-container').width() - margin.left - margin.right,
            height = 350 - margin.top - margin.bottom;

        // Set up scales
        var minDate = data[0].date,
            maxDate = data[data.length - 1].date

        var x = d3.scaleTime()
            .domain([minDate, maxDate])
            .range([0, width]);

        var y = d3.scaleLinear()
            .domain(d3.extent(data, function(d) { return d.average_photos_per_user }))
            .range([height, 0]);

        var line = d3.line()
            .curve(d3.curveMonotoneX)
            .x(function(d) { console.log('xxxxx', x(d.date)); return x(d.date); })
            .y(function(d) { return y(d.average_photos_per_user); });

        // Axes and graph setup
        // x is the d3.scaleTime()
        var xAxis = d3.axisBottom(x)
            .ticks(4);

        var yAxis = d3.axisLeft(y)
            .ticks(10);

        var svg = d3.select('#photo-stats-container')
            .append('svg')
            .attr('width', width + margin.left + margin.right)
            .attr('height', height + margin.top + margin.bottom)
            .append('g')
            .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

        svg.append('g')
            .attr('class', 'x axis')
            .attr('transform', 'translate(0,' + height + ')')
            .call(xAxis);

        svg.append('g')
            .attr('class', 'y axis')
            .call(yAxis);

        // Data binding
        var tooltip = d3.select('body')
            .append('div')
            .attr('class', 'tooltip');

        svg.selectAll('circle')
            .data(data)
            .enter().append('circle')
            .attr('cx', function(d) { return x(d.date); })
            .attr('cy', function(d) { return y(d.average_photos_per_user); })
            .attr('r', 5)
            .style('cursor', 'pointer')
            .on('mouseover', function(d) {
                var dateStringParts = d.date.toDateString().split(' '),
                    text = '<strong>' + dateStringParts[1] + ' ' + dateStringParts[3]
                        + '</strong><br>' + '<small><strong>AVG Photos/User:</strong> '
                        + d.average_photos_per_user + '</small>';

                tooltip.transition()
                    .duration(200)
                    .style('visibility', 'visible')
                    .style('left', (d3.event.pageX - 50) + 'px')
                    .style('top', (d3.event.pageY - 50) + 'px');

                tooltip.html(text);
            })
            .on('mouseout', function(d) {
                tooltip.transition()
                    .duration(500)
                    .style('visibility', 'hidden');
            })

        svg
            .append('path')
            .attr('fill', 'none')
            .attr('class', 'line')
            .attr('d', line(data))
            .style("stroke", '#6f7e95');
    }
});