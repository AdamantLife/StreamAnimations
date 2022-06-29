from PIL import Image, ImageOps, ImageChops
import numpy as np

def import_spritesheet(filelocation: str)-> Image.Image:
    """ Imports a sprite sheet as an image """
    return Image.open(filelocation)

def split_spritesheet(spritesheet: Image.Image, rowheight: int, columnwidth:int)-> list:
    """ Splits a spritesheet into individual frames """
    output = list()
    for x in range(0, spritesheet.width, columnwidth):
        for y in range(0, spritesheet.height, rowheight):
            output.append(spritesheet.crop([x, y, x+columnwidth, y + rowheight]))
    return output

def mirror_spriteframe(sprite: Image.Image, mirror: str = "horizontal") -> Image.Image:
    """ Mirror an Individual Sprite Frame horizontally, vertically, or both """
    if mirror in ["horizontal", "both"]:
        sprite = ImageOps.mirror(sprite)
    if mirror in ["vertical", "both"]:
        sprite = ImageOps.flip(sprite)
    return sprite

def mirror_sprite(sprite: list):
    """ Call mirror_spriteframe on each sprite image in the given list """
    return [mirror_spriteframe(sp) for sp in sprite]

def scale_image(img: Image.Image, multiplier:int = 2) -> Image.Image:
    """ Scales an image by the given multiplier """
    multiplier = int(multiplier)
    if multiplier == 1: return img
    if multiplier < 1: raise ValueError("Image can only be scaled up")
    img = np.array(img)
    img = np.repeat(img, multiplier, axis = 1)
    img = np.repeat(img, multiplier, axis = 0 )
    return Image.fromarray(img)

def offset_boundingbox(bbox, deltax, deltay):
    return bbox[0] - deltax, bbox[1] - deltay, bbox[2] - deltax, bbox[3] - deltay

def find_overall_boundingbox(bbox1, bbox2):
    ax0, ay0, ax1, ay1 = bbox1
    bx0, by0, bx1, by1 = bbox2
    return min(ax0, bx0), min(ay0, by0), max(ax1,bx1), max(ay1, by1)

def find_overlap_of_images(image1, image2, bbox1 = None, bbox2 = None):
    if not bbox1: bbox1 = [0, 0, image1.width, image1.height]
    if not bbox2: bbox2 = [0, 0, image2.width, image2.height]
    deltax = min(bbox1[0], bbox2[0])
    deltay = min(bbox1[1], bbox2[1])
    bbox1 = offset_boundingbox(bbox1, deltax, deltay)
    bbox2 = offset_boundingbox(bbox2, deltax, deltay)
    overall = find_overall_boundingbox(bbox1, bbox2)
    print(bbox1, bbox2, overall)
    i1 = Image.new("1", (overall[2], overall[3]), color = 1)
    print(image1.size, bbox1)
    i1.paste(image1, bbox1)
    i2 = Image.new("1", (overall[2], overall[3]), color = 1)
    i2.paste(image2, bbox2)
    return ImageChops.difference(i1, i2)

if __name__ == "__main__":
    import pathlib
    spriteset = "Forward Walk"
    ROOT = pathlib.Path(__file__).resolve().parent.parent
    OUTDIR = ( ROOT / "output").resolve()
    OUTDIR.mkdir(exist_ok = True)
    sprites = import_spritesheet((ROOT / f"samples\{spriteset}.png").resolve())
    sprites = split_spritesheet(sprites, 32, 32)
    for i,sprite in enumerate(sprites):
        sprite.save( (OUTDIR / f"{spriteset}-{i}.png").resolve() )