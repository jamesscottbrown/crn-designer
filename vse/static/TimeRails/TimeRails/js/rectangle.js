
function Rectangle(common_geom, options) {
    // Setting up scales and initial default positions
    /************************************************/
    var rect_geom = {
        width: 300 * 0.75,
        height: 200 * 0.75,
        dragbarw: 20,

        delay_line_length: 30,

        rect_top: 450 / 2,
        start_time_pos: 750 / 2,

        top_fixed: true,
        bottom_fixed: true,
        left_fixed: true,
        right_fixed: true,
        followRectangle: false,
        rectangleIndex: common_geom.rectangles.length,
        start_line_visible: true,

        num_rails_above: 0,
        get_num_rails_above: get_num_rails_above,

        rail_height: 0
    };

    function get_num_rails_above(){
        rect_geom.num_rails_above = 0;
        for (var i=0; i<rect_geom.rectangleIndex; i++){
            rect_geom.num_rails_above += 1;
            rect_geom.num_rails_above += common_geom.rectangles[i].get_num_rails();
        }
        return rect_geom.num_rails_above;
    }

    var timing_parent_bar = false;
    
    function timeToX(time){
        return common_geom.xScale(time);
    }
    function XToTime(x){
        return common_geom.xScale.invert(x);
    }
    function valToY(val){
        return common_geom.yScale(val);
    }
    function YToVal(y) {
        return common_geom.yScale.invert(y);
    }

    var helper_funcs = {
        getStartX: function (){ return rect_geom.track_circle_pos; },
        XToTime: XToTime,
        TimeToX: function(time){ return common_geom.xScale(time); },
        update_text: update_text,
        update_formula: update_formula
    };

    if (options){
        if (options.hasOwnProperty('start_time') && options.hasOwnProperty('track_circle_time') && options.hasOwnProperty('end_time')){
            rect_geom.delay_line_length = common_geom.xScale(options.start_time) - common_geom.xScale(options.track_circle_time);
            rect_geom.start_time_pos = common_geom.xScale(options.start_time);
            rect_geom.track_circle_pos = common_geom.xScale(options.track_circle_time);
            rect_geom.width = common_geom.xScale(options.end_time) - common_geom.xScale(options.start_time);
        } else {
            rect_geom.left_fixed = false;
            rect_geom.right_fixed = false;

            rect_geom.delay_line_length = 0;
            rect_geom.start_time_pos = common_geom.xScale(common_geom.xRange[0]);
            rect_geom.track_circle_pos = common_geom.xScale(common_geom.xRange[0]);
            rect_geom.width = common_geom.xScale(common_geom.xRange[1]) - common_geom.xScale(common_geom.xRange[0]);

        }

        if (!options.hasOwnProperty('lt') || !options.lt) {
            rect_geom.top_fixed = false;
            options.lt = common_geom.yScale(common_geom.yRange[1]);
        }
        rect_geom.rect_top = common_geom.yScale(options.lt);

        if (!options.hasOwnProperty('gt') || !options.gt){
            rect_geom.bottom_fixed = false;
            options.lt = common_geom.yScale(common_geom.yRange[0]);
        }

        rect_geom.height = common_geom.yScale(options.gt) - common_geom.yScale(options.lt);
    }

    rect_geom.track_circle_pos = rect_geom.start_time_pos - rect_geom.delay_line_length;
    rect_geom.delay_line_height = rect_geom.rect_top + rect_geom.height/2;


    // Function that defines where each element will be positioned
    /************************************************/
    function adjust_everything(update_description){
        // We rely on: rect_geom.width, rect_geom.height, , common_geom.h

        var num_rails_above = get_num_rails_above();
        rect_geom.rail_height = common_geom.h + (num_rails_above) * common_geom.track_padding;

        if (parseInt(common_geom.svg.attr("height")) < rect_geom.rail_height + common_geom.vertical_padding){
            common_geom.svg.attr("height", rect_geom.rail_height + common_geom.vertical_padding)
        }

        // convenience quanities (redundant)
        rect_geom.delay_line_length = rect_geom.start_time_pos - rect_geom.track_circle_pos;
        rect_geom.delay_line_height = rect_geom.rect_top + (rect_geom.height/2);

        // move things
        dragbarleft.attr("cx", rect_geom.start_time_pos)
            .attr("cy", rect_geom.delay_line_height);

        dragbarright.attr("cx", rect_geom.start_time_pos + rect_geom.width)
            .attr("cy", rect_geom.delay_line_height);

        dragbartop.attr("cx", rect_geom.start_time_pos + (rect_geom.width / 2))
            .attr("cy", rect_geom.rect_top);

        dragbarbottom.attr("cx", rect_geom.start_time_pos + (rect_geom.width / 2))
            .attr("cy", rect_geom.rect_top + rect_geom.height);

        dragrect
            .attr("x", rect_geom.start_time_pos)
            .attr("y", rect_geom.rect_top)
            .attr("height", rect_geom.height)
            .attr("width", Math.max(rect_geom.width,1));

        delay_line
            .attr("x1", rect_geom.track_circle_pos)
            .attr("x2", rect_geom.start_time_pos)
            .attr("y1", rect_geom.delay_line_height)
            .attr("y2", rect_geom.delay_line_height);

        startline.attr("x1", rect_geom.track_circle_pos)
            .attr("x2", rect_geom.track_circle_pos)
            .attr("y1", rect_geom.delay_line_height)
            .attr("y2", rect_geom.rail_height);

        track_circle.attr("cx", rect_geom.track_circle_pos)
                .attr("cy", rect_geom.rail_height);

        if (timing_parent_bar){
            // may need to shift time bars vertically
            timing_parent_bar.adjust_everything();
        }

        if (update_description){
          update_text();
        }
        set_edges();
    }

    function adjust_scales(new_xScale, new_yScale){

        function convertX(x){
            return new_xScale(common_geom.xScale.invert(x));
        }

        function convertY(y){
            return new_yScale(common_geom.yScale.invert(y));
        }

        // Adjust positions
        rect_geom.track_circle_pos = convertX(rect_geom.track_circle_pos);

        var rightPos = convertX(rect_geom.start_time_pos + rect_geom.width);
        rect_geom.width =  rightPos - convertX(rect_geom.start_time_pos);
        rect_geom.start_time_pos = convertX(rect_geom.start_time_pos);


        rect_geom.delay_line_height = convertY(rect_geom.delay_line_height);
        var bottom_pos =  convertY(rect_geom.height + rect_geom.rect_top);
        rect_geom.height = bottom_pos - convertY(rect_geom.rect_top);
        rect_geom.rect_top = convertY(rect_geom.rect_top);

        d3.select(common_geom.div_name).selectAll('.data-circle')
            .attr("cx", function(d){ return new_xScale(d.time); })
            .attr("cy", function(d){ return new_yScale(d.value); });

        d3.select(common_geom.div_name).selectAll(".example_line")
            .attr("x1", function(d){ return new_xScale(d.t1) })
            .attr("x2", function(d){ return new_xScale(d.t2) })
            .attr("y1", function(d){ return new_yScale(d.y) })
            .attr("y2", function(d){ return new_yScale(d.y) });

        d3.select(common_geom.div_name).selectAll(".example_circle")
            .attr("cx", function (d) {
                return new_xScale(d.t1)
            })
            .attr("cy", function (d) {
                return new_yScale(d.y)
            });

        d3.select(common_geom.div_name).selectAll(".example_box")
            .attr("x", function(d){ return new_xScale(d.t1) })
            .attr("width", function(d){ return new_xScale(d.t2) - new_xScale(d.t1) })
            .attr("y", function(d){ return new_yScale(d.y_max) })
            .attr("height", function(d){ return new_yScale(d.y_min) - new_yScale(d.y_max) });


        if (timing_parent_bar){
            timing_parent_bar.adjust_scales(new_xScale);
        }

        var new_data_line_generator = d3.svg.line()
        .x(function (d) { return new_xScale(d.time); })
        .y(function (d) { return new_yScale(d.value); });


        d3.select(common_geom.div_name).selectAll(".data-path")
            .attr("d", function(d){ return new_data_line_generator(d); });

        // Redraw
        common_geom.drawAxes(common_geom);
        adjust_everything();
    }


    // Callback functions for interactions
    /************************************************/
    var drag_track_circle = d3.behavior.drag()
        .origin(Object)
        .on("drag", function(){

            if (common_geom.specification_fixed && !timing_parent_bar){
                return;
            }

            var cursor_x = d3.mouse(common_geom.svg.node())[0];
            drag_track_circle_inner(cursor_x);
            adjust_everything(false);
        });


    function drag_track_circle_inner(cursor_x){
            var newx = imposeLimits(0, common_geom.w, cursor_x);

            if (timing_parent_bar) {
                newx = imposeLimits(timing_parent_bar.get_start_time() + rect_geom.delay_line_length,
                                    timing_parent_bar.get_end_time() + rect_geom.delay_line_length, newx);
            }

            var shift = newx - rect_geom.start_time_pos;
            rect_geom.track_circle_pos += shift;
            rect_geom.start_time_pos += shift;

            if (rect_geom.followRectangle){
                for (var i=0; i<common_geom.rectangles.length; i++){
                    if (i == rect_geom.rectangleIndex){ continue; }

                    var other_rect = common_geom.rectangles[i].rect_geom;
                    other_rect.track_circle_pos += shift;
                    other_rect.start_time_pos += shift;
                    common_geom.rectangles[i].adjust_everything();
                }
            }
    }

    function drag_fixed() {
        // resize so edges remain on axes if necessary
        if (!rect_geom.left_fixed) {
            drag_resize_left_inner(rect_geom.start_time_pos, 0);
        }
        if (!rect_geom.right_fixed) {
            drag_resize_right_inner(rect_geom.start_time_pos, common_geom.w);
        }
        if (!rect_geom.top_fixed) {
            drag_resize_top_inner(rect_geom.rect_top, 0);
        }
        if (!rect_geom.bottom_fixed) {
            drag_resize_bottom_inner(rect_geom.rect_top, common_geom.h);
        }
    }

    function dragmove(d) {
        if (common_geom.specification_fixed){ return; }

        // horizontal movement
        var rect_center = d3.mouse(common_geom.svg.node())[0] - rect_geom.width/2;

        if (rect_center < rect_geom.track_circle_pos){
            drag_track_circle_inner(rect_center);
        } else {
            var new_start_pos = imposeLimits(rect_geom.track_circle_pos, common_geom.w - rect_geom.width, rect_center);
            rect_geom.start_time_pos = new_start_pos;
        }

        // vertical movement
        var rect_center = d3.mouse(common_geom.svg.node())[1] - rect_geom.height/2;
        rect_geom.rect_top = imposeLimits(0, common_geom.h - rect_geom.height, rect_center);
        adjust_everything(true);
    }

    function drag_resize_left(d) {
        if (common_geom.specification_fixed){ return; }

        if (!rect_geom.left_fixed) {
            return;
        }

        var oldx = rect_geom.start_time_pos;
        //Max x on the right is x + width - dragbarw
        //Max x on the left is 0 - (dragbarw/2)

        var cursor_x = d3.mouse(common_geom.svg.node())[0];
        var newx = imposeLimits(rect_geom.track_circle_pos, rect_geom.start_time_pos + rect_geom.width, cursor_x);
        drag_resize_left_inner(oldx, newx);
    }

    function drag_resize_left_inner(oldx, newx) {
        rect_geom.start_time_pos = newx;
        rect_geom.width = rect_geom.width + (oldx - newx);

        adjust_everything(true);
    }


    function drag_resize_right(d) {
        if (common_geom.specification_fixed){ return; }

        if (!rect_geom.right_fixed) {
            return;
        }

        //Max x on the left is x - width
        //Max x on the right is width of screen + (dragbarw/2)
        var dragx = imposeLimits(rect_geom.start_time_pos, common_geom.w, rect_geom.start_time_pos + rect_geom.width + d3.event.dx);
        drag_resize_right_inner(rect_geom.start_time_pos, dragx);
    }

    function drag_resize_right_inner(oldx_left, newx_right) {
        rect_geom.width = newx_right - oldx_left;
        adjust_everything(true);
    }


    function drag_resize_top(d) {
        if (common_geom.specification_fixed){ return; }

        if (!rect_geom.top_fixed) {
            return;
        }

        var oldy = rect_geom.rect_top;
        //Max x on the right is x + width - dragbarw
        //Max x on the left is 0 - (dragbarw/2)

        var cursor_y = d3.mouse(common_geom.svg.node())[1];
        var newy = imposeLimits(0, rect_geom.rect_top + rect_geom.height - (rect_geom.dragbarw / 2), cursor_y);
        drag_resize_top_inner(oldy, newy);
    }

    function drag_resize_top_inner(oldy, newy) {
        //Max x on the right is x + width - dragbarw
        //Max x on the left is 0 - (dragbarw/2)

        rect_geom.rect_top = newy;
        rect_geom.height = rect_geom.height + (oldy - newy);
        adjust_everything(true);
    }


    function drag_resize_bottom(d) {
        if (common_geom.specification_fixed){ return; }

        if (!rect_geom.bottom_fixed) {
            return;
        }

        //Max x on the left is x - width
        //Max x on the right is width of screen + (dragbarw/2)
        var dragy = imposeLimits(rect_geom.rect_top + (rect_geom.dragbarw / 2), common_geom.h, rect_geom.rect_top + rect_geom.height + d3.event.dy);
        drag_resize_bottom_inner(rect_geom.rect_top, dragy);
    }

    function drag_resize_bottom_inner(oldy, newy) {
        //Max x on the left is x - width
        //Max x on the right is width of screen + (dragbarw/2)

        //recalculate width
        rect_geom.height = newy - oldy;
        adjust_everything(true);
    }


    // Context menus and associated functions
    /************************************************/
    var menu = [
        {
            title: 'Constraint starts at fixed time',
            action: function(elm, d, i) {
                if (timing_parent_bar){
                    timing_parent_bar.delete();
                    timing_parent_bar = false;
                    common_geom.adjustAllRectangles();
                    update_text();
                }
            },
            disabled: false // optional, defaults to false
        },
        {
            title: 'Constraint applies at <i>some</i> time in range',
            action: function(elm, d, i) {
                if (timing_parent_bar){
                    timing_parent_bar.delete();
                }
                timing_parent_bar = create_bar(1, 'some', common_geom, rect_geom, placeholder_form, newg, helper_funcs);
                update_text();
            }
        },
        {
            title: 'Constraint applies at <i>all</i> times in range',
            action: function(elm, d, i) {
                if (timing_parent_bar){
                    timing_parent_bar.delete();
                }
                timing_parent_bar = create_bar(1, 'all', common_geom, rect_geom, placeholder_form, newg, helper_funcs);
                update_text();
            }
        },

        {
            divider: true
        },
        {
            title: 'Eventually-Always',
            action: function(elm, d, i) {
                if (timing_parent_bar){
                    timing_parent_bar.delete();
                }
                timing_parent_bar = create_bar(1, 'all', common_geom, rect_geom, placeholder_form, newg, helper_funcs);
                timing_parent_bar.set_parent_bar('some')();
                update_text();
            }
        },
        {
            title: 'Always-Eventually',
            action: function(elm, d, i) {
                if (timing_parent_bar){
                    timing_parent_bar.delete();
                }
                timing_parent_bar = create_bar(1, 'some', common_geom, rect_geom, placeholder_form, newg, helper_funcs);
                timing_parent_bar.set_parent_bar('all')();
                update_text();
            }
        }

    ];

    function rclick_left() {
        if (common_geom.specification_fixed){ return; }

        rect_geom.left_fixed = !rect_geom.left_fixed;

        if (!rect_geom.left_fixed) {
            drag_resize_left_inner(rect_geom.start_time_pos, 0);
        }

        set_edges();
        return false;
    }

    function rclick_right() {
        if (common_geom.specification_fixed){ return; }

        rect_geom.right_fixed = !rect_geom.right_fixed;
        if (!rect_geom.right_fixed) {
            drag_resize_right_inner(rect_geom.start_time_pos, common_geom.w);
        }
        set_edges();
    }

    function rclick_top() {
        if (common_geom.specification_fixed){ return; }

        rect_geom.top_fixed = !rect_geom.top_fixed;
        if (!rect_geom.top_fixed) {
            drag_resize_top_inner(rect_geom.rect_top, 0);
        }
        set_edges();
    }

    function rclick_bottom() {
        if (common_geom.specification_fixed){ return; }

        rect_geom.bottom_fixed = !rect_geom.bottom_fixed;
        if (!rect_geom.bottom_fixed) {
            drag_resize_bottom_inner(rect_geom.rect_top, common_geom.h);
        }
        set_edges();
    }


    // Actually create visual elements
    /************************************************/
    d3.select(common_geom.div_name).select(".space-div").style("width", common_geom.w + "px");

    var placeholder_form = d3.select(common_geom.div_name).select(".placeholder-form")
                            .append('div')
                            .classed(".rect-" + rect_geom.rectangleIndex, true)
        .classed("single-rect-spec", true);
    var placeholder_latex = d3.select(common_geom.div_name).select(".placeholder-latex");
    var placeholder_latex_formula = placeholder_latex.append("div");

    var options_form = d3.select(common_geom.div_name).append("div").classed("space-div", true).append("form");

    var newg = common_geom.svg.append("g");

    // we draw these lines before the dragrect to improve carity when rectangle is very thin
    var delay_line = newg.append("line").classed("red-line", true);

    var startline = newg.append("line").classed("red-line", true);

    var dragrect = newg.append("rect")
        .attr("id", "active")
        .attr("fill", "lightgreen")
        .attr("fill-opacity", .25)
        .attr("cursor", "move")
        .call(d3.behavior.drag()
            .origin(Object)
            .on("drag", dragmove));


        var rectMenu = [{
            title: function(){ return 'Adjust values'; },
            action: adjust_rect_values
        },
        {
            title: function(){ return rect_geom.start_line_visible ? "Hide start line" : "Show start line"},
            action: toggle_start_line_visibility
        },
        {
            title: function(){ return rect_geom.followRectangle ? 'Stop other rectangles following' : 'Make other rectangles follow'; },
            action: function () {
                rect_geom.followRectangle = ! rect_geom.followRectangle;
            }
        },
        {
            title: function(){ return 'Delete rectangle'; },
            action: deleteRectangle
    }];


    dragrect.on('contextmenu', d3.contextMenu(rectMenu));

    var dragbarleft = newg.append("circle")
        .attr("id", "dragleft")
        .attr("r", rect_geom.dragbarw / 2)
        .attr("fill", "lightgray")
        .attr("fill-opacity", .5)
        .attr("cursor", "ew-resize")
        .call(
            d3.behavior.drag()
            .origin(Object)
            .on("drag", drag_resize_left)
        ).on('contextmenu', d3.contextMenu([{
            title: function(){
                return rect_geom.left_fixed ? 'Remove limit' : 'Apply limit';
            },
            action: rclick_left
        }]));

    var dragbarright = newg.append("circle")
        .attr("id", "dragright")
        .attr("r", rect_geom.dragbarw / 2)
        .attr("fill", "lightgray")
        .attr("fill-opacity", .5)
        .attr("cursor", "ew-resize")
        .call(
            d3.behavior.drag()
            .origin(Object)
            .on("drag", drag_resize_right)
        ).on('contextmenu', d3.contextMenu([{
            title: function(){
                return rect_geom.right_fixed ? 'Remove limit' : 'Apply limit';
            },
            action: rclick_right
        }]));


    var dragbartop = newg.append("circle")
        .attr("r", rect_geom.dragbarw / 2)
        .attr("id", "dragtop")
        .attr("fill", "lightgray")
        .attr("fill-opacity", .5)
        .attr("cursor", "ns-resize")
        .call(
            d3.behavior.drag()
            .origin(Object)
            .on("drag", drag_resize_top)
        ).on('contextmenu', d3.contextMenu([{
            title: function(){
                return rect_geom.top_fixed ? 'Remove limit' : 'Apply limit';
            },
            action: rclick_top
        }]));


    var dragbarbottom = newg.append("circle")
        .attr("id", "dragbottom")
        .attr("r", rect_geom.dragbarw / 2)
        .attr("fill", "lightgray")
        .attr("fill-opacity", .5)
        .attr("cursor", "ns-resize")
        .call( d3.behavior.drag()
        .origin(Object)
        .on("drag", drag_resize_bottom)
        ).on('contextmenu', d3.contextMenu([{
            title: function(){
                return rect_geom.bottom_fixed ? 'Remove limit' : 'Apply limit';
            },
            action: rclick_bottom
        }]));

    var track_circle = newg
        .append("g")
        .append("circle")
        .attr("r", 7)
        .classed("track_circle", true)
        .on('contextmenu', d3.contextMenu(menu))
        .call(drag_track_circle);

    function toggle_start_line_visibility(){

        if (timing_parent_bar){ return; }

        rect_geom.start_line_visible = !rect_geom.start_line_visible;

        var visibility_string = rect_geom.start_line_visible ? "visible" : "hidden";
        track_circle.style("visibility", visibility_string);
        startline.style("visibility", visibility_string);
        delay_line.style("visibility", visibility_string);
    }

    // Shading edges of rectangle
    /************************************************/

    function set_edges() {

        dragrect.style("stroke", "black");

        // Edging goes top, right, bottom, left
        // As a rectangle has 4 sides, there are 2^4 = 16 cases to handle.

        // 4 edges:
        if (rect_geom.top_fixed && rect_geom.bottom_fixed && rect_geom.left_fixed && rect_geom.right_fixed) {
            dragrect.style("stroke-dasharray", [rect_geom.width + rect_geom.height + rect_geom.width + rect_geom.height].join(','));
        }

        // 3 edges
        else if (rect_geom.top_fixed && rect_geom.bottom_fixed && rect_geom.right_fixed) {
            dragrect.style("stroke-dasharray", [rect_geom.width + rect_geom.height + rect_geom.width, rect_geom.height].join(','));
        } else if (rect_geom.top_fixed && rect_geom.bottom_fixed && rect_geom.left_fixed) {
            dragrect.style("stroke-dasharray", [rect_geom.width, rect_geom.height, rect_geom.width + rect_geom.height].join(','));
        } else if (rect_geom.top_fixed && rect_geom.left_fixed && rect_geom.right_fixed) {
            dragrect.style("stroke-dasharray", [rect_geom.width + rect_geom.height, rect_geom.width, rect_geom.height].join(','));
        } else if (rect_geom.bottom_fixed && rect_geom.left_fixed && rect_geom.right_fixed) {
            dragrect.style("stroke-dasharray", [0, (rect_geom.width), rect_geom.height + rect_geom.width + rect_geom.height].join(','));
        }

        // 2 edges
        else if (rect_geom.top_fixed && rect_geom.bottom_fixed) {
            dragrect.style("stroke-dasharray", [rect_geom.width, rect_geom.height, rect_geom.width, rect_geom.height].join(','));
        } else if (rect_geom.top_fixed && rect_geom.left_fixed) {
            dragrect.style("stroke-dasharray", [rect_geom.width, rect_geom.height + rect_geom.width, rect_geom.height].join(','));
        } else if (rect_geom.top_fixed && rect_geom.right_fixed) {
            dragrect.style("stroke-dasharray", [rect_geom.width + rect_geom.height, rect_geom.width + rect_geom.height].join(','));
        } else if (rect_geom.bottom_fixed && rect_geom.left_fixed) {
            dragrect.style("stroke-dasharray", [0, rect_geom.width + rect_geom.height, rect_geom.width + rect_geom.height].join(','));
        } else if (rect_geom.bottom_fixed && rect_geom.right_fixed) {
            dragrect.style("stroke-dasharray", [0, rect_geom.width, rect_geom.height + rect_geom.width, rect_geom.height].join(','));
        } else if (rect_geom.left_fixed && rect_geom.right_fixed) {
            dragrect.style("stroke-dasharray", [0, rect_geom.width, rect_geom.height, rect_geom.width, rect_geom.height].join(','));
        }

        // 1 edges
        else if (rect_geom.top_fixed) {
            dragrect.style("stroke-dasharray", [rect_geom.width, (rect_geom.height + rect_geom.width + rect_geom.height)].join(','));
        }
        else if (rect_geom.bottom_fixed) {
            dragrect.style("stroke-dasharray", [0, (rect_geom.width + rect_geom.height), rect_geom.width, rect_geom.height].join(','));
        }
        else if (rect_geom.left_fixed) {
            dragrect.style("stroke-dasharray", [0, (rect_geom.width + rect_geom.height + rect_geom.width), rect_geom.height].join(','));
        }
        else if (rect_geom.right_fixed) {
            dragrect.style("stroke-dasharray", [0, (rect_geom.width + rect_geom.height + rect_geom.width), rect_geom.height].join(','));
        }

        // 0 edges
        else {
            dragrect.style("stroke-dasharray", [0, rect_geom.width + rect_geom.height + rect_geom.width + rect_geom.height].join(','));
        }

        update_text();
    }


    // Describing selected region
    /************************************************/

    function getYLatexString(){

        var y_upper = YToVal(rect_geom.rect_top).toFixed(2);
        var y_lower = YToVal( valToY(y_upper) + rect_geom.height ).toFixed(2);

        var latex_string;

        // 2 bounds
        if (rect_geom.top_fixed && rect_geom.bottom_fixed) {
            latex_string = "(" + y_lower + "< x_" + common_geom.index + "<" + y_upper + ")";
        }

        // 1 bound
        else if (rect_geom.top_fixed) {
            latex_string = "(x_" + common_geom.index + "<" + y_upper + ")";
        }
        else if (rect_geom.bottom_fixed) {
            latex_string = "(" + y_lower + "< x_" + common_geom.index + ")";
        }

        // 0 bounds
        else {
            // Don't convert, but keep as an easily checkable sentinel value
            latex_string = "";
        }

        return latex_string;
    }

    function update_formula(){
        var latex_string =  get_latex_string();
        placeholder_latex_formula.html("$" + latex_string + "$");
        MathJax.Hub.Queue(["Typeset", MathJax.Hub]);
    }

    function get_latex_string(){
        var y_latex_string = getYLatexString();
        var latex_string = "";

        // If rectangle has a parent bar, rectangle is represented by a Global term with start/end times measured from start_line
        if (timing_parent_bar){
            latex_string = timing_parent_bar.getLatex();
            var delay_time = XToTime(rect_geom.start_time_pos) - XToTime(rect_geom.track_circle_pos);
            delay_time = delay_time.toFixed(2);

            var length =   XToTime(rect_geom.start_time_pos + rect_geom.width) - XToTime(rect_geom.track_circle_pos);
            length = length.toFixed(2);

            if (delay_time == 0 && length == 0){
                return latex_string + y_latex_string;
            } else {
                var symbol = common_geom.use_letters ? ' G' : ' \\square';
                return latex_string + symbol + "_{[" + delay_time + "," + length + "]}" + y_latex_string;
            }
        }

        // Otherwise, rectangle is represented by a Global term with a start and end time
        if (!rect_geom.top_fixed && !rect_geom.bottom_fixed) {
            return latex_string + "\\;"; // Insert latex symbol for space to avoid empty forumla appearing as '$$'
        }

        var x_lower = XToTime(rect_geom.start_time_pos).toFixed(2);
        var x_upper = XToTime(rect_geom.start_time_pos + rect_geom.width ).toFixed(2);

        if (!rect_geom.right_fixed){
            x_upper = "\\infty";
        }

        if (!rect_geom.left_fixed){
            x_lower = "0";
        }

        var symbol = common_geom.use_letters ? ' G' : ' \\square';
        return latex_string + symbol + "_{[" + x_lower + "," + x_upper + "]}" + y_latex_string;
    }

    function update_text() {

        function create_initial_bar (kind){
            timing_parent_bar = create_bar(1, kind, common_geom, rect_geom, placeholder_form, newg, helper_funcs);
            update_text();
        }

        var update_functions = {
            YToVal: YToVal,
            valToY: valToY,
            XToTime: XToTime,
            timeToX: timeToX,
            drag_fixed: drag_fixed,
            update_text: update_text,
            adjust_everything: adjust_everything,
            append_timing_bar: append_timing_bar
        };
        describe_constraint(timing_parent_bar, common_geom.variable_name, placeholder_form, rect_geom, update_functions);

        update_formula();
    }


    // functions for generating specification to save

    function getYSpecString(){

        var y_upper = YToVal(rect_geom.rect_top).toFixed(2);
        var y_lower = YToVal( valToY(y_upper) + rect_geom.height ).toFixed(2);

        var spec_string;

        // 2 bounds
        if (rect_geom.top_fixed && rect_geom.bottom_fixed) {
            spec_string = "Inequality(gt=" + y_lower + ", lt=" + y_upper;
        }

        // 1 bound
        else if (rect_geom.top_fixed) {
            spec_string = "Inequality(lt=" + y_upper;
        }
        else if (rect_geom.bottom_fixed) {
            spec_string = "Inequality(gt=" + y_lower;
        }

        // 0 bounds
        else {
            // Don't convert, but keep as an easily checkable sentinel value
            spec_string = "";
        }

        return spec_string;
    }

    function getSpecString(){
        var y_spec_string = getYSpecString();
        var spec_string = "";

        // If rectangle has a parent bar, rectangle is represented by a Global term with start/end times measured from start_line
        if (timing_parent_bar){
            spec_string = timing_parent_bar.getSpecString();

            var delay_time = XToTime(rect_geom.start_time_pos) - XToTime(rect_geom.track_circle_pos);
            delay_time = delay_time.toFixed(2);

            var length =   XToTime(rect_geom.start_time_pos + rect_geom.width) - XToTime(rect_geom.track_circle_pos);
            length = length.toFixed(2);

            if (delay_time == 0 && length == 0){
                spec_string += y_spec_string;
            } else {
                spec_string += "Globally(" + delay_time + "," + length + "," + y_spec_string;
            }

            var numLeftParens = 0;
            for (var i=0; i<spec_string.length; i++){
                if (spec_string[i] == "("){ numLeftParens++; }
            }

            return spec_string + ")".repeat(numLeftParens);
        }

        // Otherwise, rectangle is represented by a Global term with a start and end time
        if (!rect_geom.top_fixed && !rect_geom.bottom_fixed) {
            return spec_string;
        }

        var x_lower = XToTime(rect_geom.start_time_pos).toFixed(2);
        var x_upper = XToTime( timeToX(x_lower) + rect_geom.width ).toFixed(2);

        if (!rect_geom.right_fixed){
            x_upper = "Inf";
        }

        if (!rect_geom.left_fixed){
            x_lower = "0";
        }

        return spec_string + "Globally(" + x_lower + "," + x_upper + ", " + y_spec_string + "))";
    }

    function add_timing_bar(kind, options){
        // create timing-bar, and set it as immediate parent of rectangle
        // kind is 'some' or 'all'

        if (timing_parent_bar){
            timing_parent_bar.set_parent_bar(kind, options)();
        } else {
            timing_parent_bar = create_bar(1, kind, common_geom, rect_geom, placeholder_form, newg, helper_funcs, options);
        }
        update_text();
    }

    function append_timing_bar(kind, options){
        // create a new bar as the parent of all parents of rectangle

        if (!timing_parent_bar){
            add_timing_bar(kind, options);
        } else {
            var bar = timing_parent_bar;
            while (bar.getTimingParentBar()) {
                bar = bar.getTimingParentBar();
            }
            bar.set_parent_bar(kind, options)();
        }
    }


    function deleteRectangle(){

         if (timing_parent_bar) {
             timing_parent_bar.delete();
         }

        dragbarleft.remove();
        dragbarright.remove();
        dragbartop.remove();
        dragbarbottom.remove();
        dragrect.remove();
        delay_line.remove();
        startline.remove();
        track_circle.remove();

        common_geom.rectangles.splice(rect_geom.rectangleIndex, 1);
        for (var i=0; i<common_geom.rectangles; i++){
            common_geom.rectangles[i].saveRectangleIndex(i);
        }

        // delete description
        placeholder_latex_formula.remove();
        placeholder_form.remove();
        common_geom.adjustAllRectangles();
    }

    function adjust_rect_values(){
        d3.select("#paramModal").remove();
        var modal_contents = d3.select(common_geom.div_name).append("div")
            .attr("id", "paramModal")
            .classed("modal", true)
            .classed("fade", true)

            .append("div")
            .classed("modal-dialog", true)

            .append("div")
            .classed("modal-content", true);

        var modalHeader = modal_contents.append("div").classed("modal-header", true);
        var modalBody = modal_contents.append("div").classed("modal-body", true);
        var modalFooter = modal_contents.append("div").classed("modal-footer", true);

        modalHeader.append("button")
            .classed("close", true)
            .attr("data-dismiss", "modal") // ???
            .attr("type", "button")
            .attr("aria-hidden", true)
            .text('×');


        modalHeader.append("h4").text("Adjust values").classed("modal-title", true);

        var start, end;
        if (timing_parent_bar){
            start = XToTime(rect_geom.start_time_pos) - XToTime(rect_geom.track_circle_pos);
            end = XToTime(rect_geom.start_time_pos + rect_geom.width) - XToTime(rect_geom.track_circle_pos);
        } else {
            start = XToTime(rect_geom.start_time_pos);
            end = XToTime(rect_geom.start_time_pos + rect_geom.width);
        }


        var timeDiv = modalBody.append("div");
        timeDiv.append("text").text("From ");
        var startTimeBox = timeDiv.append("input").attr("value",  start.toFixed(2)).node();
        timeDiv.append("text").text(" to ");
        var endTimeBox = timeDiv.append("input").attr("value",  end.toFixed(2)).node();

        var valDiv = modalBody.append("div");
        valDiv.append("text").text("Value is between");
        var minValBox = valDiv.append("input").attr("value", YToVal(rect_geom.rect_top + rect_geom.height).toFixed(2)).node();
        valDiv.append("text").text(" and ");
        var maxValBox = valDiv.append("input").attr("value", YToVal(rect_geom.rect_top).toFixed(2)).node();


        modalFooter.append("button").text("Save").on("click", function(){

            if (timing_parent_bar){
                rect_geom.width = timeToX(parseFloat(endTimeBox.value)) - timeToX(parseFloat(startTimeBox.value));
                rect_geom.start_time_pos =  timeToX(parseFloat(startTimeBox.value) + XToTime(rect_geom.track_circle_pos));
            } else {
                rect_geom.width = timeToX(parseFloat(endTimeBox.value)) - timeToX(parseFloat(startTimeBox.value));
                rect_geom.start_time_pos =  timeToX(parseFloat(startTimeBox.value));

                rect_geom.track_circle_pos = rect_geom.start_time_pos;
            }

            rect_geom.height = valToY(parseFloat(minValBox.value)) - valToY(parseFloat(maxValBox.value));
            rect_geom.rect_top = valToY(parseFloat(maxValBox.value));

            adjust_everything(true);
        })

        .attr("data-dismiss", "modal");
        modalFooter.append("button").text("Close").attr("data-dismiss", "modal");

        $('#paramModal').modal('toggle');
    }


    adjust_everything(true);
    return {add_bar: append_timing_bar, getSpecString: getSpecString, adjust_scales: adjust_scales,
            adjust_everything: adjust_everything, rect_geom: rect_geom,
            saveRectangleIndex: function(index){rect_geom.rectangleIndex = index;},
            update_formula: update_formula,
            get_num_rails: function (){ return timing_parent_bar ? (1 + timing_parent_bar.get_num_rails()) : 0; },
            get_num_rails_above: get_num_rails_above
            }
}