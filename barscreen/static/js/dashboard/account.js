function update_profile(event) {
  console.log(event);
}


$(document).ready(function () {
  // Phone mask.
  $('#phone').mask('(000) 000-0000');

  // Set existing values for account.
  $("#phone_number")[0].value = _phone_number;
  $("#first_name")[0].value = _first_name;
  $("#last_name")[0].value = _last_name;
  $("#email")[0].value = _email;  

  // Menu active toggle?
  $('.account_menu ul li').click(function () {
    $('.account_menu ul').find('li').removeClass('acc_menu_active');
    $(this).addClass("acc_menu_active");
    
    // Hide all divs.
    $("#Profile").hide()
    $("#Login").hide()
    $("#Billing").hide()

    // Get clicked modal id and show it.
    var modal_id = $(this).text();
    $("#Update").show()
    $('.account_content').find("div[id*='" + modal_id + "']").show()
  });

  // // Update Profile Ajax.
  // $('#profile_save').click(function (e) {
  //   e.preventDefault();
  //   var first_name = $('#Profile').find('#fname').val();
  //   var last_name = $('#Profile').find('#lname').val();
  //   var phone_number = $('#Profile').find('#phone').val();
  //   console.log(first_name);
  //   console.log(user_id);
  //   console.log(profile_url);
  //   $.ajax({
  //     url: profile_url,
  //     method: "POST",
  //     data: JSON.stringify({ "first_name": first_name, "last_name": last_name, "phone_number": phone_number, "user_id": user_id }),
  //     dataType: "json",
  //     contentType: "application/json",
  //     error: function (jqXHR, textStatus, errorThrown) { console.log(jqXHR) },
  //     success: function(data){ console.log(data)},
  //   });
  //   location.reload();
    
  // });

  // Update Email Ajax.
  $('#email_save').click(function (e) {
    var email = $('#Login').find('#email').val();
    $.ajax({
      url: email_url,
      method: "POST",
      data: JSON.stringify({ "email": email, "user_id": user_id }),
      dataType: "json",
      contentType: "application/json",
      success: location.reload(),
      error: function (errMsg) { alert("Sorry: " + errMsg) },
    });
    location.reload();
    e.preventDefault();
  });

  // Reset password link.
  $('#password_save').click(function (e) {
    var email = $('#Login').find('#email').val();
    $('#Login').find('p').hide()
    var success_message = $('<p>An email has been sent with a link to reset your password</p>')
    $.ajax({
      url: password_url,
      method: "POST",
      data: JSON.stringify({ "email": email }),
      dataType: "json",
      contentType: "application/json",
      success: success_message.hide().appendTo('#Login').fadeIn(),
      error: function (errMsg) { alert("Sorry: " + errMsg) },
    });
    e.preventDefault();
  });

});
