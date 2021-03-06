# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""A very simple MNIST classifer, modified to display data in TensorBoard.

See extensive documentation for the original model at
http://tensorflow.org/tutorials/mnist/beginners/index.md

See documentaion on the TensorBoard specific pieces at
http://tensorflow.org/how_tos/summaries_and_tensorboard/index.md

If you modify this file, please update the exerpt in
how_tos/summaries_and_tensorboard/index.md.

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow.python.platform
from tensorflow.g3doc.tutorials.mnist import input_data
import tensorflow as tf

flags = tf.app.flags
FLAGS = flags.FLAGS
flags.DEFINE_boolean('fake_data', False, 'If true, uses fake data '
                     'for unit testing.')
flags.DEFINE_integer('max_steps', 1000, 'Number of steps to run trainer.')
flags.DEFINE_float('learning_rate', 0.01, 'Initial learning rate.')


def main(_):
  # Import data
  mnist = input_data.read_data_sets('/tmp/data/', one_hot=True,
                                    fake_data=FLAGS.fake_data)

  sess = tf.InteractiveSession()

  # Create the model
  x = tf.placeholder('float', [None, 784], name='x-input')
  W = tf.Variable(tf.zeros([784, 10]), name='weights')
  b = tf.Variable(tf.zeros([10], name='bias'))

  # use a name scope to organize nodes in the graph visualizer
  with tf.name_scope('Wx_b') as scope:
    y = tf.nn.softmax(tf.matmul(x, W) + b)

  # Add summary ops to collect data
  w_hist = tf.histogram_summary('weights', W)
  b_hist = tf.histogram_summary('biases', b)
  y_hist = tf.histogram_summary('y', y)

  # Define loss and optimizer
  y_ = tf.placeholder('float', [None, 10], name='y-input')
  # More name scopes will clean up the graph representation
  with tf.name_scope('xent') as scope:
    cross_entropy = -tf.reduce_sum(y_ * tf.log(y))
    ce_summ = tf.scalar_summary('cross entropy', cross_entropy)
  with tf.name_scope('train') as scope:
    train_step = tf.train.GradientDescentOptimizer(
        FLAGS.learning_rate).minimize(cross_entropy)

  with tf.name_scope('test') as scope:
    correct_prediction = tf.equal(tf.argmax(y, 1), tf.argmax(y_, 1))
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, 'float'))
    accuracy_summary = tf.scalar_summary('accuracy', accuracy)

  # Merge all the summaries and write them out to /tmp/mnist_logs
  merged = tf.merge_all_summaries()
  writer = tf.train.SummaryWriter('/tmp/mnist_logs', sess.graph_def)
  tf.initialize_all_variables().run()

  # Train the model, and feed in test data and record summaries every 10 steps

  for i in range(FLAGS.max_steps):
    if i % 10 == 0:  # Record summary data, and the accuracy
      if FLAGS.fake_data:
        batch_xs, batch_ys = mnist.train.next_batch(
            100, fake_data=FLAGS.fake_data)
        feed = {x: batch_xs, y_: batch_ys}
      else:
        feed = {x: mnist.test.images, y_: mnist.test.labels}
      result = sess.run([merged, accuracy], feed_dict=feed)
      summary_str = result[0]
      acc = result[1]
      writer.add_summary(summary_str, i)
      print('Accuracy at step %s: %s' % (i, acc))
    else:
      batch_xs, batch_ys = mnist.train.next_batch(
          100, fake_data=FLAGS.fake_data)
      feed = {x: batch_xs, y_: batch_ys}
      sess.run(train_step, feed_dict=feed)

if __name__ == '__main__':
  tf.app.run()
