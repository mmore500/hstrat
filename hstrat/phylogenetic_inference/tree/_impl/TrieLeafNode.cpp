#include "TrieLeafNode.hpp"
#include <cstdlib>
#include <sstream>

TrieLeafNode::TrieLeafNode() {
        std::stringstream s;
        s << random();
        this->_taxon_label = s.str();
}

TrieLeafNode::TrieLeafNode(std::string taxon_label) : _taxon_label(taxon_label) {};

bool TrieLeafNode::operator==(const TrieLeafNode &other) const {
        return this->_taxon_label == other._taxon_label;
}

bool TrieLeafNode::operator>(const TrieLeafNode &other) const {
        return this->_taxon_label > other._taxon_label;
}
