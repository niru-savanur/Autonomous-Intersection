var ContinuousVisualization = function(height, width, context) {
	var height = height;
	var width = width;
	var context = context;

	this.draw = function(objects) {
		objects.sort((a, b) => {return a.Layer - b.Layer});
		console.log(objects)
		for (var i in objects) {
			var p = objects[i];
			if (p.Shape === "simplerect")
				this.drawSimpleRectangle(p.x, p.y, p.w, p.h, p.Color, p.Filled, p.rotation);
			if (p.Shape === "rect")
				this.drawRectangle(p.x, p.y, p.w, p.h, p.Color, p.Filled, p.rotation);
			if (p.Shape === "circle")
				this.drawCircle(p.x, p.y, p.r, p.Color, p.Filled);
		};

	};

	this.drawCircle = function(x, y, radius, color, fill) {
		var cx = x * width;
		var cy = y * height;
		var r = radius;

		context.beginPath();
		context.arc(cx, cy, r, 0, Math.PI * 2, false);
		context.closePath();

		context.strokeStyle = color;
		context.stroke();

		if (fill) {
			context.fillStyle = color;
			context.fill();
		}

	};
	this.drawSimpleRectangle = function(x, y, w, h, color, fill) {
		context.beginPath();

		context.strokeStyle = color;
		context.fillStyle = color;
		if (fill)
			context.fillRect(x, y, w, h);
		else
			context.strokeRect(x, y, w, h);
	};

	this.resetCanvas = function() {
		context.clearRect(0, 0, height, width);
		context.beginPath();
	}
	this.drawRectangle = function(x, y, w, h, color, fill, rotation) {
		context.beginPath();

		context.strokeStyle = color;
		context.fillStyle = color;
		context.translate(x, y);
		context.rotate(rotation);
		if (fill)
			context.fillRect(-w/2, -h/2, w, h);
		else
			context.strokeRect(-w/2, -h/2, w, h);
		context.rotate(-rotation);
		context.translate(-x, -y);
	};

	this.resetCanvas = function() {
		context.clearRect(0, 0, height, width);
		context.beginPath();
	};
};

var Simple_Continuous_Module = function(canvas_width, canvas_height) {
	// Create the element
	// ------------------

	// Create the tag:
	var canvas_tag = "<canvas width='" + canvas_width + "' height='" + canvas_height + "' ";
	canvas_tag += "style='border:1px dotted'></canvas>";
	// Append it to body:
	var canvas = $(canvas_tag)[0];
	$("#elements").append(canvas);

	// Create the context and the drawing controller:
	var context = canvas.getContext("2d");
	var canvasDraw = new ContinuousVisualization(canvas_width, canvas_height, context);

	this.render = function(data) {
		canvasDraw.resetCanvas();
		canvasDraw.draw(data);
	};

	this.reset = function() {
		canvasDraw.resetCanvas();
	};

};
