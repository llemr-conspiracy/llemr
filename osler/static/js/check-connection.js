const workup_form = '.check-connection'
const alert_message = 'check VPN and internet connection'
$(workup_form).on('submit', function(event) {
  event.preventDefault()
  // "this" would be the {} object, so save the variable
  const form = this
  $.ajax({
    type:"GET",
    url: '/api/time',
    success: function() {
      // call submit on the DOM element, rather than the jquery selection
      // doing the latter triggers submit event handlers, and would be a recursive call 
      form.submit()
    },
    error: function() {
      alert(alert_message)
    },
  });
});
