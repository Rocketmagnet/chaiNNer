from __future__ import annotations

import numpy as np
from nodes.impl.analog import ntsc

import navi
from nodes.impl.pil_utils     import convert_to_BGRA
from nodes.properties.inputs  import ImageInput, TextInput, BoolInput, SliderInput
from nodes.properties.outputs import ImageOutput
from nodes.utils.utils        import get_h_w_c
from nodes.groups import Condition, if_group
import cv2
from sanic.log import logger

from .. import adjustments_group
import time


@adjustments_group.register(
    schema_id="chainner:image:ntsc",
    name="NTSC VHS Simulation",
    description="Simulate NTSC and VHS effects",
    icon="MdOutlineOpacity",
    inputs=[
        ImageInput(),
        BoolInput("color_bleed_before"          , default=True ).with_id( 1),
        if_group(Condition.bool( 1, True))(SliderInput("Horiz",    minimum=0, maximum=8, default= 2),
                                           SliderInput("Vertical", minimum=0, maximum=8, default= 2)  ),

          BoolInput("composite_in_chroma_lowpass" , default=True ).with_id( 4),
          BoolInput("composite_out_chroma_lowpass", default=True ).with_id( 5),
          BoolInput("composite_out_chroma_tv",      default=True ).with_id( 6),

        SliderInput("composite_preemphasis",        minimum=0, maximum=80, default= 20),
        SliderInput("video_noise",                  minimum=0, maximum=4200, default= 2),

          BoolInput("vhs_head_switching",           default=False).with_id( 9),
          BoolInput("nocolor_subcarrier",           default=False ).with_id(10),

        SliderInput("video_chroma_noise",           minimum=0, maximum=16384, default= 2),
        SliderInput("video_chroma_phase_noise",     minimum=0, maximum=50, default= 2),
          BoolInput("emulating_vhs",                default=True ).with_id(13),
        SliderInput("video_chroma_loss",            minimum=0, maximum=50000, default=10),
          BoolInput("ringing",                      default=True ).with_id(15),
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

def ntsc_vhs_simulation_node(  img                      : np.ndarray,
                color_bleed_before                      : bool,
                color_bleed_horiz                       : int,
                color_bleed_vert                        : int,

                composite_in_chroma_lowpass             : bool,
                composite_out_chroma_lowpass            : bool,
                composite_out_chroma_lowpass_tv         : bool,

                composite_preemphasis                   : int,

                video_noise                             : int,
                vhs_head_switching                      : bool,

                nocolor_subcarrier                      : bool,
                video_chroma_noise                      : int,
                video_chroma_phase_noise                : int,

                emulating_vhs                           : bool,

                video_chroma_loss                       : int,
                ringing                                 : bool,
                ) -> np.ndarray:

    #my_ntsc = ntsc.random_ntsc(int(time.time()))
    #my_ntsc = ntsc.Ntsc()
    my_ntsc = ntsc.non_random_ntsc()

    setattr(my_ntsc, "_color_bleed_before"             , color_bleed_before              )
    setattr(my_ntsc, "_color_bleed_horiz"              , color_bleed_horiz               )
    setattr(my_ntsc, "_color_bleed_vert"               , color_bleed_vert                )

    setattr(my_ntsc, "_composite_in_chroma_lowpass"    , composite_in_chroma_lowpass     )
    setattr(my_ntsc, "_composite_out_chroma_lowpass"   , composite_out_chroma_lowpass    )
    setattr(my_ntsc, "_composite_out_chroma_lowpass_tv", composite_out_chroma_lowpass_tv )

    setattr(my_ntsc, "_composite_preemphasis"          , composite_preemphasis * 0.1     )

    setattr(my_ntsc, "_video_noise"                    , video_noise                     )
    setattr(my_ntsc, "_vhs_head_switching"             , vhs_head_switching              )
    setattr(my_ntsc, "_vhs_head_switching_point"       , 1.0 - (4.5 + 0.01) / 262.5      )
    setattr(my_ntsc, "_vhs_head_switching_phase"       , (1.0 - 0.01) / 262.5            )
    setattr(my_ntsc, "_vhs_head_switching_phase_noise" , 1.0 / 500 / 262.5               )

    setattr(my_ntsc, "_video_chroma_noise"             , video_chroma_noise              )
    setattr(my_ntsc, "_video_chroma_phase_noise"       , video_chroma_phase_noise        )
    setattr(my_ntsc, "_emulating_vhs"                  , emulating_vhs                   )
    setattr(my_ntsc, "_video_chroma_loss"              , video_chroma_loss               )
    setattr(my_ntsc, "_composite_out_chroma_lowpass"   , composite_out_chroma_lowpass    )
    setattr(my_ntsc, "_ringing"                        , ringing                         )

    height, width, depth = img.shape
    logger.info("height, width = " + str(height) + " " + str(width))
    new_height = 600
    new_width  = 900 #int(width * (float(new_height) / height) )

    logger.info("new_height, new_width = " + str(new_height) + " " + str(new_width))
    new_size = (new_width, new_height)
    logger.info("new_size = " + str(new_size))

    resized_src_img = cv2.resize(img, new_size, interpolation=cv2.INTER_AREA)
    resized_src_img *= 255.0

    dst_img = np.zeros_like(resized_src_img)

    logger.info("resized_src_img = " + str(resized_src_img.shape))
    logger.info("dst_img         = " + str(        dst_img.shape))

    my_ntsc.composite_layer(dst_img, resized_src_img, 1, 2)
    dst_img *= (1.0/255.0)

    #src_img = np.copy(img)
    #src_img *= 255.0
    #dst_img = np.zeros_like(src_img)
    #logger.info("src_img = " + str(src_img.shape))
    #logger.info("dst_img = " + str(dst_img.shape))
    #my_ntsc.composite_layer(dst_img, src_img, 1, 2)
    #dst_img *= (1.0/255.0)

    return dst_img
