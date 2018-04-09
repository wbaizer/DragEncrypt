/*
 *	DragEncrypt
 *
 *	Uploader.js
 *	Set up and customize the drag and drop div
 */

function generatePassword() {
	// Generate a random number for length, ranging from 17 to 22
	var length = 17 + (Math.random() * 5);

	chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()[];:?<>';
	var password = '';
    for (var i = length; i > 0; --i) {
    	password += chars[Math.floor(Math.random() * chars.length)];
    }
    
    return password;
}

$(document).ready(function() {
	// Set up Drag and Drop
	var de_dropzone = new Dropzone(".file-drag-wrapper", {
		url: "/encrypt",
		type: "post",
		autoProcessQueue: false, // Disable auto upload after selecting file
		addedfile: function(file) { 
			// Hide drag and drop instructions on upload
			$(".file-drag-instructions").hide(); 

			// Shorten filename if too long
			filename = file.name;
			if (filename.length > 35) {
				filename = filename.substring(0, 35) + "...";
			}

			var ext = file.name.substr(file.name.lastIndexOf('.') + 1);
			//TODO Error handling for extension

			// Switch to decryption if file extension is ".encrypted"
			if (ext == "encrypted") {
				$(".file-encrypt-button").html("Decrypt");
				$(".encryption-password-text-label").html("Please enter the password to decrypt this file");
				de_dropzone.options.url = "/decrypt"
			} else {
				$(".encryption-password-text").attr("value", generatePassword());
			}


			// Display filename and restyle box
			$(".file-drag-success").text(filename);
			$(".file-drag-success").show();
			$(".file-drag-wrapper").removeClass("file-drag-wrapper").addClass("file-drag-wrapper-success");
			$(".content-subheader").slideUp("fast");
			$(".drag-encrypt-step2").slideDown("fast");
		},
		success: function(file, response){
			filename = response.filename;

			// Remember encryption key message
			var ext = filename.substr(filename.lastIndexOf('.') + 1);
			if (ext == "encrypted") {
				$(".remember-key").show();
				$(".encryption-password-text-confirm").css("display", "block");
				var passkey = $(".encryption-password-text").val();
				$(".encryption-password-text-confirm").val(passkey);
			}

			$(".drag-encrypt-step3").slideDown("fast");
			$(".drag-encrypt-inprogress").slideUp("fast");
			$(".file-download-link").attr("href", filename);
		},
		sending: function(file, xhr, formData) {
		    formData.append("key", $(".encryption-password-text").val());
		}
	});

	// Send files on button click
	$(".file-encrypt-button").on("click", function(e){
		e.preventDefault();
		de_dropzone.processQueue();	
		$(".drag-encrypt-step2").slideUp("fast");
		$(".drag-encrypt-inprogress").slideDown("fast");
	});
});

