#include "TrieInnerNode.hpp"
#include "TrieLeafNode.hpp"

#include <pybind11/stl.h>
#include <algorithm>
#include <memory>
#include <vector>

TrieInnerNode::TrieInnerNode() : _rank(0), _differentia(0) {};

TrieInnerNode::TrieInnerNode(uint64_t rank, uint64_t differentia) : _rank(rank), _differentia(differentia) {};

template <typename T>
bool compare_children(const std::vector<T> &a, const std::vector<T> &b, bool (*comparer)(T *, T *)) {
        // if (a.size() != b.size()) {
        //         return false;
        // }
        // std::vector<const T *> a_ptrs(0), b_ptrs(0);
        // for (size_t i = 0; i < a.size(); ++i) {
        //         a_ptrs.push_back(&a[i]);
        //         b_ptrs.push_back(&b[i]);
        // }
        // std::sort(a_ptrs.begin(), a_ptrs.end(), comparer);
        // std::sort(b_ptrs.begin(), b_ptrs.end(), comparer);
        // for (size_t i = 0; i < a.size(); ++i) {
        //         if (!(*a_ptrs[i] == *b_ptrs[i])) {
        //                 return false;
        //         }
        // }
        return true;
}

bool TrieInnerNode::operator==(const TrieInnerNode &other) const {
        return compare_children<TrieInnerNode>(this->_inner_children, other._inner_children, [](TrieInnerNode *a, TrieInnerNode *b) {
                if (a->_rank == b->_rank) {
                        return b->_differentia > a->_differentia;
                }
                return b->_rank > a->_rank;
        }) && compare_children<TrieLeafNode>(this->_outer_children, other._outer_children, [](TrieLeafNode *a, TrieLeafNode *b) {
                return *a > *b;
        });
}

bool TrieInnerNode::IsOriginationOfAllele(uint64_t rank, uint64_t differentia) const {
        return this->_rank == rank && this->_differentia == differentia;
}

void TrieInnerNode::AddChild(uint64_t rank, uint64_t differentia) {
        this->_inner_children.push_back(TrieInnerNode(rank, differentia));
}

void TrieInnerNode::InsertTaxon(const std::vector<uint64_t> &ranks, const std::vector<uint64_t> &differentiae) {
        assert(differentiae.size() == ranks.size());
        TrieInnerNode *root = this;
        for (auto  i = differentiae.begin(), j = ranks.begin(); j != ranks.end(); ++i, ++j) {
                uint64_t r = *j, d = *i;
                bool found = false;
                for (size_t i = 0; i < root->_inner_children.size(); ++i) {
                        TrieInnerNode *child = &root->_inner_children[i];
                        if (child->IsOriginationOfAllele(r, d)) {
                                root = child;
                                found = true;
                                break;
                        }
                }
                if (!found) {
                        root->AddChild(_rank, _differentia);
                        root = &root->_inner_children[root->_inner_children.size() - 1];
                }
        }
}
