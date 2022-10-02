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

import numpy as np
import tensorflow as tf
from absl.testing import parameterized

from keras_cv.layers.preprocessing.random_translation import RandomTranslation


class RandomTranslationTest(tf.test.TestCase, parameterized.TestCase):
    def test_horizontal_translation(self):
        images = np.ones((1, 4, 4, 3), dtype=np.float32)
        bboxes = np.array(
            [
                [
                    [0.0, 0.0, 1.0, 1.0, 0.0],
                ],
            ],
            dtype=np.float32,
        )
        layer = RandomTranslation(
            x_factor=[0.5, 0.5],
            bounding_box_format="rel_xyxy",
            fill_mode="constant",
            fill_value=0.0,
        )
        inp = {"images": images, "bounding_boxes": bboxes}
        outputs = layer(inp, training=True)
        output_images, output_bboxes = outputs["images"], outputs["bounding_boxes"]
        expected_bboxes = np.array([[[0.5, 0.0, 1.0, 1.0, 0.0]]])
        expected_images = np.ones((4, 4, 3)).astype(np.float32)
        expected_images[:, :2, :] = 0
        expected_images = np.expand_dims(expected_images, axis=0)
        self.assertAllClose(expected_images, output_images)
        self.assertAllClose(expected_bboxes, output_bboxes)

    def test_full_horizontal_translation(self):
        images = np.ones((1, 4, 4, 3), dtype=np.float32)
        bboxes = np.array(
            [
                [
                    [0.0, 0.0, 1.0, 1.0, 0.0],
                ],
            ],
            dtype=np.float32,
        )
        layer = RandomTranslation(
            x_factor=[1.0, 1.0],
            bounding_box_format="rel_xyxy",
            fill_mode="constant",
            fill_value=0.0,
        )
        inp = {"images": images, "bounding_boxes": bboxes}
        outputs = layer(inp, training=True)
        output_images, output_bboxes = outputs["images"], outputs["bounding_boxes"]
        expected_bboxes = np.zeros((1, 0, 5))
        # expected_bboxes[:, :, -1] = -1
        expected_images = np.zeros((1, 4, 4, 3)).astype(np.float32)
        self.assertAllClose(expected_images, output_images)
        # actual coordinates don't matter as the class id is set to -1
        self.assertAllClose(expected_bboxes[:, :, -1], output_bboxes[:, :, -1])

    def test_full_horizontal_translation_multiple_images(self):
        images = np.ones((1, 4, 4, 3), dtype=np.float32)

        bboxes = np.array(
            [
                [
                    [0.0, 0.0, 1.0, 1.0, 0.0],
                    [0.0, 0.0, 1.0, 1.0, 0.0],
                ],
                [
                    [0.0, 0.0, 1.0, 1.0, 0.0],
                    [0.0, 0.0, 1.0, 1.0, 0.0],
                ],
            ],
            dtype=np.float32,
        )
        layer = RandomTranslation(
            x_factor=[1.0, 1.0],
            bounding_box_format="rel_xyxy",
            fill_mode="constant",
            fill_value=0.0,
        )
        inp = {"images": images, "bounding_boxes": bboxes}
        outputs = layer(inp, training=True)
        output_images, output_bboxes = outputs["images"], outputs["bounding_boxes"]
        expected_bboxes = np.zeros((2, 0, 5))
        # expected_bboxes[:, :, -1] = -1
        expected_images = np.zeros((2, 4, 4, 3)).astype(np.float32)
        self.assertAllClose(expected_images, output_images)
        # actual coordinates don't matter as the class id is set to -1
        self.assertAllClose(expected_bboxes[:, :, -1], output_bboxes[:, :, -1])

    def test_full_horizontal_translation_on_some_bboxes(self):
        images = np.ones((2, 4, 4, 3), dtype=np.float32)
        bboxes = np.array(
            [
                [
                    [0.5, 0.0, 1.0, 1.0, 0.0],
                    [0.0, 0.0, 1.0, 1.0, 0.0],
                ],
                [
                    [0.0, 0.0, 1.0, 1.0, 0.0],
                    [0.5, 0.0, 1.0, 1.0, 0.0],
                ],
            ],
            dtype=np.float32,
        )

        layer = RandomTranslation(
            x_factor=[0.5, 0.5],
            bounding_box_format="rel_xyxy",
            fill_mode="constant",
            fill_value=0.0,
        )
        inp = {"images": images, "bounding_boxes": bboxes}
        outputs = layer(inp, training=True)
        output_images, output_bboxes = outputs["images"], outputs["bounding_boxes"]
        expected_bboxes = np.array(
            [
                [
                    [0.5, 0.0, 1.0, 1.0, 0.0],
                ],
                [
                    [0.5, 0.0, 1.0, 1.0, 0.0],
                ],
            ],
        )
        expected_images = np.zeros((2, 4, 4, 3), dtype=np.float32)
        expected_images[:, :, 2:, :] = 1
        self.assertAllClose(expected_bboxes, output_bboxes)
        self.assertAllClose(expected_images, output_images)

    def test_negative_horizontal_translation(self):
        images = np.ones((1, 4, 4, 3), dtype=np.float32)
        bboxes = np.array(
            [
                [
                    [0.0, 0.0, 1.0, 1.0, 0.0],
                ],
            ],
            dtype=np.float32,
        )
        layer = RandomTranslation(
            x_factor=[-0.5, -0.5],
            bounding_box_format="rel_xyxy",
            fill_mode="constant",
            fill_value=0.0,
        )
        inp = {"images": images, "bounding_boxes": bboxes}
        outputs = layer(inp, training=True)
        output_images, output_bboxes = outputs["images"], outputs["bounding_boxes"]
        expected_bboxes = np.array(
            [
                [
                    [0.0, 0.0, 0.5, 1.0, 0.0],
                ],
            ],
        )
        expected_images = np.ones((4, 4, 3)).astype(np.float32)
        expected_images[:, 2:, :] = 0
        expected_images = np.expand_dims(expected_images, axis=0)
        self.assertAllClose(expected_images, output_images)
        self.assertAllClose(expected_bboxes, output_bboxes)

    def test_vertical_translation(self):
        images = np.ones((1, 4, 4, 3), dtype=np.float32)
        bboxes = np.array(
            [
                [
                    [0.0, 0.0, 1.0, 1.0, 0.0],
                ],
            ],
            dtype=np.float32,
        )
        layer = RandomTranslation(
            y_factor=[0.5, 0.5],
            bounding_box_format="rel_xyxy",
            fill_mode="constant",
            fill_value=0.0,
        )
        inp = {"images": images, "bounding_boxes": bboxes}
        outputs = layer(inp, training=True)
        output_images, output_bboxes = outputs["images"], outputs["bounding_boxes"]
        expected_bboxes = np.array([[[0.0, 0.5, 1.0, 1.0, 0.0]]])
        self.assertAllClose(expected_bboxes, output_bboxes)
        expected_images = np.ones((4, 4, 3)).astype(np.float32)
        expected_images[:2, :, :] = 0
        expected_images = np.expand_dims(expected_images, axis=0)
        self.assertAllClose(expected_images, output_images)

    def test_negative_vertical_translation(self):
        images = np.ones((1, 4, 4, 3), dtype=np.float32)
        bboxes = np.array(
            [
                [
                    [0.0, 0.0, 1.0, 1.0, 0.0],
                ],
            ],
            dtype=np.float32,
        )
        layer = RandomTranslation(
            y_factor=[-0.5, -0.5],
            bounding_box_format="rel_xyxy",
            fill_mode="constant",
            fill_value=0.0,
        )
        inp = {"images": images, "bounding_boxes": bboxes}
        outputs = layer(inp, training=True)
        output_images, output_bboxes = outputs["images"], outputs["bounding_boxes"]
        expected_bboxes = np.array([[[0.0, 0.0, 1.0, 0.5, 0.0]]])
        self.assertAllClose(expected_bboxes, output_bboxes)
        expected_images = np.ones((4, 4, 3)).astype(np.float32)
        expected_images[2:, :, :] = 0
        expected_images = np.expand_dims(expected_images, axis=0)
        self.assertAllClose(expected_images, output_images)

    def test_vertical_and_horizontal_translation(self):
        images = np.ones((1, 4, 4, 3), dtype=np.float32)
        bboxes = np.array(
            [
                [
                    [0.0, 0.0, 1.0, 1.0, 0.0],
                ],
            ],
            dtype=np.float32,
        )
        layer = RandomTranslation(
            x_factor=[0.25, 0.25],
            y_factor=[0.25, 0.25],
            bounding_box_format="rel_xyxy",
            fill_mode="constant",
            fill_value=0.0,
        )
        inp = {"images": images, "bounding_boxes": bboxes}
        outputs = layer(inp, training=True)
        output_images, output_bboxes = outputs["images"], outputs["bounding_boxes"]
        expected_bboxes = np.array([[[0.25, 0.25, 1.0, 1.0, 0.0]]])
        self.assertAllClose(expected_bboxes, output_bboxes)
        expected_images = np.ones((4, 4, 3)).astype(np.float32)
        expected_images[:1, :, :] = 0
        expected_images[:, :1, :] = 0
        expected_images = np.expand_dims(expected_images, axis=0)
        self.assertAllClose(expected_images, output_images)

    def test_no_augmentation(self):
        """test for no image and bbox augmentation when x_factor,y_factor is 0,0"""
        images = np.ones((1, 4, 4, 3), dtype=np.float32)
        bboxes = np.array(
            [
                [
                    [0.0, 0.0, 1.0, 1.0, 0.0],
                ],
            ],
            dtype=np.float32,
        )
        layer = RandomTranslation(
            x_factor=[0, 0],
            y_factor=[0, 0],
            bounding_box_format="rel_xyxy",
        )
        inp = {"images": images, "bounding_boxes": bboxes}
        outputs = layer(inp, training=True)
        output_images, output_bboxes = outputs["images"], outputs["bounding_boxes"]
        self.assertAllClose(bboxes, output_bboxes)
        self.assertAllClose(images, output_images)

    def test_translation_up_with_reflect(self):
        input_image = np.reshape(np.arange(0, 25), (1, 5, 5, 1))
        bboxes = np.array(
            [
                [
                    [0.0, 0.0, 1.0, 1.0, 0.0],
                ],
            ],
            dtype=np.float32,
        )

        # Shift by 2 pixels up
        layer = RandomTranslation(
            y_factor=(-0.4, -0.4),
            x_factor=(0, 0),
            fill_mode="reflect",
            bounding_box_format="rel_xyxy",
        )
        outputs = layer({"images": input_image, "bounding_boxes": bboxes})
        output_images, output_bboxes = outputs["images"], outputs["bounding_boxes"]

        expected_image = np.reshape(
            np.asarray(
                [
                    [10, 11, 12, 13, 14],
                    [15, 16, 17, 18, 19],
                    [20, 21, 22, 23, 24],
                    [20, 21, 22, 23, 24],
                    [15, 16, 17, 18, 19],
                ]
            ),
            (1, 5, 5, 1),
        )
        expected_bboxes = np.array(
            [
                [
                    [0.0, 0.0, 1.0, 0.6, 0.0],
                    [0.0, 0.6, 1.0, 1.0, 0.0],
                ],
            ]
        )
        self.assertAllCloseAccordingToType(expected_image, output_images)
        self.assertAllCloseAccordingToType(expected_bboxes, output_bboxes)

    def test_translation_down_with_reflect(self):
        input_image = np.reshape(np.arange(0, 25), (1, 5, 5, 1))
        bboxes = np.array(
            [
                [
                    [0.0, 0.0, 1.0, 1.0, 0.0],
                ],
            ],
            dtype=np.float32,
        )

        # Shift by 2 pixels down
        layer = RandomTranslation(
            y_factor=(0.4, 0.4),
            x_factor=(0, 0),
            fill_mode="reflect",
            bounding_box_format="rel_xyxy",
        )
        outputs = layer({"images": input_image, "bounding_boxes": bboxes})
        output_images, output_bboxes = outputs["images"], outputs["bounding_boxes"]

        expected_image = np.reshape(
            np.asarray(
                [
                    [5, 6, 7, 8, 9],
                    [0, 1, 2, 3, 4],
                    [0, 1, 2, 3, 4],
                    [5, 6, 7, 8, 9],
                    [10, 11, 12, 13, 14],
                ]
            ),
            (1, 5, 5, 1),
        )
        expected_bboxes = np.array(
            [
                [
                    [0.0, 0.4, 1.0, 1.0, 0.0],
                    [0.0, 0.0, 1.0, 0.4, 0.0],
                ],
            ]
        )
        self.assertAllCloseAccordingToType(expected_image, output_images)
        self.assertAllCloseAccordingToType(expected_bboxes, output_bboxes)

    def test_translation_right_with_reflect(self):
        input_image = np.reshape(np.arange(0, 25), (1, 5, 5, 1))
        bboxes = np.array(
            [
                [
                    [0.0, 0.0, 1.0, 1.0, 0.0],
                ],
            ],
            dtype=np.float32,
        )
        # Shift by 2 pixels right
        layer = RandomTranslation(
            y_factor=(0.0, 0.0),
            x_factor=(0.4, 0.4),
            fill_mode="reflect",
            bounding_box_format="rel_xyxy",
        )
        outputs = layer({"images": input_image, "bounding_boxes": bboxes})
        output_images, output_bboxes = outputs["images"], outputs["bounding_boxes"]

        expected_image = np.reshape(
            np.asarray(
                [
                    [1, 0, 0, 1, 2],
                    [6, 5, 5, 6, 7],
                    [11, 10, 10, 11, 12],
                    [16, 15, 15, 16, 17],
                    [21, 20, 20, 21, 22],
                ]
            ),
            (1, 5, 5, 1),
        )
        expected_bboxes = (
            np.array(
                [
                    [0.4, 0.0, 1.0, 1.0, 0.0],
                    [0.0, 0.0, 0.4, 1.0, 0.0],
                ]
            )
            .reshape((1, 2, 5))
            .astype("float32")
        )

        self.assertAllCloseAccordingToType(expected_image, output_images)
        self.assertAllCloseAccordingToType(expected_bboxes, output_bboxes)

    def test_translation_down_and_right_with_reflect(self):
        input_image = np.reshape(np.arange(0, 25), (1, 5, 5, 1))
        bboxes = np.array(
            [
                [
                    [0.0, 0.0, 1.0, 1.0, 0.0],
                ],
            ],
            dtype=np.float32,
        )
        # Shift by 2 pixels down
        layer = RandomTranslation(
            y_factor=(0.4, 0.4),
            x_factor=(0.4, 0.4),
            fill_mode="reflect",
            bounding_box_format="rel_xyxy",
        )
        outputs = layer({"images": input_image, "bounding_boxes": bboxes})
        output_images, output_bboxes = outputs["images"], outputs["bounding_boxes"]

        expected_image = np.reshape(
            np.asarray(
                [
                    [6, 5, 5, 6, 7],
                    [1, 0, 0, 1, 2],
                    [1, 0, 0, 1, 2],
                    [6, 5, 5, 6, 7],
                    [11, 10, 10, 11, 12],
                ]
            ),
            (1, 5, 5, 1),
        )
        expected_bboxes = np.array(
            [
                [0.4, 0.4, 1.0, 1.0, 0.0],
                [0.4, 0.0, 1.0, 0.4, 0.0],
                [0.0, 0.0, 0.4, 0.4, 0.0],
                [0.0, 0.4, 0.4, 1.0, 0.0],
            ]
        ).reshape((1, 4, 5))
        self.assertAllCloseAccordingToType(expected_image, output_images)
        self.assertAllCloseAccordingToType(expected_bboxes, output_bboxes)

    def test_translation_with_constant(self):
        input_image = np.arange(0, 25).reshape((1, 5, 5, 1))
        bboxes = np.array(
            [
                [
                    [0.0, 0.0, 1.0, 1.0, 0.0],
                ],
            ],
            dtype=np.float32,
        )
        # Shift by 2 pixels up
        layer = RandomTranslation(
            y_factor=(-0.4, -0.4),
            x_factor=(0, 0),
            fill_mode="constant",
            fill_value=0,
            bounding_box_format="rel_xyxy",
        )
        outputs = layer({"images": input_image, "bounding_boxes": bboxes})
        output_images, output_bboxes = outputs["images"], outputs["bounding_boxes"]
        expected_image = np.reshape(
            np.asarray(
                [
                    [10, 11, 12, 13, 14],
                    [15, 16, 17, 18, 19],
                    [20, 21, 22, 23, 24],
                    [0, 0, 0, 0, 0],
                    [0, 0, 0, 0, 0],
                ]
            ),
            (1, 5, 5, 1),
        )
        expected_bboxes = np.array(
            [0.0, 0.0, 1.0, 0.6, 0.0],
            dtype=np.float32,
        ).reshape((1, 1, 5))
        self.assertAllEqual(expected_image, output_images)
        self.assertAllEqual(expected_bboxes, output_bboxes)

    def test_translation_with_wrap(self):
        with self.assertRaises(ValueError):
            RandomTranslation(
                y_factor=(-0.4, -0.4),
                x_factor=(0, 0),
                fill_mode="wrap",
                bounding_box_format="rel_xyxy",
            )

    def test_translation_with_nearest(self):
        input_image = np.reshape(np.arange(0, 25), (1, 5, 5, 1))
        # Shift by 2 pixels up
        layer = RandomTranslation(
            y_factor=(-0.4, -0.4), x_factor=(0, 0), fill_mode="nearest"
        )
        output_image = layer(input_image)
        expected_output = np.reshape(
            np.asarray(
                [
                    [10, 11, 12, 13, 14],
                    [15, 16, 17, 18, 19],
                    [20, 21, 22, 23, 24],
                    [20, 21, 22, 23, 24],
                    [20, 21, 22, 23, 24],
                ]
            ),
            (1, 5, 5, 1),
        )
        self.assertAllEqual(expected_output, output_image)
