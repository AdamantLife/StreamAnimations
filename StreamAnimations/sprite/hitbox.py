## This Module
from StreamAnimations import utils
## Third Party
from PIL import Image, ImageOps

class Hitbox():
    def __init__(self, image) -> None:
        self.sprite = None
        self._image = image.convert("1")

    @property
    def image(self):
        return self._image
    @image.setter
    def image(self, value):
        self._image = value.convert("1")

    @property
    def topleft(self):
        return list(self.sprite.location)[:2]
        
    @property
    def bbox(self):
        x,y = self.topleft
        return x, y, x+self._image.width, y+self._image.height

class SquareHitbox(Hitbox):
    @classmethod
    def create_square_image(cls, width:int, height:int)-> Image.Image:
        return Image.new("1", (width, height), 0)

    def __init__(self, image, anchor = "tl") -> None:
        """
        anchors-
            tl: top left
            tr: top right
            bl: bottom left
            br: bottom right
            c: center
        """
        super().__init__(image)
        self.anchor = anchor

    @property
    def topleft(self):
        x,y,x1, y1 = self.sprite.bbox
        if self.anchor == "tl":
            return x, y
        elif self.anchor == "tr":
            return x1-self._image.width
        elif self.anchor == "bl":
            return x, y1-self._image.height
        elif self.anchor == "br":
            return x1-self._image.width, y-self._image.height
        elif self.anchor == "c":
            x3,y3 = (x1-x)//2, (y1 - y)//2
            return x3, y3
        raise AttributeError(f"Invalid Anchor: {self.anchor}")

class MaskedSquareHitbox(SquareHitbox):
    @property
    def image(self):
        simage = self.sprite.get_image()
        simage = ImageOps.invert(simage.point(lambda pixel: 255 if pixel > 0 else 0).convert("1", dither = Image.Dither.NONE))
        sbbox = self.sprite.bbox
        print(self.sprite, self)
        return utils.find_overlap_of_images(simage, self._image, sbbox, self.bbox)
