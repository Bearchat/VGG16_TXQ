# VGG16
VGG16 (presented by University of Oxford)  
implemented with TensorFlow

## Dependencies ##
python3.6
* numpy
* skimage
* TensorFlow
* matplotlib

## Usage ##
1. Import required modules
```
import tensorflow as tf
from util.util import *
from model.vgg16 import *
```

2. Load test-image  
```
img = load_image('./test.jpg')
img = img.reshape((1, 224, 224, 3))
```
In this example, load single-image.  
If you attempt to batch-process, load some images and concatenate them.
Then, modify img-shape e.g.,
```
img = img.reshape((batch_size, 224, 224, 3))
```

3. Start Session
```
with tf.Session() as sess:
    image = tf.placeholder(shape=[batch_size, 224, 224, 3], dtype=tf.float32)
    feed_dict = {image: img}
    vgg = Vgg16()
    vgg.build(image)
    sess.run(tf.global_variables_initializer())

    prob = sess.run(vgg.net, feed_dict=feed_dict)
    print(prob)
```

## Test Training ##
```
$ python cifar.py
```

## Present Circumstances ##
Finished cifar-10 learning.

![loss](github/loss.png)

### Complete: ###
* Learning cifar10
* saving and restoring parameters


If I have overlooked something, please tell me.

## Welcome PullRequest or E-mail ##
