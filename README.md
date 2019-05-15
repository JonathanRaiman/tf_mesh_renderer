# TF Mesh Renderer

This is a differentiable, 3D mesh renderer using TensorFlow.
[Original repository](https://github.com/google/tf_mesh_renderer).

This for sends it to Pypi, and removes bazel as a dependency for installation
(e.g. just use `python3 setup.py install`).

### Installation
```
pip install mesh_renderer
```

### Usage

```
# load your geometry (this is a cube):
object_vertices = np.array([[-1, -1, 1], [-1, -1, -1], [-1, 1, -1], [-1, 1, 1], [1, -1, 1],
                            [1, -1, -1], [1, 1, -1], [1, 1, 1]])
object_triangles = np.array([[0, 1, 2], [2, 3, 0], [3, 2, 6], [6, 7, 3], [7, 6, 5], [5, 4, 7],
                             [4, 5, 1], [1, 0, 4], [5, 6, 2], [2, 1, 5], [7, 4, 0], [0, 3, 7]], dtype=np.int32)
object_vertices = tf.constant(object_vertices, dtype=tf.float32)
object_triangles = tf.constant(object_triangles, dtype=tf.int32)
object_normals = tf.nn.l2_normalize(object_vertices, dim=1)

# rotate the geometry:
angles = [[-1.16, 0.00, 3.48]]

model_rotation = camera_utils.euler_matrices(angles)[0, :3, :3]
# camera position:
eye = tf.constant([[0.0, 0.0, 6.0]], dtype=tf.float32)
lightbulb = tf.constant([[0.0, 0.0, 6.0]], dtype=tf.float32)
center = tf.constant([[0.0, 0.0, 0.0]], dtype=tf.float32)
world_up = tf.constant([[0.0, 1.0, 0.0]], dtype=tf.float32)
vertex_diffuse_colors = tf.reshape(tf.ones_like(vertices), [1, vertices.get_shape()[0].value, 3])
light_positions = tf.expand_dims(lightbulb, axis=0)
light_intensities = tf.ones([1, 1, 3], dtype=tf.float32)
ambient_color = tf.constant([[0.0, 0.0, 0.0]])

vertex_positions = tf.reshape(
    tf.matmul(vertices, model_rotation, transpose_b=True),
    [1, vertices.get_shape()[0].value, 3])
desired_normals = tf.reshape(
    tf.matmul(normals, model_rotation, transpose_b=True),
    [1, vertices.get_shape()[0].value, 3])

# render is a tf.Tensor 3d tensor of shape height x width x 4 (r, g, b, a)
# you can backpropagate through it.
render = mesh_renderer.mesh_renderer(
    vertex_positions, triangles, desired_normals,
    vertex_diffuse_colors, eye, center, world_up, light_positions,
    light_intensities, image_width, image_height,
    ambient_color=ambient_color,
)
```


# Original Readme

This is a differentiable, 3D mesh renderer using TensorFlow.

This is not an official Google product.

The interface to the renderer is provided by mesh_renderer.py and
rasterize_triangles.py, which provide TensorFlow Ops that can be added to a
TensorFlow graph. The internals of the renderer are handled by a C++ kernel.

The input to the C++ rendering kernel is a list of 3D vertices and a list of
triangles, where a triangle consists of a list of three vertex ids. The
output of the renderer is a pair of images containing triangle ids and
barycentric weights. Pixel values in the barycentric weight image are the
weights of the pixel center point with respect to the triangle at that pixel
(identified by the triangle id). The renderer provides derivatives of the
barycentric weights of the pixel centers with respect to the vertex
positions.

Any approximation error stems from the assumption that the triangle id at a
pixel does not change as the vertices are moved. This is a reasonable
approximation for small changes in vertex position. Even when the triangle id
does change, the derivatives will be computed by extrapolating the barycentric
weights of a neighboring triangle, which will produce a good approximation if
the mesh is smooth. The main source of error occurs at occlusion boundaries, and
particularly at the edge of an open mesh, where the background appears opposite
the triangle's edge.

The algorithm implemented is described by Olano and Greer, "Triangle Scan
Conversion using 2D Homogeneous Coordinates," HWWS 1997.

How to Build
------------

Follow the instructions to [install TensorFlow using virtualenv](https://www.tensorflow.org/install/install_linux#installing_with_virtualenv).

Build and run tests using Bazel from inside the (tensorflow) virtualenv:

`(tensorflow)$ ./runtests.sh`

The script calls the Bazel rules using the Python interpreter at
`$VIRTUAL_ENV/bin/python`. If you aren't using virtualenv, `bazel test ...` may
be sufficient.

Citation
--------

If you use this renderer in your research, please cite [this paper](http://openaccess.thecvf.com/content_cvpr_2018/html/Genova_Unsupervised_Training_for_CVPR_2018_paper.html "CVF Version"):

*Unsupervised Training for 3D Morphable Model Regression*. Kyle Genova, Forrester Cole, Aaron Maschinot, Aaron Sarna, Daniel Vlasic, and William T. Freeman. CVPR 2018, pp. 8377-8386.

```
@InProceedings{Genova_2018_CVPR,
  author = {Genova, Kyle and Cole, Forrester and Maschinot, Aaron and Sarna, Aaron and Vlasic, Daniel and Freeman, William T.},
  title = {Unsupervised Training for 3D Morphable Model Regression},
  booktitle = {The IEEE Conference on Computer Vision and Pattern Recognition (CVPR)},
  month = {June},
  year = {2018}
}
```


Bust of safo: https://cdn.thingiverse.com/zipfiles/ac/39/53/07/80/Bust_of_Sappho_.zip

