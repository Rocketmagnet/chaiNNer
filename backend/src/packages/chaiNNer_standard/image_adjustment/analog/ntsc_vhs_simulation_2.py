from __future__ import annotations

import numpy as np
from nodes.impl.analog import ntsc

import navi
from nodes.impl.pil_utils     import convert_to_BGRA
from nodes.properties.inputs  import ImageInput, TextInput, BoolInput, SliderInput
from nodes.properties.outputs import ImageOutput
from nodes.utils.utils        import get_h_w_c
from nodes.groups             import Condition, if_group
import cv2
from sanic.log                import logger
import json

from .. import adjustments_group
import time


@adjustments_group.register(
    schema_id   = "chainner:image:ntsc2",
    name        = "NTSC VHS Simulation 2",
    description = "Simulate NTSC and VHS effects with JSON preset",
    icon        = "MdVideocam",
    inputs=[
        ImageInput(),
          TextInput("Settings")
    ],
    outputs=[
        ImageOutput(
            image_type=navi.Image(
            ),
            channels=3,
            assume_normalized=True,
        )
    ],
)

def ntsc_vhs_simulation_2_node( img          : np.ndarray,
                              jsonSettings   : str,
                            ) -> np.ndarray:


    my_ntsc = ntsc.non_random_ntsc()

    my_ntsc._color_bleed_before                 = True
    my_ntsc._color_bleed_horiz                  = 2
    my_ntsc._color_bleed_vert                   = 2
    my_ntsc._composite_in_chroma_lowpass        = True
    my_ntsc._composite_out_chroma_lowpass       = True
    my_ntsc._composite_out_chroma_lowpass_lite  = True
    my_ntsc._composite_preemphasis              = 2
    my_ntsc._video_noise                        = 2
    my_ntsc._vhs_head_switching                 = False
    my_ntsc._vhs_head_switching_point           = 1.0 - (4.5 + 0.01) / 262.5
    my_ntsc._vhs_head_switching_phase           = (1.0 - 0.01) / 262.5
    my_ntsc._vhs_head_switching_phase_noise     = 1.0 / 500 / 262.5
    my_ntsc._video_chroma_noise                 = 2
    my_ntsc._video_chroma_phase_noise           = 2
    my_ntsc._emulating_vhs                      = True
    my_ntsc._video_chroma_loss                  = 10
    my_ntsc._ringing                            = True
    my_ntsc._ringing_power                      = 4

    settings = {}
    settings["_color_bleed_before"]              = True                                             # Start with some default values
    settings["_color_bleed_horiz"]               = 2
    settings["_color_bleed_vert"]                = 2
    settings["_composite_in_chroma_lowpass"]     = True
    settings["_composite_out_chroma_lowpass"]    = True
    settings["_composite_out_chroma_lowpass_tv"] = True
    settings["_composite_preemphasis * 0.1"]     = 20
    settings["_video_noise"]                     = 2
    settings["_vhs_head_switching"]              = False
    settings["_video_chroma_noise"]              = False
    settings["_video_chroma_phase_noise"]        = False
    settings["_emulating_vhs"]                   = True
    settings["_video_chroma_loss"]               = 10
    settings["_ringing"]                         = 0
    settings["_ringing_power"]                   = 2


    settings = settings | json.loads(jsonSettings)                                              # Then merge in the settings that have come in externally

    my_ntsc._video_chroma_loss = settings["_video_chroma_loss"]
    my_ntsc._ringing           = settings["_ringing"]
    my_ntsc._ringing_power     = settings["_ringing_power"]


    #for parameter_name, value in settings.items():                                              # and write them to the NTSC object
    #    setattr(my_ntsc, parameter_name, value)

    height, width, depth = img.shape
    new_height = 600
    new_width  = int(width * (float(new_height) / height) ) & 0xFFFE                            # Fixme: Seems very sensitive to the exact width. Doesn't like odd numbers. And other numbers?
    new_size = (new_width, new_height)
    resized_src_img = cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)
    resized_src_img *= 255.0

    dst_img_0 = np.zeros_like(resized_src_img)
    dst_img_1 = np.zeros_like(resized_src_img)
    my_ntsc.composite_layer(dst_img_0, resized_src_img, field=0, fieldno=0)
    my_ntsc.composite_layer(dst_img_1, resized_src_img, field=1, fieldno=1)
    dst_img_0 += dst_img_1
    dst_img_0 *= (1.0/255.0)

    #_ = my_ntsc.composite_layer(dst_img_0, resized_src_img, field=0, fieldno=1)
    #ntsc_out_image = cv2.convertScaleAbs(_)
    #ntsc_out_image[1:-1:2] = ntsc_out_image[0:-2:2] / 2 + ntsc_out_image[2::2] / 2
    #ntsc_out_image *= (1.0/255.0)

    return dst_img_0
