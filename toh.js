/**
 * Line graph showing decoded values over time
 * @constructor
 *
 * @param {dict} args - A set of constructor arguments (see Nengo.Component)
 * @param {int} args.n_lines - number of decoded values
 * @param {float} args.min_value - minimum value on y-axis
 * @param {float} args.max_value - maximum value on y-axis
 * @param {Nengo.SimControl} args.sim - the simulation controller
 */

Nengo.TOH = function(parent, sim, args) {
    Nengo.Component.call(this, parent, args);
    var self = this;
    this.n_lines = args.n_lines || 1;
    this.sim = sim;
    this.display_time = args.display_time;

    /** for storing the accumulated data */
    var synapse = (args.synapse !== null) ? args.synapse : 0.01;
    this.data_store = new Nengo.DataStore(this.n_lines, this.sim, synapse);

    this.axes2d = new Nengo.TimeAxes(this.div, args);

    /** create the lines on the plots */
    var line = d3.svg.line()
        .x(function(d, i) {return self.axes2d.scale_x(times[i]);})
        .y(function(d) {return self.axes2d.scale_y(d);})
    this.path = this.axes2d.svg.append("g").selectAll('path')
                                    .data(this.data_store.data);

    var colors = Nengo.make_colors(this.n_lines);
    this.path.enter().append('path')
             .attr('class', 'line')
             .style('stroke', function(d, i) {return colors[i];});

    this.update();
    this.on_resize(this.get_screen_width(), this.get_screen_height());
};
Nengo.Value.prototype = Object.create(Nengo.Component.prototype);
Nengo.Value.prototype.constructor = Nengo.Value;

/**
 * Receive new line data from the server
 */
Nengo.Value.prototype.on_message = function(event) {
    var data = new Float32Array(event.data);
    this.data_store.push(data);
    this.schedule_update();
};

/**
 * Redraw the lines and axis due to changed data
 */
Nengo.Value.prototype.update = function() {
    /** let the data store clear out old values */
    this.data_store.update();

    /** determine visible range from the Nengo.SimControl */
    var t1 = this.sim.time_slider.first_shown_time;
    var t2 = t1 + this.sim.time_slider.shown_time;

    this.axes2d.set_time_range(t1, t2);

    /** update the lines */
    var self = this;
    var shown_data = this.data_store.get_shown_data();
    var line = d3.svg.line()
        .x(function(d, i) {
            return self.axes2d.scale_x(
                self.data_store.times[i + self.data_store.first_shown_index]);
            })
        .y(function(d) {return self.axes2d.scale_y(d);})
    this.path.data(shown_data)
             .attr('d', line);
};

/**
 * Adjust the graph layout due to changed size
 */
Nengo.Value.prototype.on_resize = function(width, height) {
    if (width < this.minWidth) {
        width = this.minWidth;
    }
    if (height < this.minHeight) {
        height = this.minHeight;
    };

    this.axes2d.on_resize(width, height);

    this.update();

    this.label.style.width = width;

    this.width = width;
    this.height = height;
    this.div.style.width = width;
    this.div.style.height= height;
};

Nengo.Value.prototype.generate_menu = function() {
    var self = this;
    var items = [];
    items.push(['Set range...', function() {self.set_range();}]);

    // add the parent's menu items to this
    // TODO: is this really the best way to call the parent's generate_menu()?
    return $.merge(items, Nengo.Component.prototype.generate_menu.call(this));
};


Nengo.Value.prototype.layout_info = function () {
    var info = Nengo.Component.prototype.layout_info.call(this);
    info.min_value = this.axes2d.scale_y.domain()[0];
    info.max_value = this.axes2d.scale_y.domain()[1];
    return info;
}

Nengo.Value.prototype.update_layout = function(config) {
    this.update_range(config.min_value, config.max_value);
    Nengo.Component.prototype.update_layout.call(this, config);
}

Nengo.Value.prototype.reset = function(event) {
    this.data_store.reset();
    this.schedule_update();
}