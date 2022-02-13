$(document).ready(function () {
  $('#uploadForm').on('submit', function (event) {
    event.preventDefault();

    var fd = new FormData();
    var files = $('#sfile')[0].files;

    if (files.length > 0) {
      $('.loader').show()
      fd.append('file', files[0])

      // disable button
      $('#closeBtn').prop('disabled', true)
      $('#submitBtn').prop('disabled', true)

      $.ajax({
        url: $(this).attr('action'),
        type: 'post',
        data: fd,
        contentType: false,
        processData: false,
        success: function (response) {
          if (response != 0) {
            $('.loader').hide()
            $('#uploadModal').modal('hide');

            // enable button
            $('#closeBtn').prop('disabled', false)
            $('#submitBtn').prop('disabled', false)
          }
        }
      }).fail(function (response) {
        $('.loader').hide()
        $('#uploadModal').modal('hide');
      });
    } else {
      alert("Please select a file.")
    }
  });

  $('li').click(function () {
    $(this).toggleClass('selected');
    if ($('li.selected').length == 0)
      $('.select').removeClass('selected');
    else
      $('.select').addClass('selected');
    counter();
  });

  $('.select').click(function () {
    if ($('li.selected').length == 0) {
      $('li').addClass('selected');
      $('.select').addClass('selected');
    }
    else {
      $('li').removeClass('selected');
      $('.select').removeClass('selected');
    }
    counter();
  });

  //image pop up
  $('.pop').on('click', function () {
    $('.imagepreview').attr('src', $(this).find('img').attr('src'));
    $('#imagemodal').modal('show');
  });

});

function counter() {
  if ($('li.selected').length > 0)
    $('.send').addClass('selected');
  else
    $('.send').removeClass('selected');
  $('.send').attr('data-counter', $('li.selected').length);
}