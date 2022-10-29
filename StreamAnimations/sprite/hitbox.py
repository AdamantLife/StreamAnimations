## This Module
from StreamAnimations import utils
## Builtin
from collections import OrderedDict
## Third Party
from PIL import Image, ImageOps

def create_rect_hitbox_image(width:int, height:int)-> Image.Image:
    """ Creates a rectangular image to be used in a hitbox """
    return Image.new("1", (width, height), 255)

class Hitbox():
    def __init__(self, image, sprite= None) -> None:
        self.sprite = sprite
        self._image = image.convert("1")

    @property
    def image(self):
        return self._image
    @image.setter
    def image(self, value):
        self._image = value.convert("1")

    @property
    def topleft(self):
        return tuple(self.sprite.location)[:2]
        
    @property
    def bbox(self):
        x,y = self.topleft
        return x, y, x+self._image.width, y+self._image.height

class AnchorMixin():
    """
        anchors-
            anchors are defined in terms of vertical and horizontal alignment:
                t, c, b: top, center, bottom
                l, c, r: left, center, right

            Center can be omitted: e.g.- "t", "l", and "" are all valid alignments (representing "tc", "cl", and "cc")

            The anchor point is relative to both the mask and its sprite: so "tl" means the top-left of the mask
                is anchored to the top-left of the sprite, "cc" means the center of the mask is anchored to the
                center of the sprite, etc. 
        """
    VERTICALKEYS = ["t","b"]
    HORIZONTALKEYS = ["l","r"]

    @classmethod
    def standardize_anchor(cls, anchor):
        """ Standardizes the anchor code into a length-2 string """
        anchor = anchor.lower()

        v = [vkey for vkey in AnchorMixin.VERTICALKEYS if vkey in anchor]
        ## Multiple Vertical Anchors
        if len(v) > 1: raise ValueError(f"Invalid Anchor: {anchor}")
        ## No (non-center) Vertical Anchors
        elif not v: v = "c"
        ## One valid Vertical Anchor
        else: v = v[0]

        h = [hkey for hkey in AnchorMixin.HORIZONTALKEYS if hkey in anchor]
        ## Multiple Horizontal Anchors
        if len(h) > 1: raise ValueError(f"Invalid Anchor: {anchor}")
        ## No (non-center) Horizontal Anchors
        elif not h: h = "c"
        ## One valid Horizontal Anchor
        else: h = h[0]

        return v+h

    @property
    def topleft(self):
        v,h = self.standardize_anchor(self.anchor)
        sx,sy,sx2,sy2 = self.sprite.bbox
        sw,sh = (sx2 - sx), (sy2 - sy)
        x,y,mw,mh = 0,0, *self._image.size
        
        if v == "t":
            ## top is aligned with top of sprite
            y = sy
        elif v == "c":
            ## vcenter is midpoint of sprite (sy + half height) offset by half height of mask
            y = sy + sh//2 - mh//2
        elif v == "b":
            ## Topleft from bottom is bottom offset by height of mask
            y = sy2 - mh
        else:
            raise RuntimeError(f"Anchor Code not programmed: {v}")

        if h == "l":
            ## left is aligned with left of sprite
            x = sx
        elif h == "c":
            ## hcenter is midpoint sprite (sx + half width) offset by half width of mask
            x = sx + sw//2 - mw//2
        elif h == "r":
            ## Topleft from right is right offset by width of mask
            x = sx2 - mw
        else:
            raise RuntimeError(f"Anchor Code not programed: {h}")
        
        return x,y

        


class AnchoredHitbox(AnchorMixin, Hitbox):
    def __init__(self, *args, anchor = "tl", **kw) -> None:
        super().__init__(*args, **kw)
        self.anchor = anchor
    

class MaskedHitbox(AnchoredHitbox):
    @property
    def image(self):
        simage = self.sprite.get_image()
        simage = utils.opaque_mask(simage)
        sbbox = self.sprite.bbox
        return utils.find_overlap_of_images(self._image, simage, self.bbox, sbbox)
