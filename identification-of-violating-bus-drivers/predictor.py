import tensorflow as tf
import numpy as np

class Predictor:
    def __init__(self, checkpoint_filename, input_name="images",
                 output_name="features"):
        self.session = tf.Session()
        with tf.io.gfile.GFile(checkpoint_filename, "rb") as file_handle:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(file_handle.read())
        tf.import_graph_def(graph_def, name="")
        ops = tf.compat.v1.get_default_graph().get_operations()
        all_tensor_names = {output.name for op in ops for output in op.outputs}

        self.tensor_dict = {}
        for key in [
            'num_detections', 'detection_boxes', 'detection_scores',
            'detection_classes', 'detection_masks'
        ]:
            tensor_name = key + ':0'
            if tensor_name in all_tensor_names:
                self.tensor_dict[key] = tf.get_default_graph(
                ).get_tensor_by_name(tensor_name)

        self.image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')

    def __call__(self, frame):
        image = np.expand_dims(frame, axis=0)
        output_dict = self.session.run(self.tensor_dict,
                                       feed_dict={self.image_tensor: image})
        output_dict['num_detections'] = int(
            output_dict['num_detections'][0])
        output_dict['detection_classes'] = output_dict[
            'detection_classes'][0].astype(np.int64)
        output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
        output_dict['detection_scores'] = output_dict['detection_scores'][0]
        return output_dict