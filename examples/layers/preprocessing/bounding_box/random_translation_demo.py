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
"""
random_translation_demo.py shows how to use the RandomTranslate preprocessing layer for
object detection.
"""
import demo_utils
import tensorflow as tf

from keras_cv.layers import preprocessing


def main():
    dataset = demo_utils.load_voc_dataset(bounding_box_format="rel_xyxy")
    random_translation = preprocessing.RandomTranslation(
        bounding_box_format="rel_xyxy",
        fill_mode="reflect",
        y_factor=[0.5, 0.5],
        x_factor=[0.5, 0.5],
    )
    result = dataset.map(random_translation, num_parallel_calls=tf.data.AUTOTUNE)
    demo_utils.visualize_data(result, bounding_box_format="rel_xyxy")


if __name__ == "__main__":
    main()
