import Camera from './camera.js';
import { Events, getMousePos } from './event.js';
import { Vec2 } from './vec.js';


export class BaseGameObject {
    constructor () {
        let self = this;
        this.visible = true;
        this.object_id = Math.floor(Math.random() * 100000);
        this._name = 'base_game_object_' + this.object_id;
        this.canvasClick(function (arg) {self.clicked(arg);});
        this.z = 0;
    }

    draw(context) {
        console.log('implement draw');
    }

    clicked(mouse_pos) {
        console.log('implement clicked');
    }

    child_draw() {}

    canvasClick(clickedFunc) {
        let self = this;
        Events.handlers('canvas.click').set(
            self._name,
            function (data) {
                if (!self.handle_click)
                    return;
                let mouse_pos = getMousePos(data.this, data.event);
                if (
                    mouse_pos.x > self.pos.x
                    && mouse_pos.x < self.pos.x + self.size.x
                    && mouse_pos.y > self.pos.y
                    && mouse_pos.y < self.pos.y + self.size.y
                ) {
                    clickedFunc(mouse_pos);
                }
            },
        );
    }
}


export class GameObject extends BaseGameObject {
    constructor(pos, size, fillStyle) {
        super();
        this.pos = pos;
        this.size = size;
        this.fillStyle = fillStyle;
    }

    draw(context) {
        context.fillStyle = this.fillStyle;
        context.fillRect(
            this.pos.x,
            this.pos.y,
            this.pos.x + this.size.x,
            this.pos.y + this.size.y,
        );
    }
}


class Card extends BaseGameObject {
    constructor() {
        super();
        this.pos = new Vec2(0, 0);
        this.size = new Vec2(50, 50);
        this.visible = false;
        this.z = -10;
        this.movable = false;
        this.board_pos = null;
        this.name = 'card';
    }

    mousePosToBoard(pos) {
        return new Vec2(
            Math.min(
                Math.max(
                    Math.floor((pos.x - Camera.offset)/100),
                    0,
                ),
                7,
            )*100 + Camera.offset,
            Math.min(
                Math.max(
                    Math.floor((pos.y - Camera.offset)/100),
                    0,
                ),
                7,
            )*100 + Camera.offset,
        );
    }

    draw(context) {
        context.fillStyle = this.fillStyle;
        context.fillRect(
            this.pos.x,
            this.pos.y,
            this.size.x,
            this.size.y,
        );
    }

    copy() {
        return Object.create(
            Object.getPrototypeOf(this),
            Object.getOwnPropertyDescriptors(this)
        );
    }

    selectToMove(board_pos) {
        this.board_pos = board_pos;
    }

    validMove(newPos) {
        if (!this.board_pos)
            return false;
        if (Math.abs(this.board_pos.x - newPos.x) + Math.abs(this.board_pos.y - newPos.y) > 1)
            return false;
        return true;
    }
}


export class Virus extends Card {
    static fillStyle = '#f4f';

    constructor() {
        super();
        this.fillStyle = Virus.fillStyle;
        this.movable = true;
        this.name = 'virus';
    }
}


export class Link extends Card {
    static fillStyle = '#44f';

    constructor() {
        super();
        this.fillStyle = Link.fillStyle;
        this.movable = true;
        this.name = 'link';
    }
}

export class Enemy extends Card {
    static fillStyle = '#f44';

    constructor() {
        super();
        this.fillStyle = Enemy.fillStyle;
        this.visible = true;
    }
}


export class Exit extends Card {
    constructor() {
        super();
        this.visible = true;
        this.fillStyle = '#ff4';

    }

    static create_default_at(exit_class, poses) {
        Events.handlers('board.prepare').set('create_exits_'+exit_class.name, function (board) {
            for (let pos of poses) {
                let exit_card = new exit_class();
                exit_card.pos = board.toGlobal(pos);
                board.board[pos.x][pos.y] = exit_card;
            }
        });
    }
}

export class OwnExit extends Exit {
    constructor() {
        super();
    }
}

export class EnemyExit extends Exit {
    constructor() {
        super();
    }
}
