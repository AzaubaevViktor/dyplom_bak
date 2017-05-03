class ProcessorsDashBoard {
    constructor () {
        this.cardId = 0;
    }

    init() {
        return new Promise((resolve, reject) => {
            this.div = $("#processors");
            this.firstButton = $("#add-proc-btn");
            this.calcBtn = $("#calc-btn").on('click', () => {this.calc()});
            this.div.sortable({
                cancel: '.list-group',
                handle: '.card-block',
            });
            this._getProcessors().then(
                () => {
                    this._updateDropDowns();
                    resolve();
                },
                reject
            )
        });
    }

    _getProcessors() {
        return new Promise((resolve, reject) => {
            $.get({
                url: '/lemmatize/api/processors',
                success: (data) => {
                    this.processors = {};
                    for (let key in data) {
                        let item = data[key];
                        this.processors[item.id] = new ProcessorCard(
                            item.id,
                            item.name,
                            item.desc,
                            item.args
                        )
                    }
                    resolve();
                },
                error: (err, status) => {
                    reject(err);
                }
            })
        });
    }

    _updateDropDowns() {
        let _this = this;
        this.firstButton.find(".dropdown-menu").each(function (data){
            let el = $(this);
            console.log(el);
            let position = el.parent().data('position');
            el.html("").append(_this._dropdownGenerate(position))
        });
        $('.dropdown-toggle').dropdown();

        $(".add-processor").on('click', function () {
            let el = $(this);
            _this.addProcessor(el.data('processor'));
            console.log(`Pressed Proc:${el.data('processor')}`);
        });
    }

    addProcessor(processorName) {
        let processor = this.processors[processorName];

        this.div.append(processor.render(this.cardId));

        this.cardId++;
    }

    _dropdownGenerate(position) {
        function getA(processor, content) {
            return `<a class="dropdown-item add-processor" href="#" data-processor="${processor}">${content}</a>`
        }

        let items = "";
        let procs = this.processors;

        for (let key in procs) {
            let proc = procs[key];
            items += getA(proc.id, proc.name)
        }

        return items;
    }

    getData() {
        let cardIds = this.div.sortable("toArray");
        let data = [];
        for (let cardId of cardIds) {
            data.push(ProcessorCard.getData($(`.card#${cardId}`)));
        }
        return data;
    }

    calc() {
        $.post({
            url: "/lemmatize/calc",
            data: {
                info: JSON.stringify(this.getData()),
                csrfmiddlewaretoken: csrf_token
            },
            dataType: 'json',
            success: (data) => {
                draw(data);
                console.log("draw", data);
            },
            error: (data) => {
                console.log(data);
                alert(`Error ${data.statusText}`);
            }
        })
    }
}

let typesAssign = {
    int: 'number',
    str: 'text'
};

class ProcessorCard {
    constructor (_id, name, desc, args) {
        this.id = _id;
        this.name = name;
        this.desc = desc;
        this.args = args;
    }

    static _renderArg(arg) {
        return $(`
        <li class="list-group-item">
            <div class="form-group">
                <label for="input${arg.name}">${arg.desc}</label>
                <input type="${typesAssign[arg.type]}" class="form-control" id="${arg.name}" placeholder="${arg.default || ''}">
            </div>
        </li>`)
    }

    _renderArgs() {
        let form = $("<form></form>");

        for (let arg of this.args) {
            form.append(ProcessorCard._renderArg(arg));
        }

        return form;
    }

    static getData(div) {
        let data = {
            processor: div.data("processor")
        };
        for (let el of div.find(".proc-arguments  input")) {
            let $el = $(el);
            data[$el.attr('id')] = $el.val();
        }
        return data;
    }

    render(cardId) {
        let card = $(`
            <div id="${cardId}" class="card" data-processor="${this.id}">
                <div class="proc-header card-block">
                    <h4 class="card-title">${this.name}
                        <a href="#" class="close card-link text-danger text-right" data-action="delete">
                            <span aria-hidden="true">&times;</span>
                        </a>
                    </h4>
                    <p class="card-text">${this.desc}</p>
                </div>
                <ul class="proc-arguments list-group list-group-flush">
                    <!-- Rendered Args -->
                </ul>
            </div>`);
        card.find(".list-group").append(this._renderArgs());
        card.find("a").on('click', function () {
            let $this = $(this);
            console.log($this);
            if ('delete' == $this.data('action')) {
                $this.closest(".card").remove();
                return false;
            }
        });

        return card;
    }
}

function cardInit() {
    let procs = new ProcessorsDashBoard();
    procs.init().then(() => {console.log("Ok!")});
}

$(document).ready(() => {
    cardInit();
});