

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


                      function renderCalendar() {
                            var currentDate = $('input#start_date').val();
                            console.log(currentDate);
                        if(currentDate != '' || currentDate != null){
                            currentDate = new Date();
                        }
                            var venue_id = $('#venue_id').val();
                            var token = $('[name="csrf_token"]').val();
                            var calendarEl = document.getElementById('calendar');
                            var calendar = new FullCalendar.Calendar(calendarEl, {
                            selectable: true,
                            initialView: 'dayGridMonth',
                            initialDate: currentDate,
                      eventClick: function(calEvent, jsEvent, view) {
console.log(calEvent);
  },
                            events: {
                                url: '/ajax/reservations/get/' + venue_id,
                                method: 'POST',
                    <!--			extraParams: {-->
                    <!--				csrf_token: "<t t-esc="request.csrf_token(None)"/>",-->
                    <!--: token,-->
                    <!--			},-->
                    <!--			failure: function () {-->
                    <!--&lt;!&ndash;				toastr.error(&ndash;&gt;-->
                    <!--&lt;!&ndash;					'There was an error while fetching events!',&ndash;&gt;-->
                    <!--&lt;!&ndash;					'Error!',&ndash;&gt;-->
                    <!--&lt;!&ndash;					{&ndash;&gt;-->
                    <!--&lt;!&ndash;						timeOut: 2000,&ndash;&gt;-->
                    <!--&lt;!&ndash;						fadeOut: 2000,&ndash;&gt;-->
                    <!--&lt;!&ndash;					}&ndash;&gt;-->
                    <!--				);-->
                    <!--			},-->
                                color: '#5aaaff',
                                textColor: 'black',
                            },


<!--                            dateClick: function(info) {-->
<!--                              alert(info.dayEl.innerText);-->
<!--                      var text = info.dayEl.innerText;-->
<!--                      event_id = text.split("/");-->
<!--                        alert(event_id[1]);-->
<!--                      event = calendar.getEventById('event_id[1]')-->
<!--                      console.log(event);-->
<!--                            },-->
<!--                      var currentDate = $('input#date').val();-->
<!--                      $('#calendar').fullCalendar('gotoDate', currentDate);-->
<!--                                            console.log(currentDate)-->
                            });
                            calendar.render();
                    };


                      $('select#venue_id').on('change', function(){
                        var price = $(this).find('option:selected').data('price');
                        var venue =  $('select#venue_id').val();
//                        if(price != '' || price != null){
//                            $('input#auditorium_price').val(price).trigger('change')
//                        }
                        if(venue != '' || venue != null){
                              renderCalendar()
                      }
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