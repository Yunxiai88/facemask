$(document).ready(function () {

  // upload files
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

  $('.select').click(() => {
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

  $('#filterBtn').click(() => {
    if ($('li.selected').length > 0) {
      // form selected values
      var value = []
      $('li.selected').each(function() {
        var imname = $(this).find('img').attr("name");
        value.push(imname)
      });

      var doc = document.getElementById("imageForm");
      // form a input element
      var input = document.createElement('input')
      input.type = 'hidden'
      input.name = 'filterImages'
      input.value = value
      doc.appendChild(input)

      doc.submit();
    } else {
      alert("Please select at least one image to process.");
      return false
    }
  });

  $('#maskBtn').click(() => {
      var value = []
      $('li.mask').each(function() {
        var imname = $(this).find('img').attr("name");
        value.push(imname)
      });

      var doc = document.getElementById("maskForm");
      // form a input element
      var input = document.createElement('input')
      input.type = 'hidden'
      input.name = 'processedImages'
      input.value = value
      doc.appendChild(input)

      doc.submit();
  });

  $('#downloadBtn').click(() => {
    var value = []
    $('li.download').each(function() {
      var imname = $(this).find('img').attr("name");
      value.push(imname)
    });

    var doc = document.getElementById("downloadForm");
    // form a input element
    var input = document.createElement('input')
    input.type = 'hidden'
    input.name = 'selectedImages'
    input.value = value
    doc.appendChild(input)

    doc.submit();
});

  //image popup
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