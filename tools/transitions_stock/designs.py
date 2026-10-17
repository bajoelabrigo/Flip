"""Every Stock transition, family by family (see kit.Family). Ids are unique across the catalog."""

from __future__ import annotations

import fam_glitch
import fam_zoom
import fam_shapes
import fam_light
import fam_liquid
import fam_3d
import fam_fun
import fam_youtuber

FAMILIES = [*fam_glitch.FAMILIES, *fam_zoom.FAMILIES, *fam_shapes.FAMILIES, *fam_light.FAMILIES, *fam_liquid.FAMILIES, *fam_3d.FAMILIES, *fam_fun.FAMILIES,
            *fam_youtuber.FAMILIES]

ALL = [(f, v) for f in FAMILIES for v in f.variants]
_ids = [v.id for _, v in ALL]
assert len(_ids) == len(set(_ids)), "duplicate transition ids"
