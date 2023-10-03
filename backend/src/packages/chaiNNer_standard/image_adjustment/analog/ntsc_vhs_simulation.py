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

from .. import adjustments_group
import time


@adjustments_group.register(
    schema_id   = "chainner:image:ntsc",
    name        = "NTSC VHS Simulation",
    description = "Simulate NTSC and VHS effects",
    icon        = "MdVideocam",
    inputs=[
        ImageInput(),

          BoolInput("Color bleed before",           default=True ).with_id( 1),
        if_group(Condition.bool( 1, True))
        (
            SliderInput("Bleed horiz",              minimum=0, maximum=8, default= 2),
            SliderInput("Bleed vertical",           minimum=0, maximum=8, default= 2)
        ),

          BoolInput("Composite in chroma lowpass" , default=True ).with_id( 4),
          BoolInput("Composite out chroma lowpass", default=True ).with_id( 5),
          BoolInput("Composite out chroma tv",      default=True ).with_id( 6),

        SliderInput("Composite preemphasis",        minimum=0, maximum=80, default= 20),
        SliderInput("Video noise",                  minimum=0, maximum=4200, default= 2),

          BoolInput("VHS head switching",           default=False).with_id( 9),

        SliderInput("Chroma noise",                 minimum=0, maximum=16384, default= 2),
        SliderInput("Chroma phase_noise",           minimum=0, maximum=50, default= 2),
          BoolInput("Emulating VHS",                default=True ).with_id(12),
        SliderInput("Video chroma loss",            minimum=0, maximum=50000, default=10),
          BoolInput("Ringing",                      default=True ).with_id(14),
        if_group(Condition.bool(14, True))
        (
            SliderInput("Ringing power",            minimum=2, maximum=7, default= 4)
        )
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

def ntsc_vhs_simulation_node( img                             : np.ndarray,
                              color_bleed_before              : bool,
                              color_bleed_horiz               : int,
                              color_bleed_vert                : int,
                              composite_in_chroma_lowpass     : bool,
                              composite_out_chroma_lowpass    : bool,
                              composite_out_chroma_lowpass_tv : bool,
                              composite_preemphasis           : int,
                              video_noise                     : int,
                              vhs_head_switching              : bool,
                              video_chroma_noise              : int,
                              video_chroma_phase_noise        : int,
                              emulating_vhs                   : bool,
                              video_chroma_loss               : int,
                              ringing                         : bool,
                              ringing_power                   : int,
                            ) -> np.ndarray:

    #my_ntsc = ntsc.random_ntsc(int(time.time()))
    #my_ntsc = ntsc.Ntsc()
    my_ntsc = ntsc.non_random_ntsc()

    my_ntsc._color_bleed_before                 = color_bleed_before
    my_ntsc._color_bleed_horiz                  = color_bleed_horiz
    my_ntsc._color_bleed_vert                   = color_bleed_vert
    my_ntsc._composite_in_chroma_lowpass        = composite_in_chroma_lowpass
    my_ntsc._composite_out_chroma_lowpass       = composite_out_chroma_lowpass
    my_ntsc._composite_out_chroma_lowpass_lite  = composite_out_chroma_lowpass_tv
    my_ntsc._composite_preemphasis              = composite_preemphasis * 0.1
    my_ntsc._video_noise                        = video_noise
    my_ntsc._vhs_head_switching                 = vhs_head_switching
    my_ntsc._vhs_head_switching_point           = 1.0 - (4.5 + 0.01) / 262.5
    my_ntsc._vhs_head_switching_phase           = (1.0 - 0.01) / 262.5
    my_ntsc._vhs_head_switching_phase_noise     = 1.0 / 500 / 262.5
    my_ntsc._video_chroma_noise                 = video_chroma_noise
    my_ntsc._video_chroma_phase_noise           = video_chroma_phase_noise
    my_ntsc._emulating_vhs                      = emulating_vhs
    my_ntsc._video_chroma_loss                  = video_chroma_loss
    my_ntsc._ringing                            = ringing
    my_ntsc._ringing_power                      = ringing_power

    height, width, depth = img.shape
    new_height = 600
    new_width  = int(width * (float(new_height) / height) ) & 0xFFFE    # Fixme: Seems very sensitive to the exact width. Doesn't like odd numbers. And other numbers?

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
