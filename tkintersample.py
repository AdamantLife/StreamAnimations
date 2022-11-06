## This Module
from StreamAnimations import utils
from StreamAnimations.sprite import hitbox
from StreamAnimations.canvases import SinglePageCanvas
from StreamAnimations.engine import utils as engineutils
from StreamAnimations.systems import twodimensional
from StreamAnimations import engine
from StreamAnimations.engine import entities
from StreamAnimations.engine.ai import algorithms
from StreamAnimations.engine.ai.heuristics import distances

## Renderer
from StreamAnimations.engine.renderers.tkinter import TkinterCanvas

## Buitlin
import tkinter as tk
import pathlib
import random

## Third Party
import PIL.Image, PIL.ImageTk

ROOT = pathlib.Path(__file__).resolve().parent
SAMPLEDIR = (ROOT / "samples").resolve()
SPRITESIZE = 32
CANVASSIZE = 1920, 1080
BASEHEIGHT = 10
FRAMERATE = 16
SCALE = 5
MOTIVATIONTIMER = 1000//10


def load_character():
    up, down, right = utils.import_spritesheet((SAMPLEDIR / "Walk Up.png").resolve()), \
        utils.import_spritesheet((SAMPLEDIR / "Walk Down.png").resolve()), \
            utils.import_spritesheet((SAMPLEDIR / "Walk Right.png"))
    directions = dict(up = utils.split_spritesheet(up, SPRITESIZE, SPRITESIZE),
        down = utils.split_spritesheet(down, SPRITESIZE, SPRITESIZE),
        right = utils.split_spritesheet(right, SPRITESIZE, SPRITESIZE)
        )
    directions["left"] = utils.mirror_sprite(directions['right'])

    me = twodimensional.MobileSprite(hitboxes = [], animations = dict(idle=directions['down'][0],**directions))
    mehitbox = hitbox.MaskedHitbox(hitbox.create_rect_hitbox_image(me.get_image().width, BASEHEIGHT),anchor="bl")
    me.add_hitbox(mehitbox)

    me.location = (50, 20)
    return me
    

