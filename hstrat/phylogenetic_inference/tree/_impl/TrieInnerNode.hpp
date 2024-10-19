#include <cstdint>
#include <memory>
#include <vector>
#include <pybind11/stl.h>

#ifndef TRIE_INNER_NODE
#define TRIE_INNER_NODE

#include "TrieLeafNode.hpp"

class TrieLeafNode;
class TrieInnerNode {
private:
        uint64_t _rank;
        uint64_t _differentia;
        std::vector<TrieInnerNode> _inner_children;
        std::vector<TrieLeafNode> _outer_children;

        void AddChild(uint64_t rank, uint64_t differentia);
        bool IsOriginationOfAllele(uint64_t rank, uint64_t differentia) const;
public:

        const uint64_t &rank = _rank;
        const uint64_t &differentia = _differentia;
        const std::vector<TrieInnerNode> &inner_children = _inner_children;
        const std::vector<TrieLeafNode> &outer_children = _outer_children;

        TrieInnerNode();
        TrieInnerNode(uint64_t rank, uint64_t differentia);
        void InsertTaxon(const std::vector<uint64_t> &ranks, const std::vector<uint64_t> &differentiae);
        bool operator==(const TrieInnerNode &other) const;
};

#endif
