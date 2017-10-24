
function describe_constraint (timing_parent_bar, variable_name, placeholder_form, geom, funcs) {
    placeholder_form.selectAll("*").remove();

    addNewRailOption();

    var time_number;
    if (timing_parent_bar) {
        time_number = timing_parent_bar.describe_constraint();
    } else {
        time_number = 0;
    }
    var newDiv = placeholder_form.append("div").classed("spec-row", true);

    getInequalityDurationOption(newDiv);

    var time_offset = (time_number > 0) ? " t_" + time_number + " + " : "";

    if (geom.left_fixed && geom.right_fixed) {
        addStartTimeValue(newDiv, time_offset, timing_parent_bar);
        newDiv.append("text").text("and");
        addEndTimeValue(newDiv, time_offset, timing_parent_bar);
    } else if (!geom.left_fixed && geom.right_fixed) {
        addEndTimeValue(newDiv, time_offset, timing_parent_bar);
    } else if (geom.left_fixed && !geom.right_fixed) {
        addStartTimeValue(newDiv, time_offset, timing_parent_bar);
    }

    newDiv.append("text").text(", " + variable_name + " is ");

    getInequalityOption(newDiv);

    // values
    if (geom.top_fixed && geom.bottom_fixed) {
        addMinValue(newDiv);
        newDiv.append("text").text(" and ");
        addMaxValue(newDiv);
    } else if (!geom.top_fixed && geom.bottom_fixed) {
        addMinValue(newDiv);
    } else if (geom.top_fixed && !geom.bottom_fixed) {
        addMaxValue(newDiv);
    }

    function addNewRailOption(){
        var initialDiv = placeholder_form.append("div").classed("spec-row", true);
        var new_rail_select = initialDiv.append("select").classed("spec_menu", true);

        new_rail_select.append("option")
            .text(" ")
            .attr("selected", "selected");

        new_rail_select.append("option")
            .text("For all times");

        new_rail_select.append("option")
            .text("For some times");


        new_rail_select.on("change", function(){
            var kind = false;
            if (this.value == "For all times"){
                kind = "all";
            } else if (this.value == "For some times"){
                kind = "some";
            }
            funcs.append_timing_bar(kind)
        });
    }

    function addMinValue(newDiv) {
        newDiv.append("input")
            .classed("spec_menu", true)
            .attr("value", funcs.YToVal(geom.rect_top + geom.height).toFixed(2))
            .attr("size", "6")
            .on("change", function () {
                geom.height = funcs.valToY(parseFloat(this.value)) - geom.rect_top;
                funcs.adjust_everything();
            });
    }

    function addMaxValue(newDiv) {
        newDiv.append("input")
            .classed("spec_menu", true)
            .attr("value", funcs.YToVal(geom.rect_top).toFixed(2))
            .attr("size", "6")
            .on("change", function () {
                var new_top = funcs.valToY(parseFloat(this.value));

                geom.height += (geom.rect_top - new_top);
                geom.rect_top = new_top;
                funcs.adjust_everything();
            });
    }

    function addStartTimeValue(newDiv, time_offset, timing_parent_bar) {

        newDiv.append("text").text(time_offset);
        var input = newDiv.append("input")
            .classed("spec_menu", true)
            .attr("size", "6");

        var start;
        if (timing_parent_bar){
            start = funcs.XToTime(geom.start_time_pos) - funcs.XToTime(geom.track_circle_pos);

            input.on("change", function () {
                var new_start_time_pos = funcs.timeToX(parseFloat(this.value) + funcs.XToTime(geom.track_circle_pos));
                geom.width += (geom.start_time_pos - new_start_time_pos);
                geom.start_time_pos = new_start_time_pos;
                funcs.adjust_everything();
            });

        } else {
            start = funcs.XToTime(geom.start_time_pos);

            input.on("change", function () {
                var new_start_time_pos = funcs.timeToX(parseFloat(this.value));
                geom.width += (geom.start_time_pos - new_start_time_pos);
                geom.start_time_pos = new_start_time_pos;
                funcs.adjust_everything();
            });
        }
        input.attr("value", start.toFixed(2));
    }

    function addEndTimeValue(newDiv, time_offset, timing_parent_bar) {

        newDiv.append("text").text(time_offset);
        var input = newDiv.append("input")
            .classed("spec_menu", true)
            .attr("size", "6");

        var end;
        if (timing_parent_bar){
            end = funcs.XToTime(geom.start_time_pos + geom.width) - funcs.XToTime(geom.track_circle_pos);

            input.on("change", function () {
                geom.width = funcs.timeToX(parseFloat(this.value) + funcs.XToTime(geom.track_circle_pos)) - geom.start_time_pos;
                funcs.adjust_everything();
            });

        } else {
            end = funcs.XToTime(geom.start_time_pos + geom.width);

            input.on("change", function () {
                geom.width = funcs.timeToX(parseFloat(this.value)) - geom.start_time_pos;
                funcs.adjust_everything();
            });

        }
        input.attr("value", end.toFixed(2));

    }

    function getInequalityDurationOption(newDiv) {

        var select = newDiv.append("select").classed("spec_menu", true);

        var between = select.append("option").text("between");
        var after = select.append("option").text("after");
        var before = select.append("option").text("before");
        var selected = select.append("option").text("always");

        if (geom.left_fixed && geom.right_fixed) {
            between.attr("selected", "selected");
        } else if (!geom.left_fixed && geom.right_fixed) {
            before.attr("selected", "selected");
        } else if (geom.left_fixed && !geom.right_fixed) {
            after.attr("selected", "selected");
        } else {
            selected.attr("selected", "selected");
        }

        select.on("change", function () {
            var new_interval_type = this.value;

            if (new_interval_type == "between") {
                geom.left_fixed = true;
                geom.right_fixed = true;

            }
            else if (new_interval_type == "after") {
                geom.left_fixed = true;
                geom.right_fixed = false;
            }
            else if (new_interval_type == "before") {
                geom.left_fixed = false;
                geom.right_fixed = true;
            }
            else if (new_interval_type == "always") {
                geom.left_fixed = false;
                geom.right_fixed = false;
            }

            funcs.drag_fixed();
            funcs.update_text();
        });
    }

    function getInequalityOption(newDiv) {
        var select = newDiv.append("select").classed("spec_menu", true);

        var between = select.append("option").text("between");
        var below = select.append("option").text("below");
        var above = select.append("option").text("above");
        var unconstrained = select.append("option").text("unconstrained");


        if (geom.top_fixed && geom.bottom_fixed) {
            between.attr("selected", "selected");
        } else if (geom.top_fixed && !geom.bottom_fixed) {
            below.attr("selected", "selected");
        } else if (!geom.top_fixed && geom.bottom_fixed) {
            above.attr("selected", "selected");
        } else {
            unconstrained.attr("selected", "selected");
        }

        select.on("change", function () {
            var new_interval_type = this.value;

            if (new_interval_type == "between") {
                geom.top_fixed = true;
                geom.bottom_fixed = true;
            }
            else if (new_interval_type == "below") {
                geom.top_fixed = true;
                geom.bottom_fixed = false;
            }
            else if (new_interval_type == "above") {
                geom.top_fixed = false;
                geom.bottom_fixed = true;
            }
            else if (new_interval_type == "unconstrained") {
                geom.top_fixed = false;
                geom.bottom_fixed = false;
            }

            funcs.drag_fixed();
            funcs.update_text();
        });
    }
}
