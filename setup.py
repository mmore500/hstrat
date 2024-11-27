#!/usr/bin/env python

"""The setup script."""

# shim for compatibility with setuptools build workflow
# adapted from https://stackoverflow.com/a/58754298

from pybind11.setup_helpers import Pybind11Extension, build_ext

from setuptools import setup

setup(
    ext_modules=[
        Pybind11Extension(
            "hstrat.phylogenetic_inference.tree.build_tree_searchtable_cpp",
            ["hstrat/phylogenetic_inference/tree/build_tree_searchtable_cpp.cpp"],
            cxx_std=23
        ),
    ],
    cmdclass={"build_ext": build_ext},
)
