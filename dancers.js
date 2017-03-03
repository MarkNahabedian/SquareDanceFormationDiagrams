


var svg_uri = "http://www.w3.org/2000/svg";
var xlink_uri = "http://www.w3.org/1999/xlink";

/*

  A note about coordinate systems:

  The coordinates used for dancer placement (small integers typically
  from 1 to 8) that are used as the x and y parameters of the Dancer
  constructor are a convenience for describing formations.

  The floor svg coordinate system is used for describing placement and
  drawing of each dancer in the svg element.  It is typically some
  constant factor scale up from the placement coordinates, with some
  translation.

  Some additional scaling is applied to the floor svg coordinate
  system to make all of the dancers fit into the available screen real
  estate.

   */

function Floor(dancers) {
  // This particular floor
  this.dancers = dancers;
  // Some defsault drawing parameters:
  this.dancer_size = 20;
  // spacing between centers, not perimeters
  this.dancer_spacing = this.dancer_size * 1.3;
  this.dancer_nose_radius = 3;
  // how much of the dancer outline is rounded for the non-gendered dancer
  this.neu_corner_fraction = 0.3;
  // Tell the dancers what floor they're on.
  var floor = this;
  console.log("dancers " + this.dancers);
  this.dancers.map(function(d) { d.floor = floor; });
};

Floor.prototype.draw = function(svg_id) {
  // Setting up for drawing:
  var xs = this.dancers.map(function(d) { return d.x; });
  var ys = this.dancers.map(function(d) { return d.y; });
  var min_x = Math.min.apply(null, xs);
  var max_x = Math.max.apply(null, xs);
  var min_y = Math.min.apply(null, ys);
  var max_y = Math.max.apply(null, ys);
  var svg_element = document.getElementById(svg_id);
  if (!svg_element) {
    console.log("No svg element with id " + svg_id);
    return;
  }
  // Add one to provide half a dancer of space at each border.
  var dancers_wide = 1 + max_x - min_x;
  var dancers_high = 1 + max_y - min_y;
  // Does the svg element already have dimensions?
  console.log("For Floor " + svg_id + " the ideal aspect ratio (width/height) is " +
	      dancers_wide / dancers_high);
  var width = svg_element.clientWidth;
  var height = svg_element.clientHeight;
  console.log("svg size: " + width + " x " + height);
  var available = Math.min(width / dancers_wide, height / dancers_high);
  console.log("space available for a dancer: " + available);

  var put_dancers_here = document.createElementNS(svg_uri, "g");
  var translate = "translate("
  	+ (width / 2 - dancers_wide * this.dancer_spacing / 2) + ", "
  	+ (height / 2 - dancers_high * this.dancer_spacing / 2) + ")";
  put_dancers_here.setAttribute("transform", translate);
  svg_element.appendChild(put_dancers_here);
  this.dancers.map(function(d) {
      put_dancers_here.appendChild(d.svg(svg_id));
  });
  return this;
};

Floor.prototype.getDancer = function(label) {
  if (label instanceof Dancer) return label;
  for (var i = 0; i < this.dancers.length; i++) {
    var dancer = this.dancers[i];
    if (dancer.label == label) return dancer;
  }
  return null;
};

// Makes a Dancer.  x and y are floor positions, typically numbers from 1 to 8.
function Dancer(x, y, direction, label, gender, color) {
  this.x = x;
  this.y = y;
  this.direction = direction;
  this.label = label || "";
  this.gender = gender || Dancer.gender.NEU;
  this.color = color || "white";
  this.floor = null;
};

Dancer.gender = {
    GUY: "guy",
    GAL: "gal",
    NEU: "unspecified"
};

// Builds an svg:g element for a Dancer and returns it.  It's up to the
// caller to add it to the DOM tree.
Dancer.prototype.svg = function(floor_svg_id) {
  var g = document.createElementNS(svg_uri, "g");
  var dancer_id = floor_svg_id + ":" + this.label;
  g.setAttribute("ID", this.dancer_id);
  var rotate = "rotate(" + (180 - this.direction * 90) + ")";
  var translate = "translate("
  	+ (this.x * this.floor.dancer_spacing) + ", "
  	+ (this.y * this.floor.dancer_spacing) + ")";
  var xform = translate + " " + rotate;
  g.setAttribute("transform", xform);
  var dancer_shape;
  switch (this.gender) {
    case Dancer.gender.GUY:
      dancer_shape = dancer_guy(this);
      break;
    case Dancer.gender.GAL:
      dancer_shape = dancer_gal(this);
      break;
    default:
      dancer_shape = dancer_neu(this);
  }
  dancer_shape.setAttribute("fill", this.color);
  dancer_shape.setAttribute("stroke", "black");
  g.appendChild(dancer_shape);
  g.appendChild(nose(this));

  var label = document.createElementNS(svg_uri, "text");
  label.setAttribute("text-anchor", "middle");
  label.setAttribute("alignment-baseline", "middle");
  label.appendChild(document.createTextNode(this.label));
  g.appendChild(label);

  return g;
};

