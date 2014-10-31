$(function()
{
	$("#UpdatePreview").click(function(event)
	{
		event.preventDefault();
		var markdown = $("#"+$(event.currentTarget).attr("from")).val();
		var target = $("#"+$(event.currentTarget).attr("to"));

		$.ajax({
		    data: markdown,
		    type: "POST",
		    url: "/markdown",
		    success: function (data, status) {
		    	target.html(data);
		    }
		});
	});
})