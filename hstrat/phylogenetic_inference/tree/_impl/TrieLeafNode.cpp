#include <iostream>
#include <format>
#include <random>

#include "TrieLeafNode.hpp"

TrieLeafNode::TrieLeafNode() {
  std::mt19937 gen(std::random_device{}());
  std::uniform_int_distribution<uint32_t> dis(0, 0xFFFFFFFF);

  this->_taxon_label = std::format(
    "{:08x}{:08x}{:08x}{:08x}", dis(gen), dis(gen), dis(gen), dis(gen)
  );
}

TrieLeafNode::TrieLeafNode(std::string taxon_label) : _taxon_label(taxon_label) {}

bool TrieLeafNode::operator==(const TrieLeafNode &other) const {
  return this->_taxon_label == other._taxon_label;
}

bool TrieLeafNode::operator>(const TrieLeafNode &other) const {
  return this->_taxon_label > other._taxon_label;
}
