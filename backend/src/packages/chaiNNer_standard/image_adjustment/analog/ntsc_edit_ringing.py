from __future__ import annotations

import numpy as np
from nodes.impl.analog import ntsc

import navi
from nodes.impl.pil_utils     import convert_to_BGRA
from nodes.properties.inputs  import ImageInput, TextInput, BoolInput, SliderInput
from nodes.properties.outputs import ImageOutput, TextOutput
from nodes.utils.utils        import get_h_w_c
from nodes.groups             import Condition, if_group
import cv2
from sanic.log                import logger

from .. import adjustments_group
import json


@adjustments_group.register(
    schema_id   = "chainner:image:ntsc_edit_ringing",
    name        = "NTSC edit ringing",
    description = "",
    icon        = "MdVideocam",
    inputs=[
        TextInput("Settings"),
        BoolInput("Ringing", default=True ).with_id(1),
        if_group(Condition.bool(1, True))
        (
            SliderInput("Ringing power", minimum=2, maximum=7, default= 4)
        )

    ],
    outputs=[
        TextOutput("Settings"),
    ],
)

def ntsc_edit_ringing_node(jsonSettings  : str,
                           ringing       : bool,
                           ringingPower  : int) -> str:

    settings = json.loads(jsonSettings)

    settings["_ringing"]       = ringing
    settings["_ringing_power"] = ringingPower

    return json.dumps(settings)
