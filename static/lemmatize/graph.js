class Graph {

}

class LemmaFinder {
    constructor() {
        console.log("Yep");
        this.lemmas = [];
        this.resp_id = -1;
        for (let i = 0; i<10; ++i) {
            this.lemmas.push($(`#lemma${i}`))
        }
        this._connect_input();
    }

    get_input_value() {
        return this.input.val()
    }

    _connect_input() {
        this.input = $("#lemma_name");

        // KeyUp
        this.input.on('keyup', () => {
            this.resp_id++;
            let value = this.get_input_value();
            if ("" == value) {
                this.fill([]);
            } else {
                $.get({
                    url: `/lemmatize/api/search/${value}`,
                    data: {"resp_id": this.resp_id},
                    success: (data) => {
                        console.log(this, data);
                        if (this.resp_id == data.resp_id) {
                            this.fill(data.lemmas);
                        }
                    },
                    format: "JSON"
                })
            }
        });

        this.lemma_find_helper = $("#lemma_find");
        // Focus
        this.input.on('focus', () => {
            this.lemma_find_helper.attr('hidden', false);
        });
        this.input.on('blur', () => {
            this.lemma_find_helper.attr('hidden', true);
        })
    }

    fill(lemmas) {
        let _id = 0;
        for (let lemma of lemmas) {
            this.lemmas[_id].html(`${lemma.name} <span class="badge badge-default badge-pill">${lemma.meets_count}</span>`);
            this.lemmas[_id].attr('hidden', false);
            _id++;
        }

        for (; _id < 10; _id++) {
            this.lemmas[_id].attr('hidden', true);
        }
    }
}


class Drawer {
    constructor() {
        this.clear();


    }

    clear() {
        d3.select("svg").selectAll("*").remove();
    }
}


function draw(data, lemma_name) {
    d3.select("svg").selectAll("*").remove();

    let svg = d3.select("svg");
    let margin = {top: 20, right: 20, bottom: 30, left: 50};
    let width = +svg.attr("width") - margin.left - margin.right;
    let height = +svg.attr("height") - margin.top - margin.bottom;
    let g = svg.append("g").attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    let x = d3.scaleTime().rangeRound([0, width]);

    let y = d3.scaleLinear().rangeRound([height, 0]);

    let line = d3.line()
        .x(function(d) { return x(new Date(d[0] * 1000)); })
        .y(function(d) { return y(d[1]); });

    x.domain(d3.extent(data, (el) => new Date(el[0] * 1000)));
    y.domain(d3.extent(data, (el) => el[1]));

    g.append("g")
        .attr("transform", "translate(0," + height + ")")
        .call(d3.axisBottom(x))
        .select(".domain")
        .remove();


    // gridlines in x axis function
    function make_x_gridlines() {
        return d3.axisBottom(x)
            .ticks(12)
    }

// gridlines in y axis function
    function make_y_gridlines() {
        return d3.axisLeft(y)
            .ticks(12)
    }

// add the X gridlines
    svg.append("g")
        .attr("class", "grid")
        .attr("transform", `translate(${margin.left}, ${margin.top + height})`)
        .call(make_x_gridlines()
            .tickSize(-height)
            .tickFormat("")
        );

    // add the Y gridlines
    svg.append("g")
        .attr("class", "grid")
        .attr("transform", `translate(${margin.left}, ${margin.top})`)
        .call(make_y_gridlines()
            .tickSize(-width)
            .tickFormat("")
        );

    g.append("g")
        .call(d3.axisLeft(y))
        .append("text")
        .attr("fill", "#000")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", "0.71em")
        .attr("x", -6)
        .attr("text-anchor", "end")
        .text(lemma_name);

    g.append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-linejoin", "round")
        .attr("stroke-linecap", "round")
        .attr("stroke-width", 1.5)
        .attr("d", line);
}

function drawInit() {
    let svg = $("svg");
    function resizeSvg() {
        svg.attr("width", svg.parent().width());
        svg.attr("height", $(window).height());
    }
    resizeSvg();
    $(window).resize(resizeSvg);

    let lemma_finder = new LemmaFinder();

    let draw_button = $("#draw_button");

    draw_button.click(() => {
        let lemma = lemma_finder.get_input_value();
        let graphType = $("#graphType").val();
        let width = $("#width").val();

        $.get({
            url: `/lemmatize/data/${graphType}`,
            data: {
                word: lemma,
                width: width
            },
            beforeSend: () => {
                $("#helper").text("Processing...");
            },
            success: (data) => {
                $("#helper").text("Ok!");
                draw(data, lemma);
            },
            error: (err, status) => {
                $("#helper").text(`Error: ${status}!`);
            }
        });

        return false;
    });
}


$(document).ready(() => {
    drawInit();
});