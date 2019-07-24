function updateFormImage() {
  // Set form file input to data url of canvas.
  $("#loop_image")[0].value = $("#loop_preview")[0].src;
}


function image_creator() {
  /*
    Image factory function. Will turn the current playlist into
    a meshed together image using 1-4 playlist items.
  */

  // Variable declaration.
  var thumbnails = [];
  var canvas = $("#loop_canvas");
  var img = $("#loop_preview");

  // Static dimensions for image modes 1-4
  var image_dimension_modes = {
    1: {
      0: [0, 0, 540, 405]
    },
    2: {
      0: [0, 0, 270, 205.5],
      1: [270, 205.5, 270, 205.5],
    },
    3: {
      0: [0, 0, 270, 205.5],
      1: [270, 0, 260, 205.5],
      2: [135, 205.5, 270, 205.5],
    },
    4: {
      0: [0, 0, 270, 205.5],
      1: [260, 0, 260, 205.5],
      2: [0, 205.5, 270, 205.5],
      3: [270, 205.5, 270, 205.5],
    },
  }

  // Canvas 2d context.
  var context = canvas.get(0).getContext("2d");

  // Spawn clear rectangle context for canvas image.
  context.clearRect(0, 0, 540, 405)

  // Populate thumbnails from playlist.
  $('#playlist').find('img').each(function () {
    thumbnails.push($(this).attr("src"));
  });

  // Set image mode from number of thumbnails (maxing at 4).
  var image_mode = thumbnails.slice(0, 4).length;

  // If not image mode 4, add blank background.
  if (image_mode != 4) {
    context.fillStyle = "#232323";
    context.fillRect(0, 0, 540, 405)
  }

  // Iterate each thumbnail and add them to the canvas.
  thumbnails.slice(0, 4).forEach((item, index) => {

    // Create new image, set crossorigin and src.
    var image = new Image();
    image.crossOrigin = "";
    image.src = item;

    // Get current image dimensions based off index and image mode.
    var img_dimensions = image_dimension_modes[image_mode][index]

    // Add onload function which draws the image to canvas, and updates the preview image to the new canvas image.
    image.onload = function () {

      // Draw image to canvas.
      context.drawImage(image, img_dimensions[0], img_dimensions[1], img_dimensions[2], img_dimensions[3])

      // Update preview image.
      img.attr('src', canvas[0].toDataURL("image/png"));
      updateFormImage()
    }
  })
}


$(document).ready(function () {

  $(".content_channel").click(function () {
    $(document).find(".channel").hide()
    $t = $(this);
    var channel_id = $(this).find(".content_id").text();
    $.ajax({
      url: post_url,
      method: "POST",
      data: JSON.stringify({ "channel_id": channel_id }),
      dataType: "json",
      contentType: "application/json",
      success: function (resp) {
        $t.parent().parent().parent().parent().after(
          resp.data
        )
      },
      error: function (errMsg) { alert("Error find channel: " + errMsg) },
    })
  });

  $('body').click(function (event) {
    $('.modal').removeClass('is-visible');
  });

  $('#promo_cancel').click(function (event) {
    $(document).find('.modal').removeClass('is-visible');
    $(document).find('#promo_file').val('');
    $(document).find('#name').val('');
    $(document).find('#description').val('');
  });

  $(".add_promo").click(function (e) {
    e.preventDefault();
    e.stopPropagation();
    $('.modal').toggleClass('is-visible');
  });

  $(".modal-wrapper").click(function (e) {
    e.stopPropagation();
  });

  var array = [];
  $('#save_button').on('click', function () {
    $('#playlist').has('li').each(function () {
      var loop_type = $(this).find('h5').map(function () {
        return $(this).text();
      })
      var loop_id = $(this).find('span').map(function () {
        return $(this).text();
      });
      for (var i = 0; i < loop_id.length && i < loop_type.length; i++)
        array[i] = loop_type[i] + loop_id[i];
    });
    console.log(array);
    var loopname = $("#title_value").val();
    var image_url = $("#loop_preview").attr("src");
    console.log(loopname);
    if (loopname.length < 1 || $('#playlist').children().length < 1) {
      if (loopname.length < 1) {
        alert("Please Give your Loop a Title.");
      } else {
        alert("Please Add Shows and Promos to your Loop.");
      }
    } else {
      $.ajax({
        url: save_url,
        method: "POST",
        data: JSON.stringify({ "name": loopname, "playlist": array, "image_data": image_url, "user_id": user_id }),
        dataType: "json",
        contentType: "application/json",
        // headers: {
        //   "Access-Control-Allow-Origin": "*",
        //   "Access-Control-Allow-Methods": "*",
        //   "Access-Control-Allow-Headers": "*"
        // },
        success: function (data) { alert("Sumbited " + loopname + " successfully.") },
        error: function (errMsg) { alert("Sorry: " + errMsg) },
      });
    }
  });
});

