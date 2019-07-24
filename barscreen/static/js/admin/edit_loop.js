function updatePlaylistData() {
  /*
    Iterates all existing items in loop playlist and adds them to loop_data.
  */
  // Get existings loops from form.
  var loop_data_element = $("#loop_data")[0];
  
  // Create loop data array.
  var loop_data = [];

  // Iterate each tr.
  $("#loop_content tr").each(function () {
    // Select current li.
    var li = $(this);

    // Get the item id and type.
    loop_item_id = li.find("#li_id")[0].textContent;
    loop_item_type = li.find("#li_type")[0].textContent;

    // Add loop item to playlist.
    loop_data.push(loop_item_type + "_" + loop_item_id);

    // Set value on form input element.
    loop_data_element.value = JSON.stringify({ "data": loop_data })
  });
}

$(document).ready(function() {

    $.each(loop_playlist, function(index, value) {
      var load_item = $("<tr></tr>").append("<td>" + value.name + "</td><td id='li_type'>" + value.type + "</td><td id='li_id'>" + value.id + "</td>")
      $("#loop_content").append(load_item);
    });
    updatePlaylistData();
    //   var array = [];
    //   $(".edit_container").on('click', 'button', function () {
    //     $('#loop_content').has('tr').each(function () {
    //       var loop_type = $('#loop_content td:nth-child(2)').map(function () {
    //         return $(this).text();
    //       })
    //       var loop_id = $('#loop_content td:nth-child(3)').map(function () {
    //         return $(this).text();
    //       });
    //       for (var i = 0; i < loop_id.length && i < loop_type.length; i++)
    //         array[i] = loop_type[i] + loop_id[i];
    //       console.log(array);
    //     });
    //     var loopname = $("#loop_name").val();
    //     var image_data = $("#loop_img_data")[0].innerText
    //     console.log(array);
    //     console.log("success");
    //     console.log(loopname);
    //     $.ajax({
    //       url: post_url,
    //       method: "PUT",
    //       data: JSON.stringify({
    //         "name": loopname,
    //         "loop_id": loop_id,
    //         "playlist": array,
    //         "user_id": user_id,
    //         "image_data": image_data,
    //       }),
    //       dataType: "json",
    //       contentType: "application/json",
    //       success: function (data) { alert("Sumbited " + loopname + " successfully.") },
    //       error: function (errMsg) { alert("Sorry: " + errMsg) },
    //   });
    // });
  });
  