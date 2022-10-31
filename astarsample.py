from StreamAnimations.engine.renderers.gif import GifRenderer
from StreamAnimations.canvases import SinglePageCanvas
from StreamAnimations import sprite
from StreamAnimations.engine.ai.algorithms import astar
from StreamAnimations.engine.ai.heuristics.distances import squaredistance, lineardistance
from StreamAnimations.engine.utils import collision_stop_rule
from StreamAnimations.systems import twodimensional

## Third Party
from PIL import Image

## Builtin
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
OUTDIR = ( ROOT / "output").resolve()
OUTDIR.mkdir(exist_ok = True)


canvas = SinglePageCanvas((10,10), steplength=1)
renderer = GifRenderer(canvas, background = Image.new("RGBA",(10,10), (173, 216, 230,255)))
canvas.add_listener("movement", collision_stop_rule)
character = Image.new(mode= "RGBA",size= (1,1), color= (255,0,0))
character = {direction:[character] for direction in twodimensional.TwoDimensional_4Way.directions()}
character = twodimensional.Sprite2D(character, hitboxes = (1,1))
wall = Image.new(mode="RGBA", size = (1,1), color = (0,0,0))


# Map One
# MAP=1
# start = (0,9)
# walls = [sprite.StationarySprite({"idle":wall}, hitboxes = (1,1)) for w in range(3)]
# canvas.add_sprite(walls[0], (6,3))
# canvas.add_sprite(walls[1], (7,3))
# canvas.add_sprite(walls[2], (7,4))
# goal = (9,0)

## Map Two
MAP=2
for coord in [
    ## First Column (empty)
    ## Second Column
    (1,0), (1,1), (1,2), (1,4), (1,5), (1,7), (1,8), (1,9),
    ## Third Column
    (2,2),(2,4),(2,7),
    ## Fourth Column
    (3,2), (3,4), (3,6), (3,7),
    ## Fifth Column
    (4,4), (4,9), 
    ## Sixth Column
    (5,0), (5,1), (5,2), (5,3), (5,4), (5,6), (5,7), (5,8), (5,9),
    ## Seventh Column
    (6,0),
    ## Eigth Column
    (7,0), (7,2), (7,3), (7,4), (7,5), (7,6), (7,7), (7,8), 
    ## Ninth Column
    (8,0), (8,2), (8,4), (8,8), 
    ## Tenth Column
    (9,0), (9,2), (9,6), 
]:
    wallsprite = sprite.StationarySprite({"idle":wall}, hitboxes = (1,1))
    canvas.add_sprite(wallsprite, coord)
start = (2,0)
goal = (8,3)

## Add character
canvas.add_sprite(character, start)

## Get astar path
characterpath = astar(
    character.location,         ## Start Location
    goal,                       ## Goal
    heuristic= lineardistance,  ## Heuristic
    adjacent = lambda start:    ## Find adjacent
        [(character.cs.determine_offset_coordinate(dire, start), 1)    ## create a node with coordinate offset from the start postion with cost 1
         for dire in character.valid_moves(canvas, start)]          ## For each direction in valid_moves (returns direction names)
         )

##  Renderer initial frame
with renderer.frame(): pass

## Convert path to rendered frames (animate)
for coordinate in characterpath:
    with renderer.frame() as f:
        offset = character.cs.calculate_offset(coordinate, character.location)
        ## No movement, typically this is the start coordinate
        if not any(coord for coord in offset): continue
        f.move_sprite(character, offset = offset)

## Save
renderer.save((OUTDIR/f"astar-map{MAP}.gif").resolve(), 10, scale = 5)
