#include <cstdlib>
#include <format>

#include "TrieLeafNode.hpp"

TrieLeafNode::TrieLeafNode() {
  this->_taxon_label = std::format("{}", std::random());
}

TrieLeafNode::TrieLeafNode(std::string taxon_label) : _taxon_label(taxon_label) {}

bool TrieLeafNode::operator==(const TrieLeafNode &other) const {
  return this->_taxon_label == other._taxon_label;
}

bool TrieLeafNode::operator>(const TrieLeafNode &other) const {
  return this->_taxon_label > other._taxon_label;
}