function nose(dancer) {
    var nose = document.createElementNS(svg_uri, "circle");
    nose.setAttribute("r", "" + dancer.floor.dancer_nose_radius);
    nose.setAttribute("cx", "0");
    nose.setAttribute("cy", "" + (- (dancer.floor.dancer_size / 2)));
    nose.setAttribute("stroke", "none");
    nose.setAttribute("fill", "black");
    return nose;
}

// Returns a not yet positioned SVG group element to be added to some parent element
function dancer_guy (dancer) {
    var shape = document.createElementNS(svg_uri, "rect");
    shape.setAttribute("width", "" + dancer.floor.dancer_size);
    shape.setAttribute("height", "" + dancer.floor.dancer_size);
    shape.setAttribute("x", "" + (- (dancer.floor.dancer_size / 2)));
    shape.setAttribute("y", "" + (- (dancer.floor.dancer_size / 2)));
    return shape;
}

// Returns a not yet positioned SVG group element to be added to some parent element
function dancer_gal (dancer) {
    var shape = document.createElementNS(svg_uri, "circle");
    shape.setAttribute("r", "" + (dancer.floor.dancer_size / 2));
    shape.setAttribute("cx", "0");
    shape.setAttribute("cy", "0");
    return shape;
}

// Returns a not yet positioned SVG group element to be added to some parent element
function dancer_neu (dancer) {
    var shape = document.createElementNS(svg_uri, "path");
    // Identify the X and Y coordinates of the line and arc ends
    var r = dancer.floor.neu_corner_fraction * dancer.floor.dancer_size;
    var right = dancer.floor.dancer_size / 2;
    var bottom = dancer.floor.dancer_size / 2;
    var left = - dancer.floor.dancer_size / 2;
    var top = - dancer.floor.dancer_size / 2;
    var path = [
	//  top left corner
	"M", left, top + r,
	"A", r, r, 0, 0, 1, left + r, top,
	// top edge
	"H", right - r,
	// top right corner
	"A", r, r, 0, 0, 1, right, top + r,
	// right edge
	"V", bottom - r,
	// bottom right corner
	"A", r, r, 0, 0, 1, right - r, bottom,
	// bottom edge
	"H", left + r,
	// botton left corner
	"A", r, r, 0, 0, 1, left, bottom - r,
	// left edge
	"Z"];
    pathstr = "";
    for (e in path) {
	pathstr += path[e];
	pathstr += " ";
    }
    shape.setAttribute("d", pathstr);
    return shape;
}

// Reposition a Dancer by revolving it around some point by an angle.
// The angle is expressed as a number of walls in promenade direction.
Dancer.prototype.revolve = function(center_x, center_y, angle) {
  var delta_x = this.x - center_x;
  var delta_y = this.y - center_y;
  var radians = 2 * Math.PI * angle / 4;
  var sin = Math.sin(radians);
  var cos = Math.cos(radians);
  // The dancer coordinate system (X axis ascending to the right, Y
  // axis ascending down the page) is the opposite handedness from the
  // cartesian plane, so we change the sign of the change in Y
  // coordinate.
  var revolved_x = delta_x * cos + delta_y * sin;
  var revolved_y = - delta_x * sin + delta_y * cos;
  this.x = center_x + revolved_x;
  this.y = center_y + revolved_y;
  this.direction = (this.direction + angle) % 4;
};

// Rotate the specified dancers around their common center point.
// Angle is expressed as a number of walls in promenade direction.
Floor.prototype.rotate = function(angle, dancers) {
  var floor = this;
  dancers = dancers.map(function(d) {
      return floor.getDancer(d);
  });
  var plus = function(a, b) { return a + b; };
  var center_x = dancers.map(function(d) { return d.x; }).reduce(plus)
    / dancers.length;
  var center_y = dancers.map(function(d) { return d.y; }).reduce(plus)
    / dancers.length;
  dancers.map(function(d) { d.revolve(center_x, center_y, angle); });
  return this;
};
