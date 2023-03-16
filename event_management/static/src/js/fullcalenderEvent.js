

        document.addEventListener('DOMContentLoaded', function() {
            var calendarEl = document.getElementById('calendar');
            var currentDate = $('input#start_date').val();
            var venue = $('input#current_user_auditorium').val();
            console.log('currentDate');
            console.log(currentDate);
            console.log('venue');
            console.log(venue);
        if(currentDate != '' || currentDate != null){
            currentDate = new Date();
        }
          var calendar = new FullCalendar.Calendar(calendarEl, {
            eventClick: function(info) {
              var eventObj = info.event;
              if (eventObj.start) {
                alert(
                  'Start Time :-' + eventObj.startStr +  ' : ' + eventObj.extendedProps.startStr + '.\n' +
                  'End Time :-' + eventObj.endStr +  ' : '  + eventObj.extendedProps.endStr
                );
                info.jsEvent.preventDefault(); // prevents browser from following link in current tab.
              }
            },

            initialDate: currentDate,
            events: {
                url: '/ajax/reservations/get/' + venue,
                method: 'POST',
                color: '#5aaaff',
           },
          });

  calendar.render();
});

