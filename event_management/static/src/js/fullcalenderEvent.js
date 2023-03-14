

                     $('.login_btn').on('click', function(){
                        $('#RegistrationModal').modal('toggle')
                        $('#LoginModal').modal('toggle')
                    })

                    $('.register-btn').on('click', function(){
                        $('#LoginModal').modal('toggle')
                        $('#RegistrationModal').modal('toggle')
                      })


                    $('select#district_id').on('change', function(){
                        var val = $(this).val();
                    $('select#place_id > option').each(function(){
                        if($(this).data('distid') == val){
                            $(this).show()
                        }else{
                            $(this).hide()
                        }
                      $('select#place_id').val('').trigger('change')
                    })

                    })
                      $('select#place_id').on('change', function(){
                        var val = $(this).val();
                    $('select#venue_id > option').each(function(){
                        if($(this).data('place') == val){
                            $(this).show()
                        }else{
                            $(this).hide()
                        }
                    })
                      $('select#venue_id').val('').trigger('change')
                    })


                      $('input#date').on('change', function(){
                        var date = $(this).val();
                      console.log(date)
                        var venue = $('select#venue_id').val();
                        var eventsCount = $('#calendar table.fc-scrollgrid-sync-table .fc-day[data-date="'+date+'"] .fc-event').length

                        if(venue == null){
                            alert('Please select an Auditorium')
                            $('html,body').animate({
                                scrollTop: $('select#venue_id').offset().top
                            }, 500);
                        }else{
                             if(eventsCount > 0){
                                 alert('Event already exists for this date, Please choose another date.')
                                return false;
                             }
                        }
                    })


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
              console.log(eventObj)
              console.log("eventObj")
              console.log(eventObj.extendedProps)
              if (eventObj.url) {
                alert(
                  'Clicked ' + eventObj.title + '.\n' +
                  'Will open ' + eventObj.url + ' in a new tab'
                );
                info.jsEvent.preventDefault(); // prevents browser from following link in current tab.
              } else {
                alert('Clicked ' + eventObj.title);
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

