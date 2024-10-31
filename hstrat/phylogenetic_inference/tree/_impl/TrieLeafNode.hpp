#include <string>

#ifndef TRIE_LEAF_NODE
#define TRIE_LEAF_NODE

#include "TrieInnerNode.hpp"
class TrieInnerNode;
class TrieLeafNode {
private:
  std::string _taxon_label;
public:
  TrieLeafNode();
  TrieLeafNode(std::string taxon_label);
  bool operator==(const TrieLeafNode &other) const;
  bool operator>(const TrieLeafNode &other) const;
};

#endif // !TRIE_LEAF_NODE
