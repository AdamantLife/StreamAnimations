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
    if multiplier is None: multiplier = 2
    multiplier = int(multiplier)
    if multiplier == 1: return img
    if multiplier < 1: raise ValueError("Image can only be scaled up")
    img = np.array(img)
    img = np.repeat(img, multiplier, axis = 1)
    img = np.repeat(img, multiplier, axis = 0 )
    return Image.fromarray(img)

def offset_boundingbox(bbox, deltax, deltay):
    return bbox[0] + deltax, bbox[1] + deltay, bbox[2] + deltax, bbox[3] + deltay

def find_overall_boundingbox(bbox1, bbox2):
    ax0, ay0, ax1, ay1 = bbox1
    bx0, by0, bx1, by1 = bbox2
    return min(ax0, bx0), min(ay0, by0), max(ax1,bx1), max(ay1, by1)

def check_boundingbox_overlap(box1, box2)-> bool:
    """ Checks if two boxes overlap """
    ax0, ay0, ax1, ay1 = box1
    bx0, by0, bx1, by1 = box2
    ## horizontal displacement
    if(ax0 >= bx1 or bx0 >= ax1 ): return False
    ## vertical displacement
    if(ay0 >= by1 or by0 >= ay1 ): return False
    return True
    

def find_overlap_of_images(image1, image2, bbox1 = None, bbox2 = None):
    """ Returns the overlapping area between two Bi-level images (mode="1" images) relative to the first image provided.

        image1 and image2 are the images to overlap.
        bbox1 and bbox2 relate to image1 and image2 respectively. If not provided
            a bbox will be defined as [0,0,image.width, image.height].
        The bboxes determine how the images are overlayed relative to each other.

        The returned Image is cropped to the bbox of image1 (bbox1).
    """
    if not bbox1: bbox1 = [0, 0, image1.width, image1.height]
    if not bbox2: bbox2 = [0, 0, image2.width, image2.height]
    xmin = min(bbox1[0], bbox2[0])
    ymin = min(bbox1[1], bbox2[1])
    deltax = 0 - xmin
    deltay = 0 - ymin
    bbox1 = offset_boundingbox(bbox1, deltax, deltay)
    bbox2 = offset_boundingbox(bbox2, deltax, deltay)
    overall = find_overall_boundingbox(bbox1, bbox2)
    i1 = Image.new("1", (overall[2], overall[3]), color = 0)
    i1.paste(image1, bbox1)
    i2 = Image.new("1", (overall[2], overall[3]), color = 0)
    i2.paste(image2, bbox2)
    return ImageChops.logical_and(i1, i2).crop(bbox1)

def opaque_mask(image: Image.Image):
    """ Converts the image to mode=1 (black and white) with the non-transparent portions converted to black """
    image = image.copy().convert("RGBA")
    pixels = image.load()
    for x in range(image.width):
        for y in range(image.height):
            ## If pixel's alpha channel is not fully transparent, make it white (1)
            if pixels[x,y][3] != 0:
                pixels[x,y] = (255, 255, 255, 255)
            ## Otherwise, make it black (0)
            else:
                pixels[x,y] = (0,0,0,0)
    return image.convert("1")

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