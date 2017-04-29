class Processors {
    constructor () {

    }

    init() {
        return new Promise((resolve, reject) => {
            this.div = $("#processors");
            this._getProcessors().then(
                () => {
                    this.div.append(this.getAddBtn(0));
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
                    this.processors = data;
                    resolve();
                },
                error: (err, status) => {
                    reject(err);
                }
            })
        });
    }

    getAddBtn(_id) {
        return `<div class="btn-group btn-block add-btn" data-id="${_id}">
                <button type="button" class="btn btn-success dropdown-toggle btn-block" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
                    Добавить
                </button>
                <div class="dropdown-menu">
                </div>
            </div>`
    }

    _updateDropDowns() {
        let _this = this;
        $(".add-btn > .dropdown-menu").each(function (data){
            let el = $(this);
            console.log(el);
            let _id = el.parent().data('id');
            el.html("").append(_this.dropdownGenerate(_id))
        });
        $('.dropdown-toggle').dropdown()
    }

    dropdownGenerate(_id) {
        function getA(pId, content) {
            return `<a class="dropdown-item add-processor" href="#" data-proc-id="${pId}" data-id="${_id}">${content}</a>`
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
    constructor (name, desc) {
        this.name = name;
        this.desc = desc;
    }

    render() {
        `<div class="card">
                <div class="card-block">
                    <h4 class="card-title">${this.name}</h4>
                    <p class="card-text">${this.desc}</p>
                </div>
                <ul class="list-group list-group-flush">
                    <li class="list-group-item">Cras justo odio</li>
                    <li class="list-group-item">Dapibus ac facilisis in</li>
                    <li class="list-group-item">Vestibulum at eros</li>
                </ul>
                <div class="card-block">
                    <a href="#" class="card-link text-success">Add after</a>
                    <a href="#" class="card-link text-primary">Calculate</a>
                    <a href="#" class="card-link text-danger">Delete</a>
                </div>
            </div>`
    }
}

function cardInit() {
    let procs = new Processors();
    procs.init().then(() => {console.log("Ok!")});
}

$(document).ready(() => {
    cardInit();
});