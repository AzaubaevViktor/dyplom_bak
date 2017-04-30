class ProcessorsDashBoard {
    constructor () {

    }

    init() {
        return new Promise((resolve, reject) => {
            this.div = $("#processors");
            this._getProcessors().then(
                () => {
                    this.firstButton = this.getAddBtn(0);
                    this.div.append(this.firstButton);
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

    getAddBtn(position) {
        return $(`<div class="btn-group btn-block add-btn" data-position="${position}">
                <button type="button" class="btn btn-success dropdown-toggle btn-block" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    Добавить
                </button>
                <div class="dropdown-menu">
                </div>
            </div>`)
    }

    _updateDropDowns() {
        let _this = this;
        $(".add-btn > .dropdown-menu").each(function (data){
            let el = $(this);
            console.log(el);
            let position = el.parent().data('position');
            el.html("").append(_this.dropdownGenerate(position))
        });
        $('.dropdown-toggle').dropdown();

        $(".add-processor").on('click', function () {
            let el = $(this);
            _this.addProcessor(el.data('position'), el.data('processor'));
            console.log(`Pressed Proc:${el.data('processor')}, position:${el.data('position') }`);
        });
    }

    addProcessor(position, processorName) {
        let processor = this.processors[processorName];
        if (0 == position) {
            this.firstButton.after(processor.render());
        }
    }

    dropdownGenerate(position) {
        function getA(processor, content) {
            return `<a class="dropdown-item add-processor" href="#" data-processor="${processor}" data-position="${position}">${content}</a>`
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

    renderArg(arg) {
        return $(`
<li class="list-group-item">
            <div class="form-group">
                <label for="input${arg.name}">${arg.desc}</label>
                <input type="${arg.type}" class="form-control" id="input${arg.name}" placeholder="${arg.default || ''}">
            </div>
</li>`)
    }

    renderArgs() {
        let form = $("<form></form>");

        for (let arg of this.args) {
            form.append(this.renderArg(arg));
        }

        return form;
    }

    render(position) {
        let card = $(`<div class="card" data-position="${position}  ">
                <div class="card-block">
                    <h4 class="card-title">${this.name}</h4>
                    <p class="card-text">${this.desc}</p>
                </div>
                <ul class="list-group list-group-flush">
                    
                    <!-- Rendered Args -->
                
                </ul>
                <div class="card-block">
                    <a href="#" class="card-link text-success">Add after</a>
                    <a href="#" class="card-link text-primary">Calculate</a>
                    <a href="#" class="card-link text-danger">Delete</a>
                </div>
            </div>`);
        card.find(".list-group").append(this.renderArgs());
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