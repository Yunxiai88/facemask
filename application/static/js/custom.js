$(document).ready(function () {
    $('#uploadForm').on('submit', function(event) {
        event.preventDefault();

        var fd = new FormData();
        var files = $('#sfile')[0].files;

        if(files.length > 0 ){
            $('.loader').show()
            fd.append('file',files[0])

            // disable button
            $('#closeBtn').prop('disabled', true)
            $('#submitBtn').prop('disabled', true)

            $.ajax({
                url: $(this).attr('action'),
                type: 'post',
                data: fd,
                contentType: false,
                processData: false,
                success: function(response) {
                    if(response != 0) {
                        $('.loader').hide()
                        $('#uploadModal').modal('hide');
                        
                        // enable button
                        $('#closeBtn').prop('disabled', false)
                        $('#submitBtn').prop('disabled', false)
                    }
                }
            }).fail(function(response) {
                $('.loader').hide()
                $('#uploadModal').modal('hide');
            });
        } else {
            alert("Please select a file.")
        }
    });

    //image pop up
    $(function() {
		$('.pop').on('click', function() {
			$('.imagepreview').attr('src', $(this).find('img').attr('src'));
			$('#imagemodal').modal('show');   
		});		
    });

});