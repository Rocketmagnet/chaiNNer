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
    schema_id   = "chainner:image:ntsc_prest_vhs",
    name        = "NTSC VHS Preset Good quality",
    description = "",
    icon        = "MdVideocam",
    inputs=[
    ],
    outputs=[
        TextOutput("Settings"),
    ],
)

def ntsc_vhs_preset_good_quality_node() -> str:
    settings = {}
    settings["_color_bleed_before"]              = 0                                             # Start with some default values
    settings["_color_bleed_horiz"]               = 0
    settings["_color_bleed_vert"]                = 0
    settings["_composite_in_chroma_lowpass"]     = 0
    settings["_composite_out_chroma_lowpass"]    = 0
    settings["_composite_out_chroma_lowpass_tv"] = 0
    settings["_composite_preemphasis * 0.1"]     = 0
    settings["_video_noise"]                     = 0
    settings["_vhs_head_switching"]              = 0
    settings["_video_chroma_noise"]              = 0
    settings["_video_chroma_phase_noise"]        = 0
    settings["_emulating_vhs"]                   = 0
    settings["_video_chroma_loss"]               = 0
    settings["_composite_out_chroma_lowpass"]    = 0
    settings["_ringing"]                         = 0
    settings["_ringing_power"]                   = 0

    return json.dumps(settings)
