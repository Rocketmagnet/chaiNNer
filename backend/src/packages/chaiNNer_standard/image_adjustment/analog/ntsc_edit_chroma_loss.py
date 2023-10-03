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
    schema_id   = "chainner:image:ntsc_edit_chroma_loss",
    name        = "NTSC edit chroma loss",
    description = "",
    icon        = "MdVideocam",
    inputs=[
        TextInput("Settings"),
        SliderInput("Chroma loss", minimum=0, maximum=50000, default=10)
    ],
    outputs=[
        TextOutput("Settings"),
    ],
)

def ntsc_edit_chroma_loss_node(jsonSettings  : str,
                               chromaLoss    : int) -> str:

    #logger.info("In:")
    #logger.info("chroma loss = " + str(chromaLoss))
    #logger.info(jsonSettings)

    settings = json.loads(jsonSettings)

    settings["_video_chroma_loss"] = chromaLoss

    modifiedSettings = json.dumps(settings)

    #logger.info("Out:")
    #logger.info(modifiedSettings)

    return modifiedSettings
