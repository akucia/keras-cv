# Copyright 2022 The KerasCV Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import warnings

import tensorflow as tf

from keras_cv import bounding_box
from keras_cv.layers.preprocessing.base_image_augmentation_layer import (
    BaseImageAugmentationLayer,
)
from keras_cv.utils import preprocessing


@tf.keras.utils.register_keras_serializable(package="keras_cv")
class RandomTranslation(BaseImageAugmentationLayer):
    """A preprocessing layer which randomly flips images during training.

    This layer will flip the images horizontally and or vertically based on the
    `mode` attribute. During inference time, the output will be identical to
    input. Call the layer with `training=True` to flip the input.

    Input shape:
      3D (unbatched) or 4D (batched) tensor with shape:
      `(..., height, width, channels)`, in `"channels_last"` format.

    Output shape:
      3D (unbatched) or 4D (batched) tensor with shape:
      `(..., height, width, channels)`, in `"channels_last"` format.

    Arguments:
        x_factor: A tuple of two floats, a single float or a
            `keras_cv.FactorSampler`. For each augmented image a value is sampled
            from the provided range. If a float is passed, the range is interpreted as
            `(0, x_factor)`.  Values represent a percentage of the image to translate
             over. For example, 0.3 translates pixels up to 30% of the way across the
             image. All provided values should be positive.  If `None` is passed, no
             translation occurs on the X axis.
             Defaults to `None`.
        y_factor: A tuple of two floats, a single float or a
            `keras_cv.FactorSampler`. For each augmented image a value is sampled
            from the provided range. If a float is passed, the range is interpreted as
            `(0, y_factor)`. Values represent a percentage of the image to translate
             over. For example, 0.3 translates pixels up to 30% of the way across the
             image. All provided values should be positive.  If `None` is passed, no
             translation occurs on the Y axis.
             Defaults to `None`.
        interpolation: interpolation method used in the `ImageProjectiveTransformV3` op.
             Supported values are `"nearest"` and `"bilinear"`.
             Defaults to `"bilinear"`.
        fill_mode: fill_mode in the `ImageProjectiveTransformV3` op.
             Supported values are `"reflect"`, `"wrap"`, `"constant"`, and `"nearest"`.
             Defaults to `"reflect"`. Note, that using reflect in combination with
             large y_factor or x_factor might generate a mirror image of an object,
             which won't have an associated bounding box.
        fill_value: fill_value in the `ImageProjectiveTransformV3` op.
             A `Tensor` of type `float32`. The value to be filled when fill_mode is
             constant".  Defaults to `0.0`.
        bounding_box_format: The format of bounding boxes of input dataset. Refer to
             https://github.com/keras-team/keras-cv/blob/master/keras_cv/bounding_box/converters.py
             for more details on supported bounding box formats.
        seed: Integer. Used to create a random seed.
    """

    def __init__(
        self,
        x_factor=None,
        y_factor=None,
        fill_mode="reflect",
        interpolation="bilinear",
        fill_value=0.0,
        seed=None,
        bounding_box_format=None,
        **kwargs
    ):
        super().__init__(seed=seed, force_generator=True, **kwargs)
        self.seed = seed
        if x_factor is not None:
            self.x_factor = preprocessing.parse_factor(
                x_factor, max_value=None, param_name="x_factor", seed=seed
            )
        else:
            self.x_factor = x_factor
        if y_factor is not None:
            self.y_factor = preprocessing.parse_factor(
                y_factor, max_value=None, param_name="y_factor", seed=seed
            )
        else:
            self.y_factor = y_factor
        if x_factor is None and y_factor is None:
            warnings.warn(
                "RandomTranslation received both `x_factor=None` and `y_factor=None`.  "
                "As a result, the layer will perform no augmentation."
            )
        self.auto_vectorize = True
        self.bounding_box_format = bounding_box_format
        self.fill_mode = fill_mode
        self.fill_value = fill_value
        self.interpolation = interpolation

    def augment_label(self, label, transformation, **kwargs):
        return label

    def augment_image(self, image, transformation, **kwargs):
        return self._translate_image(image, transformation)

    def get_random_transformation(self, **kwargs):
        translate_horizontal = 0.0
        translate_vertical = 0.0
        if self.x_factor:
            translate_horizontal = self.x_factor()
        if self.y_factor:
            translate_vertical = self.y_factor()
        return {
            "translate_horizontal": tf.cast(translate_horizontal, dtype=tf.float32),
            "translate_vertical": tf.cast(translate_vertical, dtype=tf.float32),
        }

    def _translate_image(self, image, transformation):
        image = preprocessing.ensure_tensor(image, self.compute_dtype)
        image_shape = tf.cast(image.shape, tf.float32)
        image_width = image_shape[1]
        image_height = image_shape[0]
        element = tf.stack(
            [
                transformation["translate_horizontal"] * image_width,
                transformation["translate_vertical"] * image_height,
            ],
        )
        output = preprocessing.transform(
            tf.expand_dims(image, 0),
            preprocessing.get_translation_matrix(tf.expand_dims(element, axis=0)),
            fill_mode=self.fill_mode,
            fill_value=self.fill_value,
            interpolation=self.interpolation,
        )
        output = tf.squeeze(output, 0)
        output.set_shape(image_shape)
        return output

    @staticmethod
    def _translate_bounding_boxes_horizontal(bounding_boxes, dx):
        x1, x2, x3, x4, rest = tf.split(
            bounding_boxes, [1, 1, 1, 1, bounding_boxes.shape[-1] - 4], axis=-1
        )
        output = tf.stack(
            [
                x1 + dx,
                x2,
                x3 + dx,
                x4,
                rest,
            ],
            axis=-1,
        )
        output = tf.squeeze(output, axis=1)
        return output

    @staticmethod
    def _translate_bounding_boxes_vertical(bounding_boxes, dy):
        x1, x2, x3, x4, rest = tf.split(
            bounding_boxes, [1, 1, 1, 1, bounding_boxes.shape[-1] - 4], axis=-1
        )
        output = tf.stack(
            [
                x1,
                x2 + dy,
                x3,
                x4 + dy,
                rest,
            ],
            axis=-1,
        )
        output = tf.squeeze(output, axis=1)
        return output

    def augment_bounding_boxes(
        self, bounding_boxes, transformation=None, image=None, **kwargs
    ):
        if self.bounding_box_format is None:
            raise ValueError(
                "`RandomTranslation()` was called with bounding boxes,"
                "but no `bounding_box_format` was specified in the constructor."
                "Please specify a bounding box format in the constructor. i.e."
                "`RandomFlip(bounding_box_format='xyxy')`"
            )

        bounding_boxes = bounding_box.convert_format(
            bounding_boxes,
            source=self.bounding_box_format,
            target="rel_xyxy",
            images=image,
        )
        bounding_boxes = RandomTranslation._translate_bounding_boxes_horizontal(
            bounding_boxes,
            transformation["translate_horizontal"],
        )
        bounding_boxes = RandomTranslation._translate_bounding_boxes_vertical(
            bounding_boxes,
            transformation["translate_vertical"],
        )

        bounding_boxes = bounding_box.clip_to_image(
            bounding_boxes,
            bounding_box_format="rel_xyxy",
            images=image,
        )
        bounding_boxes = bounding_box.convert_format(
            bounding_boxes,
            source="rel_xyxy",
            target=self.bounding_box_format,
            dtype=self.compute_dtype,
            images=image,
        )
        return bounding_boxes

    def augment_segmentation_mask(
        self, segmentation_mask, transformation=None, **kwargs
    ):
        return self._translate_image(segmentation_mask, transformation)

    def compute_output_shape(self, input_shape):
        return input_shape

    def get_config(self):
        config = {
            "seed": self.seed,
            "x_factor": self.x_factor,
            "y_factor": self.y_factor,
            "bounding_box_format": self.bounding_box_format,
            "fill_mode": self.fill_mode,
            "fill_value": self.fill_value,
            "interpolation": self.interpolation,
        }
        base_config = super().get_config()
        return dict(list(base_config.items()) + list(config.items()))
