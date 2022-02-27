$(document).ready(function () {

  $('#files').fileinput({
    uploadUrl: '/admin/upload',
    theme : 'explorer-fas',
    uploadAsync: false,
    showRemove :true,
    showPreview: true,
    showCancel:true,
    showCaption: true,
    minFileCount: 1,
    validateInitialCount: true,
    allowedFileExtensions: ['jpg', 'png'],
    browseClass: "btn btn-primary ",
    dropZoneEnabled: true,
    dropZoneTitle: 'Drag file here！',
  });

  $('#faceFile').fileinput({
      uploadUrl: '/uploadFace',
      theme : 'explorer-fas',
      uploadAsync: false,
      showRemove :true,
      showPreview: true,
      showCancel:true,
      showCaption: true,
      maxFileCount: 2,
      minFileCount: 1,
      validateInitialCount: true,
      allowedFileExtensions: ['jpg', 'png'],
      browseClass: "btn btn-primary ",
      dropZoneEnabled: true,
      dropZoneTitle: 'Drag file here！',
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

  $('#processBtn').click(() => {
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
      input.name = 'faceImages'
      input.value = value
      doc.appendChild(input)

      doc.submit();
    } else {
      alert("Please select at least one image to process.");
      return false
    }
  });

  $('#deleteBtn').click(() => {
    if ($('li.selected').length > 0) {
      var value = []
      $('li.selected').each(function() {
        var imname = $(this).find('img').attr("name");
        value.push(imname)
      });

      var doc = document.getElementById("deleteForm");
      // form a input element
      var input = document.createElement('input')
      input.type = 'hidden'
      input.name = 'deleteImages'
      input.value = value
      doc.appendChild(input)

      doc.submit();
    } else {
      alert("Please select at least one image to process.");
      return false
    }
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

});

function counter() {
  if ($('li.selected').length > 0)
    $('.send').addClass('selected');
  else
    $('.send').removeClass('selected');
  $('.send').attr('data-counter', $('li.selected').length);
}