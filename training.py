# -*- coding: utf-8 -*-
"""reducing_training_time_testing_vivek_training.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zWrS3ag-69ygFmaSS35bHb47v7LGRtIY

<a href="https://colab.research.google.com/github/Jeff-AB/ECE542FinalProject/blob/jeff-development/ECE542FinalProject.ipynb" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/></a>

# ECE 542 Final Project

## Model Summary

<img src=https://ronjian.github.io/assets/Mask-RCNN/mask-rcnn.png width="500">

# References

# Mask R CNN
1. https://www.analyticsvidhya.com/blog/2019/07/computer-vision-implementing-mask-r-cnn-image-segmentation/

2. https://machinelearningmastery.com/how-to-perform-object-detection-in-photographs-with-mask-r-cnn-in-keras/

3. https://engineering.matterport.com/splash-of-color-instance-segmentation-with-mask-r-cnn-and-tensorflow-7c761e238b46 (Best)
"""
# Commented out IPython magic to ensure Python compatibility.
# %tensorflow_version 1.x
import tensorflow
import os
import sys
import random
import math
import numpy as np
import argparse
import skimage.io
import matplotlib
import matplotlib.pyplot as plt
from mrcnn import utils
import mrcnn.model as modellib
from mrcnn import visualize
import coco
from CityScapesDataset import CityscapesSegmentationDataset, TrainingConfig

# Submodule Libraries

# Import Mask RCNN
sys.path.append(ROOT_DIR)  # To find local version of the library

# Import COCO config
sys.path.append(os.path.join(ROOT_DIR, 'samples/coco/'))  # To find local version


#Global Constants
data_dir = 'data/'

train_dir = 'data/train'
val_dir = 'data/val'

CITI_ROOT = os.path.abspath('cityscapesScripts/')
MASK_ROOT = os.path.abspath('Mask_RCNN/')

sys.path.append(MASK_ROOT)
sys.path.append(CITI_ROOT)

# Commented out IPython magic to ensure Python compatibility.
# Root directory of the project
ROOT_DIR = os.path.abspath('Mask_RCNN/')

# Directory to save logs and trained model
MODEL_DIR = os.path.join(ROOT_DIR, 'logs')

# Local path to trained weights file
COCO_MODEL_PATH = os.path.join(ROOT_DIR, 'mask_rcnn_coco.h5')

# Download COCO trained weights from Releases if needed
if not os.path.exists(COCO_MODEL_PATH):
    utils.download_trained_weights(COCO_MODEL_PATH)

# Directory of images to run detection on
IMAGE_DIR = os.path.abspath(os.path.join(data_dir, 'test'))

DEFAULT_LOGS_DIR='logs'

config = TrainingConfig()
config.display()

