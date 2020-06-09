const checkConnectionClass = 'check-connection'
const checkConnectionUrl= '/workup/check-connection'
const alertMessage = 'Check VPN and internet connection.'

/**
 * Checks that server connection is stable before redirecting in order to 
 * prevent losing form data.
 * 
 * To implement a connection check for a form, ensure the following:
 * 
 * - the template contains this script
 * - the relevant form is of class 'check-connection'
 * - the name argument to the Crispy Forms Submit class is not 'submit',
 *   i.e., self.helper.add_input(Submit('submit', 'Submit')) should instead be
 *   self.helper.add_input(Submit('submit-button', 'Submit'))
 */
function addConnectionCheck() {
  $('.' + checkConnectionClass).submit(function(event) {
    event.preventDefault()
    const form = this
    $.ajax({
      url: checkConnectionUrl,
      success: function() {
        // call submit on the DOM element, rather than the jquery selection
        form.submit()
      },
      error: function() {
        alert(alertMessage)
      },
    });
  });
}

addConnectionCheck()
