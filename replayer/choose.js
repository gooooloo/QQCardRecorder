function doChoose(cb)
{
	options = {
		success: function(files) {
				 //alert("Here's the file link: " + files[0].link)
				 var txtFile = new XMLHttpRequest();
				 txtFile.open("GET", files[0].link, true);
				 txtFile.onreadystatechange = function() {
					 if (txtFile.readyState === 4) {  // Makes sure the document is ready to parse.
						 if (txtFile.status === 200) {  // Makes sure it's found the file.
							 allText = txtFile.responseText; 
							 cb(allText);
						 }
					 }
				 }
				 txtFile.send(null);

			 },

		cancel: function() { },
		linkType: "direct", // or "direct"
		multiselect: false, // or true
		extensions: ['.txt'],
	};

	Dropbox.choose(options);
};