def train_model():

    """# Model Setup

    Run this cell in order to setup the file structure that Mask R-CNN will expect to use. This includes MODEL_DIR for saving models, 

    *   `MODEL_DIR`: directory to write trained models to
    *   `COCO_MODEL_PATH`: directory to read trained models in from
    *   `IMAGE_DIR`: directory root for image data (training and testing)

    create config class based on application.
    """

    # Create model object in training mode.
    model = modellib.MaskRCNN(mode="training", model_dir=MODEL_DIR, config=config)

    # Load weights trained on MS-COCO, excepting areas for training
    # We can exclude the bounding box layers for now, but they will
    # be useful for interpreting our images for now
    model.load_weights(COCO_MODEL_PATH, by_name=True, exclude=["mrcnn_bbox_fc",
                                                            "mrcnn_bbox",
                                                            "mrcnn_mask",
                                                            "mrcnn_class_logits"])

    """# Dataset organization

    TODO: We read in data using the following structure. This will allow us to have annotations stored in a JSON format in one directory with images stored in another with train and val subset labels respectively. 

    ```
    DATA_DIR
    │
    └───annotations
    │   │   bdd100k_labels_images_<subset><year>.json
    │   
    └───<subset><year>
        │   image021.jpeg
        │   image022.jpeg
    ```

    # Model Training

    Run these cells in order to train the Mask R-CNN model's mask and ROI-related layers (excludes CNN backbone layers).
    """

    if model.model_dir is None:
        model.model_dir = '/home/jabaraho'
    # Training dataset.
    dataset_train = CityscapesSegmentationDataset()
    dataset_train.load_cityscapes(data_dir, 'train')
    dataset_train.prepare()

    # Validation dataset
    dataset_val = CityscapesSegmentationDataset()
    dataset_val.load_cityscapes(data_dir, 'val')
    dataset_val.prepare()

    model.train(dataset_train, 
                dataset_val,
                learning_rate=config.LEARNING_RATE,
                epochs=5,
                layers='heads',
                augmentation=None)


    # Retrieve history for plotting loss and accuracy per epoch
    history = model.keras_model.history.history

    # Accuracy plot config
    plt.subplot(1, 2, 1)
    plt.plot(history.history['categorical_accuracy'])
    plt.plot(history.history['val_categorical_accuracy'])
    plt.title('Training and Validation Accuracy vs. Epoch')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy')
    plt.legend(('Training', 'Validation'))
    plt.grid()

    # Loss plot config
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'])
    plt.plot(history.history['val_loss'])
    plt.title('Training and Validation Loss vs. Epoch')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend(('Training', 'Validation'))
    plt.grid()

    # Display plot
    plt.show()
    ## Save Model History
    with open(os.path.join(MODEL_DIR, 'training_history')), 'wb') as file_pi:
        pickle.dump(history.history, file_pi)

"""# Model Evaluation

Run these cells in order to receive an evaluation on a test image. First, the new model is selected from among the saved checkpoint models. Then, a configuration is set for inference (the same as before). Then a sample image is labeled using the Berkeley Deep Drive classes.
"""

def display_predictions():
    # select trained model 
    dir_names = next(os.walk(MODEL_DIR))[1]
    key = config.NAME.lower()
    dir_names = filter(lambda f: f.startswith(key), dir_names)
    dir_names = sorted(dir_names)

    if not dir_names:
        import errno
        raise FileNotFoundError(
            errno.ENOENT,
            "Could not find model directory under {}".format(self.model_dir))
        
    fps = []
    # Pick last directory
    for d in dir_names: 
        dir_name = os.path.join(model.model_dir, d)
        # Find the last checkpoint
        checkpoints = next(os.walk(dir_name))[2]
        checkpoints = filter(lambda f: f.startswith("mask_rcnn"), checkpoints)
        checkpoints = sorted(checkpoints)
        if not checkpoints:
            print('No weight files in {}'.format(dir_name))
        else:
            checkpoint = os.path.join(dir_name, checkpoints[best_epoch])
            fps.append(checkpoint)

    model_path = sorted(fps)[-1]
    print('Found model {}'.format(model_path))

    # Recreate the model in inference mode
    model = modellib.MaskRCNN(mode='inference', 
                            config=config,
                            model_dir=ROOT_DIR)

    # Load trained weights (fill in path to trained weights here)
    assert model_path != "", "Provide path to trained weights"
    print("Loading weights from ", model_path)
    model.load_weights(model_path, by_name=True)

    # Load a random image from the images folder
    root, dirs, file_names = next(os.walk(IMAGE_DIR))
    print(file_names)
    image = skimage.io.imread(os.path.join(IMAGE_DIR, random.choice(file_names)))

    # Run detection
    results = model.detect([image], verbose=1)

    # Visualize results
    r = results[0]
    visualize.display_instances(image, r['rois'], r['masks'], r['class_ids'], 
                                class_names, r['scores'])

def parse_args():
    parser = argparse.ArgumentParser(description='Train and display checkpoint results')
    parser.add_argument('--checkpoint_detection', action='store_true')
    parser.add_argument('--train_model', action='store_true')
    parser.add_argument('--train_from_checkpoint', action='store_true')
    return parser.parse_args()

def main():
    args = parse_args()

    if(args.checkpoint_detection):
        display_predictions()
    elif(args.train_model):
        train_model()
    elif(args.train_from_checkpoint):
        print('not implemented')
    else:
        print('no valid args provided')
if __name__ == "__main__":
    #select mode to run
    main()