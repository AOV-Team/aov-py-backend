/**
 * Created by gallen on 6/6/18.
 */

$( document ).ready(function() {
    // Run initialization code
    init();

    function init() {
        setUpDateRangeSelect();
        // $.ajax({
        //     url: '/api/statistics/photos',
        //     method: 'get',
        //     success: function() {
        //
        //     }
        // });
    }

    // Reference: https://stackoverflow.com/a/21903119/1597697
    var getUrlParameter = function getUrlParameter(sParam) {
        var sPageURL = decodeURIComponent(window.location.search.substring(1)),
            sURLVariables = sPageURL.split('&'),
            sParameterName,
            i;

        for (i = 0; i < sURLVariables.length; i++) {
            sParameterName = sURLVariables[i].split('=');

            if (sParameterName[0] === sParam) {
                return sParameterName[1] === undefined ? true : sParameterName[1];
            }
        }
    };

    function setUpDateRangeSelect() {
        $('input[name="date-picker"]').daterangepicker({
            alwaysShowCalendars: true,
            opens: 'right',
            autoUpdateInput: false,
            locale: {
                cancelLabel: 'Clear'
            },
            linkedCalendars: true,
            minYear: 2014,
            maxYear: 2050,
            maxSpan: {
                "days": 30
            },
            showCustomRangeLabel: false
        }, function(start, end) {
            // data = {
            //     date: start.format('YYYY-MM-DD') + " - " + end.format('YYYY-MM-DD')
            // };
            var page = getUrlParameter("page");
            if (page === undefined) {
                data = {
                    date: start.format('YYYY-MM-DD') + " - " + end.format('YYYY-MM-DD')
                };
            } else {
                data = {
                    page: page,
                    date: start.format('YYYY-MM-DD') + " - " + end.format('YYYY-MM-DD')
                };
            }

            $.ajax({
                url: "/admin/power_users",
                method: "get",
                data: data
            });
        });
    }

    // function setUpCalendar() {
    //     const picker = datepicker(document.querySelector('#date-picker'), {
    //       position: 'tr', // Top right.
    //       startDate: new Date(), // This month.
    //       startDay: 1, // Calendar week starts on a Monday.
    //       dateSelected: new Date(), // Today is selected.
    //       disabledDates: [new Date('1/1/2050'), new Date('1/3/2050')], // Disabled dates.
    //       minDate: new Date(2014, 0, 1), // Jan 1st, 2014.
    //       maxDate: new Date(2099, 0, 1), // Jan 1st, 2099.
    //       noWeekends: false, // Weekends will be unselectable.
    //       formatter: function(el, date) {
    //         // This will display the date as `1/1/2017`.
    //         el.value = date.toDateString();
    //       },
    //       onSelect: function(instance) {
    //         // Show which date was selected.
    //         console.log(instance.dateSelected);
    //       },
    //       onShow: function(instance) {
    //         console.log('Calendar showing.');
    //       },
    //       onHide: function(instance) {
    //         console.log('Calendar hidden.');
    //       },
    //       onMonthChange: function(instance) {
    //         // Show the month of the selected date.
    //         console.log(instance.currentMonthName);
    //       },
    //       customMonths: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
    //       customDays: ['S', 'M', 'T', 'W', 'Th', 'F', 'S'],
    //       overlayPlaceholder: 'Enter a 4-digit year',
    //       overlayButton: 'Select',
    //       disableMobile: true // Conditionally disabled on mobile devices.
    //     });
    // }
});
