$(document).ready(function () {
  // Phone mask.
  $('#phone').mask('(000) 000-0000');

  // Menu active toggle?
  $('.account_menu ul li').click(function () {
    $('.account_menu ul').find('li').removeClass('acc_menu_active');
    $(this).addClass("acc_menu_active");
    var modal_id = $(this).text();
    console.log(modal_id);
    $('.account_content').children().fadeOut(250);
    $('.account_content').find("div[id*='" + modal_id + "']").delay(250).fadeIn(250);
  });

  // Update Profile Ajax.
  $('#profile_save').click(function (e) {
    var first_name = $('#Profile').find('#fname').val();
    var last_name = $('#Profile').find('#lname').val();
    var phone_number = $('#Profile').find('#phone').val();
    console.log(first_name);
    console.log(user_id);
    console.log(profile_url);
    $.ajax({
      url: profile_url,
      method: "POST",
      data: JSON.stringify({ "first_name": first_name, "last_name": last_name, "phone_number": phone_number, "user_id": user_id }),
      dataType: "json",
      contentType: "application/json",
      error: function (jqXHR, textStatus, errorThrown) { console.log(jqXHR) },
    });
    location.reload();
    e.preventDefault();
  });

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