def load_printer():
    frames = []
    for zlevel in range(1,6):
        sheet = utils.import_spritesheet( (SAMPLEDIR / f"Prusa Z{zlevel}.png").resolve())
        frames.extend(utils.split_spritesheet(sheet, SPRITESIZE, SPRITESIZE))
    animations =  {"idle": frames[0], "printing": frames}

    printer = twodimensional.StationarySprite(animations=animations)
    printer.set_animation("printing")
    printerhitbox = hitbox.MaskedHitbox(hitbox.create_rect_hitbox_image(printer.get_image().width, BASEHEIGHT//2), anchor="bl")
    printer.add_hitbox(printerhitbox)

    printer.location = (80,80)
    return printer

def load_desk():
    animations= {"idle":utils.split_spritesheet(utils.import_spritesheet( (SAMPLEDIR / "Desk-1.png").resolve()), SPRITESIZE, 45)}
    desk = twodimensional.StationarySprite(animations= animations)
    # deskhitbox = hitbox.MaskedHitbox(hitbox.create_rect_hitbox_image(desk.get_image().width, BASEHEIGHT),anchor="bl")
    # desk.add_hitbox(deskhitbox)
    textanimations = {"idle": utils.split_spritesheet(utils.import_spritesheet( (SAMPLEDIR / "stream.png").resolve() ), SPRITESIZE, 21)}
    monitortext = twodimensional.CosmeticSprite(animations= textanimations, offset = (12,12), parent = desk)

    desk.location = (50, 50)

    return [desk, monitortext]

def single_loop_animation(sprite, canvas):
    def callback():
        if sprite.animations.is_last_frame():
            sprite.animations.pause()
            return True
        sprite.animations.cycle()
        return True
    return callback
SingleLoopAnimation = engine.SpriteAction(single_loop_animation)

def collect_from_printer(sprite, canvas):
    sprite._path_to_printer = []
    def callback():
        if not printer.animations.is_paused:
            return False
        if not sprite._path_to_printer:
            steplength = canvas.steplength
            ## Hide printer so we don't trigger collisions with it
            zindex = printer.zindex
            printer.zindex = -1
            path = algorithms.astar(sprite.location, ## Start
                printer.location, ## Target
                lambda start: [(sprite.cs.determine_offset_coordinate(dire, start, steplength = steplength), 1) for dire in sprite.valid_moves(canvas, start)], ## Adjacent node and cost
                distances.squaredistance) ## Heuristic
            ## Restore printer
            printer.zindex = zindex
            sprite._path_to_printer.extend(path)
            ## Remove initial square
            sprite._path_to_printer.pop(0)
        step = sprite._path_to_printer.pop(0)
        offset = sprite.cs.calculate_offset(step, sprite.location)
        initialcoord = sprite.location
        canvas.move_sprite(sprite, offset = offset)
        if sprite.location == initialcoord:
            sprite._path_to_printer.clear()
        return True
    return callback
CollectFromPrinter = engine.SpriteAction(collect_from_printer)

def unpause_printer(event):
    """ Collision callback for """
    ## sprite is not in a virtual state (move algo)
    ## the sprite is me
    ## the sprite being collided with is the printer
    ## and the printer is paused
    if not event.sprite.virtual and event.sprite == me and event.collisionhitbox.sprite == printer and printer.animations.is_paused:
        printer.animations.unpause()
        printer.animations.cycle()
        printcounter.value += 1

def wander(sprite, canvas):
    sprite.wander_history = []
    def callback():
        directions = list(sprite.valid_moves(canvas))
        if(not directions):
            return False
        new_direction = None
        if not sprite.wander_history or len(directions) == 1:
            new_direction = random.choice(directions)
        else:
            if sprite.wander_history[0] in directions and random.random() < max(90-len(sprite.wander_history), 0)/100:
                new_direction = sprite.wander_history[0]
            else:
                new_direction = random.choice(directions)
        if sprite.wander_history and new_direction != sprite.wander_history[0]: sprite.wander_history = []
        sprite.wander_history.append(new_direction)
        canvas.move_sprite(sprite, direction =new_direction)
        return True
    return callback
Wander = engine.SpriteAction(wander)

def recharge(sprite, canvas):
    sprite._path_to_desk = []
    def callback():
        if not printer.animations.is_paused:
            return False
        if not sprite._path_to_desk:
            steplength = canvas.steplength
            path = algorithms.astar(sprite.location, ## Start
                DESKRALLYPOINT, ## Target
                lambda start: [(sprite.cs.determine_offset_coordinate(dire, start, steplength = steplength), 1) for dire in sprite.valid_moves(canvas, start)], ## Adjacent node and cost
                distances.squaredistance) ## Heuristic
            path = list(path) 
            print(path)
            sprite._path_to_desk.extend(path)
            ## Remove initial square
            sprite._path_to_desk.pop(0)
        step = sprite._path_to_desk.pop(0)
        offset = sprite.cs.calculate_offset(step, sprite.location)
        initialcoord = sprite.location
        canvas.move_sprite(sprite, offset = offset)
        if sprite.location == initialcoord:
            sprite._path_to_desk.clear()
        return True
    return callback
Recharge = engine.SpriteAction(recharge)


CollectHeuristic = lambda: 100_000 if printer.animations.is_paused else 0
WanderHeuristic = lambda: 10
RechargeHeuristic = lambda: 100_000_000 if (motivationbar.value == 0 or motivationbar.charging) else 0

## Setup Canvas
canvas = SinglePageCanvas(CANVASSIZE, SPRITESIZE // 4)
## When the me sprite collides with the printer when it is paused, unpause the printer
## (does not prevent the collision and needs to be triggered before collision_stop_rule)
canvas.add_listener("movement", engineutils.collision_callback_rule(unpause_printer))
## Prevent all collisions
canvas.add_listener("movement", engineutils.collision_stop_rule)

## Setup Sprites
sprites = []
me = load_character()
sprites.append(me)
printer = load_printer()
sprites.append(printer)
desk, screen = load_desk()
sprites.append(desk)
sprites.append(screen)

deskimagesize = desk.get_image().size
DESKRALLYPOINT = desk.cs.round_to_steplength((
    (desk.location[0]+deskimagesize[0]//2), (desk.location[1]+deskimagesize[1]+10))
    , steplength= canvas.steplength)

print(DESKRALLYPOINT)

printcounter = twodimensional.CounterHUD(cmin = 0, label = "Prints Collected: ", fontoptions=dict(size=50, fill=(0,0,0,255)))
printcounter.location = (0,0)
sprites.append(printcounter)
motivationbar = twodimensional.BarHUD(label = "HP", fontoptions=dict(size=50, fill=(0,0,0,255)), 
    labelposition="inside", start= 100, size = (300, 50), background=(255, 255, 255, 255), border = True)
motivationbar.location = (printcounter.get_image().width//SCALE + 100, 0)
motivationbar.charging = False
sprites.append(motivationbar)

## Add sprites to Canvas
for sp in sprites: canvas.add_sprite(sp)

## Add AI
entitylist = []
mePriorityQueue = (
    (CollectHeuristic, CollectFromPrinter(me, canvas)),
    (WanderHeuristic, Wander(me, canvas)),
    (RechargeHeuristic, Recharge(me, canvas))
)
meEntity = entities.PriorityAI(0, priority_queue=mePriorityQueue)
meEntity.sprite = me
entitylist.append(meEntity)
printerEntity = entities.ActionEntity(1, action = SingleLoopAnimation(printer, canvas))
printerEntity.sprite = printer
entitylist.append(printerEntity)

## Setup Renderer
root = tk.Tk()
tkcanvas = tk.Canvas(root, width= CANVASSIZE[0], height = CANVASSIZE[1])
tkcanvas.pack()

background = PIL.Image.new("RGB", CANVASSIZE, (219, 240, 250))

renderer = TkinterCanvas(canvas, tkcanvas, framerate=FRAMERATE, scale = SCALE, background = background)

def loop():
    idles = [sprite for sprite in sprites if not sprite.animations.is_paused]
    for entity in entitylist:
        result = entity.get_action()()
        ## Result means the entity is active, so not idle
        ## entity is tied to a sprite
        ## sprite is an idle sprite that can be animated (not idle)
        if result and getattr(entity, "sprite", None) and entity.sprite in idles:
            idles.remove(entity.sprite)
    canvas.animate_idlesprites(idles)
    renderer.render(scale = renderer.scale, background = renderer.background)
    root.after(1000//FRAMERATE, loop)

def motivationTimer():
    if me.location == DESKRALLYPOINT:
        motivationbar.charging = True
        motivationbar.value = min(motivationbar.max, motivationbar.value+1)
    else:
        motivationbar.charging = False
        motivationbar.value = max(0, motivationbar.value - 1)
    root.after(MOTIVATIONTIMER, motivationTimer)


renderer.render(scale = renderer.scale, background = renderer.background)
root.after(1000//FRAMERATE, loop)
root.after(MOTIVATIONTIMER, motivationTimer)
root.mainloop()