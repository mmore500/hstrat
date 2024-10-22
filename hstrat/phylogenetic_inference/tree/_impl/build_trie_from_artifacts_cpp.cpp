// cppimport

#include <pybind11/pybind11.h>
#include <pybind11/cast.h>
#include <pybind11/stl.h>
#include <pybind11/pytypes.h>

#include "TrieInnerNode.hpp"

#include <memory>
#include <iostream>
#include <type_traits>
#include <utility>

namespace py = pybind11;

TrieInnerNode build_trie_from_artifacts_sync(
        const std::vector<std::pair<std::vector<uint64_t>, std::vector<uint64_t>>> &population,
        const std::vector<std::string> &taxon_labels
) {
        TrieInnerNode root{};
        for (const std::pair<std::vector<uint64_t>, std::vector<uint64_t>> &specimen : population) {
                root.InsertTaxon(specimen.first, specimen.second);
        }
        return root;  // does a full copy consider returning a shared_ptr or something
}

PYBIND11_MODULE(build_trie_from_artifacts_cpp, m) {
        m.doc() = "C++ implementations for the algorithms found in the build_trie_from_artifacts.py file.";
        m.def("build_trie_from_artifacts_sync", &build_trie_from_artifacts_sync, py::arg("population"), py::arg("taxon_labels"));
        py::class_<TrieInnerNode, std::shared_ptr<TrieInnerNode>>(m, "TrieInnerNode_C")
                .def(py::init<>())
                .def(py::init<uint64_t, uint64_t>(),
                     py::arg("differentia"), py::arg("rank"))
                .def("InsertTaxon",
                     &TrieInnerNode::InsertTaxon,
                     py::arg("differentiae"), py::arg("ranks"))
                .def("__eq__", &TrieInnerNode::operator==)
                .def_property_readonly("inner_children", [](const TrieInnerNode &n) {
                        return py::cast(n.inner_children);
                })
                .def_property_readonly("outer_children", [](const TrieInnerNode &n) {
                        return py::cast(n.outer_children);
                })
                .def_property_readonly("differentia", [](const TrieInnerNode &n) {
                        return n.differentia;
                })
                .def_property_readonly("rank", [](const TrieInnerNode &n) {
                        return n.rank;
                });

        py::class_<TrieLeafNode, std::shared_ptr<TrieLeafNode>>(m, "TrieLeafNode_C")
                .def(py::init<>())
                .def(py::init<const std::string&>(),
                     py::arg("taxon_label"));
}

/*
<%
cfg['sources'] = ['TrieLeafNode.cpp', 'TrieInnerNode.cpp']
setup_pybind11(cfg)
%>
*/