$(document).delegate(".show_item", 'click', function () {
  $("show_item").hide();
  if ($(this).find(".show_info").is(':visible')) {
    $(this).find(".show_info").hide();
  } else {
    $(this).find(".show_info").show();
  }
});

$(document).delegate(".show_clip", 'click', function (e) {
  e.stopPropagation();
});

$(document).delegate(".playlist_add", 'click', function (e) {
  e.stopPropagation();
});

$(document).delegate(".playlist_add", 'click', function () {
  $e = $(this)

  // Get existings loops from form.
  var loop_data_element = $("#loop_data")[0]
  
  // Get value as object.
  var loop_data = []
  if (loop_data_element.value) {
    var loop_data = JSON.parse(loop_data_element.value)["data"];

  }

  var ul = $(".playlist_list ul");
  if ($(this).find("div.promo_id").length) {
    var loopItem_id = $(this).find(".promo_id").text();
    var loopItem_type = "Promo";
    var loopItem_img = $(this).find(".content_img img").attr('src');
    var loopItem_name = $(this).find(".content_title span").text();
  } else {
    var loopItem_id = $(this).parent().find(".show_id").text();
    var loopItem_type = "Show";
    var loopItem_img = $(this).parent().find(".clip_container video").attr('poster');
    var loopItem_name = $(this).parent().find(".show_name").text();
  }

  // Add new loop item to playlist.
  loop_data.push(loopItem_type + "_" + loopItem_id);
  
  // Set value on form input element.
  loop_data_element.value = JSON.stringify({"data": loop_data})
  
  var playlist_item = '<li><div><img src="' + loopItem_img + '"/></div><div><span>' + loopItem_id + '</span><h4>' + loopItem_name + '</h4><h5>' + loopItem_type + '</h5></div></li>';
  ul.append(playlist_item);
  image_creator();
});

$(document).on('click', '.playlist_list ul li', function () {
  $(this).remove();
  image_creator();
});

/* Promo Video Preview */

$(function () {
  var video = $(".promo_video");
  var thumbnail = $("#promo_canvas");
  var input = $("#promo_file");
  var ctx = thumbnail.get(0).getContext("2d");
  var duration = 0;
  var img = $("#promo_preview");

  input.on("change", function (e) {
    $(document).find('.promo_img').removeClass('after_overlay');
    var file = e.target.files[0];
    // Validate video file type
    if (["video/mp4"].indexOf(file.type) === -1) {
      alert("Only 'MP4' video format allowed.");
      return;
    }
    // Set video source
    video.find("source").attr("src", URL.createObjectURL(file));
    // Load the video
    video.get(0).load();
    // Load metadata of the video to get video duration and dimensions
    video.on("loadedmetadata", function (e) {
      duration = video.get(0).duration;
      // Set canvas dimensions same as video dimensions
      thumbnail[0].width = 512;
      thumbnail[0].height = 288;
      // Set video current time to get some random image
      video[0].currentTime = 5;
      // Draw the base-64 encoded image data when the time updates
      video.one("timeupdate", function () {
        ctx.drawImage(video[0], 0, 0, 512, 288);
        img.attr("src", thumbnail[0].toDataURL());
      });
    });
  });
});
