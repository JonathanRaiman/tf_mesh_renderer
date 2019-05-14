import os.path as osp
import sys
from distutils.core import Extension, setup
from distutils.command.build_ext import build_ext
import subprocess
from distutils.version import StrictVersion

SCRIPT_DIR = osp.dirname(osp.realpath(__file__))

extra_compile_args = ['-std=c++11']
extra_link_args = []


if sys.platform == 'darwin':
    extra_compile_args.append('-stdlib=libc++')
    extra_link_args.append('-stdlib=libc++')

include_dirs = ['/usr/local/include']
library_dirs = ['/usr/local/lib']

mesh_renderer_lib = Extension(
    name='mesh_renderer_lib',
    sources=['mesh_renderer/kernels/rasterize_triangles_op.cc',
             'mesh_renderer/kernels/rasterize_triangles_impl.cc',
             'mesh_renderer/kernels/rasterize_triangles_grad.cc'],
    include_dirs=include_dirs,
    library_dirs=library_dirs,
    libraries=[],
    language='c++',
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args,
)


def get_version():
    with open('VERSION', 'r') as fp:
        version = fp.readline()
        return version.strip()


REMOVE_FLAGS = {'-Wstrict-prototypes'}


class mesh_renderer_build_ext(build_ext):
    def get_libraries(self, ext):
        libs = super(mesh_renderer_build_ext, self).get_libraries(ext)
        last_lib = [libs[-1], "python{}".format(sys.version_info.major)]
        actual_python_libname = None
        for ll in last_lib:
            if actual_python_libname is not None:
                break
            for path in self.library_dirs:
                if osp.exists(osp.join(path, "lib" + ll + ".so")):
                    actual_python_libname = ll
                    break
        if actual_python_libname is None:
            actual_python_libname = libs[-1]
        return libs[:-1] + [actual_python_libname]

    def build_extensions(self):
        extension = self.extensions[0]
        assert extension.name == 'mesh_renderer_lib'

        import tensorflow as tf
        # Read more at https://www.tensorflow.org/versions/r1.1/extend/adding_an_op

        # seems like extra chars like "-rc1" are at the end of string, right after "patch" number so this should work
        tf_version_major, tf_version_minor = map(int, tf.__version__.split(".")[:2])
        assert tf_version_major == 1

        if "__cxx11_abi_flag__" in tf.__dict__:
            abi = tf.__cxx11_abi_flag__
        else:
            tf_path = tf.__path__[0]
            if tf_version_minor >= 4:
                tf_so = '{}/libtensorflow_framework.so'.format(tf_path)
            else:
                tf_so = '{}/python/_pywrap_tensorflow_internal.so'.format(tf_path)

            gcc_from_tf = subprocess.check_output("strings " + tf_so + " | grep GCC | grep ubuntu | uniq || true", shell=True).decode("utf-8").strip()
            clang_from_tf = subprocess.check_output("strings " + tf_so + " | grep clang || true", shell=True).decode("utf-8").strip()

            if len(gcc_from_tf) > 5:
                assert len(gcc_from_tf) > 5, "Cannot extract tensorflow gcc version."
                gcc_version = gcc_from_tf.split("-")[0].split(" ")[-1]
                print("Detected gcc_version: %s" % gcc_version)
                if StrictVersion(gcc_version) < StrictVersion("5.0"):
                    abi = 0
                else:
                    abi = 1
            elif len(clang_from_tf) > 0:
                abi = 1
            else:
                raise ValueError("not using clang or gcc, not sure how to set D_GLIBCXX_USE_CXX11_ABI.")
        extension.extra_compile_args.append('-D_GLIBCXX_USE_CXX11_ABI=%s' % abi)

        extension.include_dirs.append(tf.sysconfig.get_include())
        if tf_version_minor >= 4:
            extension.extra_link_args.append('-ltensorflow_framework')
            extension.include_dirs.append(tf.sysconfig.get_include() + '/external/nsync/public')
            extension.library_dirs.append(tf.sysconfig.get_lib())

        self.compiler.compiler_so = list(filter(lambda flag: flag not in REMOVE_FLAGS, self.compiler.compiler_so))
        super(mesh_renderer_build_ext, self).build_extensions()


setup(
    name='mesh_renderer',
    version=get_version(),
    cmdclass={'build_ext': mesh_renderer_build_ext},
    py_modules=['mesh_renderer', 'camera_utils', 'rasterize_triangles'],
    ext_modules=[mesh_renderer_lib],
    description='TF rendering',
    author='Someone, OpenAI',
    author_email='google@openai.com',
    install_requires=[],
)
