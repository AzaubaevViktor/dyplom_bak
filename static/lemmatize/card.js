class ProcessorsDashBoard {
    constructor () {

    }

    init() {
        return new Promise((resolve, reject) => {
            this.div = $("#processors");
            this.firstButton = $("#add-proc-btn");
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

        this.div.prepend(processor.render());

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
}

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
                <input type="${arg.type}" class="form-control" id="input${arg.name}" placeholder="${arg.default || ''}">
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

    render(position) {
        let card = $(`
            <div class="card" data-position="${position}  ">
                <div class="card-block">
                    <h4 class="card-title">${this.name}</h4>
                    <p class="card-text">${this.desc}</p>
                </div>
                <ul class="list-group list-group-flush">
                    <!-- Rendered Args -->
                </ul>
                <div class="card-block">
                    <a href="#" class="card-link text-primary" data-action="calc">Calculate</a>
                    <a href="#" class="card-link text-danger" data-action="delete">Delete</a>
                </div>
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