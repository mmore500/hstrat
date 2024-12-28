// cppimport
#ifdef DEBUG
#undef NDEBUG
#endif

#include <algorithm>
#include <bit>
#include <cassert>
#include <functional>
#include <limits>
#include <numeric>
#include <optional>
#include <ranges>
#include <span>
#include <unordered_map>
#include <utility>
#include <vector>

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

using namespace pybind11::literals;
namespace py = pybind11;

typedef uint64_t u64;
constexpr u64 u64_max = std::numeric_limits<uint64_t>::max();

/** @brief Discard the output of functions that requires an output iterator */
template<typename T> struct null_output_iterator {
  // adapted from https://stackoverflow.com/a/73189051/17332200
  using iterator_category = std::forward_iterator_tag;
  using value_type = T;
  using difference_type = T;
  using pointer = T*;
  using reference = T&;

  /** @brief No-op assignment */
  void operator=(T const&) {}

  /** @brief Can be pre-incremented */
  null_output_iterator& operator++() { return *this; }

  /** @brief Can be post-incremented */
  null_output_iterator operator++(int) { return *this; }

  /** @brief Can be dereferenced */
  null_output_iterator& operator*() { return *this; }
};


/**
 *  An iterator that casts the value of another iterator to u64.
 */
template<typename T> struct as_u64_iterator {
  using value_type = u64;
  using pointer = u64*;
  using reference = u64&;
  using iterator_category = std::forward_iterator_tag;
  using difference_type = int;

  T iter;

  explicit as_u64_iterator(const T& iter) : iter(iter) {}

  u64 operator*() const { return static_cast<u64>(*iter); }

  as_u64_iterator& operator++() {
    ++iter;
    return *this;
  }

  as_u64_iterator operator++(int) {
    auto res = *this;
    ++iter;
    return res;
  }

  bool operator==(const as_u64_iterator& other) const {
    return iter == other.iter;
  }

  bool operator!=(const as_u64_iterator& other) const {
    return iter != other.iter;
  }
};


/**
 *  An iterator that counts up from 0.
 *  Adapted from https://github.com/mmore500/signalgp-lite/blob/6ec86f7fb189b299fee842b9231ca9711deafd11/include/sgpl/utility/CountingIterator.hpp
 */
template<typename T=size_t>
class CountingIterator {

  size_t idx{};

public:
  using value_type = T;
  using pointer = value_type*;
  using reference = value_type&;
  using iterator_category = std::forward_iterator_tag;
  using difference_type = int;

  CountingIterator() = default;
  explicit CountingIterator(const T& t) : idx( t ) {}

  value_type operator*() const { return idx; }

  CountingIterator operator++(int) {
    const auto res = *this;
    ++idx;
    return res;
  }

  CountingIterator& operator++() {
    ++idx;
    return *this;
  }

  CountingIterator operator+(const size_t rhs) {
    CountingIterator res{ *this };
    res.idx += rhs;
    return res;
  }

  bool operator==(const CountingIterator& other) const {
    return operator*() == other.operator*();
  }

  bool operator!=(const CountingIterator& other) const {
    return operator*() != other.operator*();
  }

};


/**
 *  An object that holds all the information for building a
 *  trie using the searchtable approach. Each record is stored
 *  at one index in the member vectors. Storage details:
 *    - The `dstream_data_id` represents that in the downstream
 *      library, and is unique per artifact.
 *    - Children for a node are stored as storing the index for
 *      the first child in `search_first_child_id`, and storing
 *      the rest of the children as a linked list in the first
 *      child in `search_next_sibling_id`.
 *    - `ancestor_id` and `search_ancestor_id` differ when the
 *      records are consolidated. `ancestor_id` remains to save
 *      the information, while `search_ancestor_id` changes.
 *    - Parents have a higher `rank` than children.
 *  @see build_trie_searchtable_nested
 *  @see build_trie_searchtable_exploded
 *  @see extend_trie_searchtable_exploded
 */
struct Records {
  std::vector<u64> dstream_data_id;
  std::vector<u64> id;
  std::vector<u64> search_first_child_id;
  std::vector<u64> search_next_sibling_id;
  std::vector<u64> search_ancestor_id;
  std::vector<u64> ancestor_id;
  std::vector<u64> differentia;
  std::vector<u64> rank;
  u64 max_differentia = 0;

  explicit Records(const u64 init_size, const bool init_root=true) {
    this->dstream_data_id.reserve(init_size);
    this->id.reserve(init_size);
    this->search_first_child_id.reserve(init_size);
    this->search_next_sibling_id.reserve(init_size);
    this->search_ancestor_id.reserve(init_size);
    this->ancestor_id.reserve(init_size);
    this->differentia.reserve(init_size);
    this->rank.reserve(init_size);

    if (init_root) this->addRecord(u64_max, 0, 0, 0, 0, 0, 0, 0); // root node
  }

  /** Copy constructor. */
  Records(const Records &other) = delete;

  /** Move constructor. */
  Records(Records &&other) = default;

  bool operator==(const Records &other) const = default;

  void swap(Records &other) noexcept {
    this->dstream_data_id.swap(other.dstream_data_id);
    this->id.swap(other.id);
    this->search_first_child_id.swap(other.search_first_child_id);
    this->search_next_sibling_id.swap(other.search_next_sibling_id);
    this->search_ancestor_id.swap(other.search_ancestor_id);
    this->ancestor_id.swap(other.ancestor_id);
    this->differentia.swap(other.differentia);
    this->rank.swap(other.rank);
    std::swap(this->max_differentia, other.max_differentia);
  }

  void addRecord(
    const u64 data_id,
    const u64 id,
    const u64 ancestor_id,
    const u64 search_ancestor_id,
    const u64 search_first_child_id,
    const u64 search_next_sibling_id,
    const u64 rank,
    const u64 differentia
  ) {
    this->dstream_data_id.push_back(data_id);
    this->id.push_back(id);
    this->search_first_child_id.push_back(search_first_child_id);
    this->search_next_sibling_id.push_back(search_next_sibling_id);
    this->search_ancestor_id.push_back(search_ancestor_id);
    this->ancestor_id.push_back(ancestor_id);
    this->differentia.push_back(differentia);
    this->rank.push_back(rank);
    max_differentia = std::max(max_differentia, differentia);
  }

  u64 size() const { return this->dstream_data_id.size(); }

};


/**
 *  Removes record entries that are unifurcations and are associated with
 *  dropped ranks (i.e., by current num_strata_deposited, differentiae at those
 *  ranks have been purged. This function is used to save memory.
 *
 *  Note that detection of dropped ranks is incomplete, as it is based on the
 *  reconfiguration of the search trie. A more comprehensive approach could
 *  collate dropped ranks across all records.
 */
Records collapse_dropped_unifurcations(Records &records) {
  assert(std::equal(
    std::begin(records.id),
    std::end(records.id),
    CountingIterator<u64>{}
  ));

  // how many entries have an entry as ancestor?
  std::vector<uint8_t> ancestor_ref_counts(records.size());
  std::for_each(
    std::begin(records.id),
    std::end(records.id),
    [&ancestor_ref_counts, &records](const u64 id){
      // note: want to count root as ref to self
      const auto ancestor_id = records.ancestor_id[id];
      assert(ancestor_id <= id);
      auto& ref_count = ancestor_ref_counts[ancestor_id];
      // increment preventing overflow
      ref_count = std::min(ref_count + 1, 2);
    }
  );

  // a.k.a. should_keeps; ref to save memory
  auto& is_not_dropped_unifurcation = ancestor_ref_counts;
  std::transform(
    std::begin(records.id),
    std::end(records.id),
    std::begin(ancestor_ref_counts),
    std::begin(is_not_dropped_unifurcation),  // output iterator
    [&records](
      const u64 id, const uint8_t ancestor_ref_count
    ) {
      const bool is_unifurcation = ancestor_ref_count == 1;
      const bool is_dropped = (
        records.ancestor_id[id] != id
        and records.search_ancestor_id[id] == id
      );
      const bool is_dropped_unifurcation = is_unifurcation and is_dropped;
      return !is_dropped_unifurcation;
    }
  );

  // maps position [old id] to new, contiguously assigned id
  std::vector<u64> id_remap;
  id_remap.reserve(records.size());

  // set up id_remap ansatz; number of preceding kept items
  assert(!is_not_dropped_unifurcation.empty());
  id_remap.push_back(0);
  std::partial_sum(
    as_u64_iterator(std::begin(is_not_dropped_unifurcation)),
    as_u64_iterator(std::prev(std::end(is_not_dropped_unifurcation))),
    std::back_inserter(id_remap),
    std::plus<u64>{}
  );

  // fill id_remap with reassigned ids
  std::transform(
    std::begin(records.id),
    std::end(records.id),
    std::begin(id_remap),
    std::begin(id_remap),
    [&id_remap, &records, &is_not_dropped_unifurcation](
      const u64 id, const u64 ansatz
    ) {
      const bool should_keep = is_not_dropped_unifurcation[id];
      if (should_keep) return ansatz;
      else {
        const auto orig_ancestor_id = records.ancestor_id[id];
        assert(orig_ancestor_id < id);
        return id_remap[orig_ancestor_id];
      }
    }
  );

  // create new record set
  const auto reserve_size = records.size() + records.size() / 2;  // 1.5x
  Records new_records(reserve_size, /* init_root= */ false);
  assert(new_records.size() == 0);
  std::transform(
    std::begin(records.id),
    std::end(records.id),
    std::begin(id_remap),
    null_output_iterator<int>{},
    [&is_not_dropped_unifurcation, &id_remap, &new_records, &records](
      const u64 old_id, const u64 new_id
    ) {
        const bool should_keep = is_not_dropped_unifurcation[old_id];
        if (should_keep) {
          assert(new_id == new_records.size());
          assert(new_id <= old_id);
          assert(is_not_dropped_unifurcation[
            records.search_ancestor_id[old_id]
          ]);
          assert(is_not_dropped_unifurcation[
            records.search_first_child_id[old_id]
          ]);
          assert(is_not_dropped_unifurcation[
            records.search_next_sibling_id[old_id]
          ]);

          new_records.addRecord(
            records.dstream_data_id[old_id],  // dstream_data_id
            new_id,  // id
            id_remap[  // ancestor_id
              records.ancestor_id[old_id]
            ],
            id_remap[  // search_ancestor_id
              records.search_ancestor_id[old_id]
            ],
            id_remap[  // search_first_child_id
              records.search_first_child_id[old_id]
            ],
            id_remap[  // search_next_sibling_id
              records.search_next_sibling_id[old_id]
            ],
            records.rank[old_id],
            records.differentia[old_id]
        );
      }
      return int{}; // no-op return value
    }
  );

  assert(std::equal(
    std::begin(new_records.id),
    std::end(new_records.id),
    CountingIterator<u64>{}
  ));

  const auto logging_info = py::module::import("logging").attr("info");
  logging_info(
    py::str(
      "collapsing dropped unifurcations removed {} of {} records, {} remain"
    ).format(
      records.size() - new_records.size(),
      records.size(),
      new_records.size()
    )
  );

  return new_records;
}

/**
 * A makeshift iterator for children, called like this:
 *
 *   ChildrenGenerator iter(records, node);
 *   while ((child = iter.next())) {
 *     ...
 *   }
 *
 * Returns a value of 0 when there is no more children.
 */
class ChildrenGenerator {
private:
  const Records &records;
  u64 prev;
  const u64 node;

public:
  ChildrenGenerator(
    const Records &records, const u64 node
  ) : records(records), prev(0), node(node) {}

  u64 next() {
    u64 cur;
    if (!this->prev) {
      this->prev = this->node;
      cur = this->records.search_first_child_id[this->node];
    } else {
      cur = this->records.search_next_sibling_id[this->prev];
    }
    if (this->prev == cur) {
      return 0;
    }
    this->prev = cur;
    return this->prev;
  }

};


/**
 * A more permissive declval.
*/
template<class T> T& permissive_declval() {
  std::abort();
  return *static_cast<T*>(nullptr);
}


/**
 * A sentinel type for the ChildrenView range.
 */
struct ChildrenSentinel {};


/**
 * STL-compatible iterator for children of a node.
 */
class ChildrenIterator {
  std::reference_wrapper<const Records> records;
  u64 current;
public:
  using value_type = u64;
  using difference_type = std::ptrdiff_t;
  using iterator_category = std::input_iterator_tag;
  using iterator_concept = std::input_iterator_tag;

  // some compilers require iterators to be default-constructible...
  // this should never actually be used
  ChildrenIterator() : records(permissive_declval<Records>()) { }

  ChildrenIterator(const Records& records, u64 parent)
  : records(records)
  , current(
    records.search_first_child_id[parent] == parent
    ? 0
    : records.search_first_child_id[parent]
  )
  { }
  u64 operator*() const { return current; }
  ChildrenIterator& operator++() {
    const auto& records = this->records.get();
    const auto next = records.search_next_sibling_id[current];
    current = (next == current) ? 0 : next;
    return *this;
  }
  void operator++(int) { ++(*this); }
  friend bool operator==(const ChildrenIterator &it, ChildrenSentinel) {
    return it.current == 0;
  }
  friend bool operator==(ChildrenSentinel, const ChildrenIterator &it) {
    return it.current == 0;
  }
};


/**
 * A STL-compatible range view over the children of a node.
 */
struct ChildrenView : public std::ranges::view_interface<ChildrenView> {
  ChildrenView(const Records &records, const u64 parent)
    : records(records), parent(parent) {}
  ChildrenIterator begin() const { return ChildrenIterator{records, parent}; }
  ChildrenSentinel end() const { return {}; }
private:
  std::reference_wrapper<const Records> records;
  u64 parent;
};
static_assert(std::input_iterator<ChildrenIterator>);
static_assert(std::sentinel_for<ChildrenSentinel, ChildrenIterator>);
static_assert(std::ranges::range<ChildrenView>);
static_assert(std::ranges::input_range<ChildrenView>);


/**
 * Removes `node` from the children of its parent. See the
 * information on Records for how children are stored.
 *
 * @see attach_search_parent
 * @see Records
 */
void detach_search_parent(Records &records, const u64 node) {
  const u64 parent = records.search_ancestor_id[node];
  const u64 next_sibling = records.search_next_sibling_id[node];
  const bool is_last_child = next_sibling == node;

  if (records.search_first_child_id[parent] == node) {
    const u64 child_id = is_last_child ? parent : next_sibling;
    records.search_first_child_id[parent] = child_id;
  } else {
    // removes from the linked list of children
    const auto children_range = ChildrenView(records, parent);
    const auto sibling = std::ranges::find_if(
      children_range,
      [node, &records](const u64 child) {
        return records.search_next_sibling_id[child] == node;
      }
    );
    if (sibling != children_range.end()) {
      const u64 sibling_id = is_last_child ? *sibling : next_sibling;
      records.search_next_sibling_id[*sibling] = sibling_id;
    }
  }

  records.search_ancestor_id[node] = node;
  records.search_next_sibling_id[node] = node;
}


/**
 * Attaches `node` to the children of `parent`.
 *
 * @see detach_search_parent
 * @see Records
 */
void attach_search_parent(Records &records, const u64 node, const u64 parent) {
  if (records.search_ancestor_id[node] == parent) {
    return;
  }

  records.search_ancestor_id[node] = parent;

  const u64 ancestor_first_child = records.search_first_child_id[parent];
  const bool is_first_child = ancestor_first_child == parent;
  const u64 sibling_id = is_first_child ? node : ancestor_first_child;
  records.search_next_sibling_id[node] = sibling_id;
  records.search_first_child_id[parent] = node;

}


/**
 * Implementation of collapse_indistinguishable_nodes optimized for small
 * differentia sizes (e.g., a byte or less).
 *
 * @see consolidate_trie
 */
template<size_t max_differentia>
void collapse_indistinguishable_nodes_small(Records &records, const u64 node) {
  std::array<u64, max_differentia + 1> winners{};
  std::vector<std::tuple<u64, u64>> losers_with_differentiae;

  for (auto child : ChildrenView(records, node)) {
    const u64 differentia = records.differentia[child];
    auto& winner = winners[differentia];
    if (winner == 0 || child < winner) { std::swap(winner, child); }
    if (child) losers_with_differentiae.push_back({child, differentia});
  }
  for (const auto& [loser, differentia] : losers_with_differentiae) {
    const u64 winner = winners[differentia];

    std::vector<u64> loser_children;
    std::ranges::copy(
      ChildrenView(records, loser), std::back_inserter(loser_children)
    );
    for (const u64 loser_child : loser_children) {
      detach_search_parent(records, loser_child);
      attach_search_parent(records, loser_child, winner);
    }
    detach_search_parent(records, loser);
  }
}

/**
 * Implementation of collapse_indistinguishable_nodes optimized for large
 * differentia sizes (e.g., larger than a byte).
 */
void collapse_indistinguishable_nodes_large(Records &records, const u64 node) {
  std::unordered_map<u64, std::vector<u64>> groups;
  ChildrenGenerator gen(records, node);
  u64 child;
  while ((child = gen.next())) {  // consider what we are using as the key here
    std::vector<u64> &items = groups[records.differentia[child]];
    items.insert(std::lower_bound(items.begin(), items.end(), child), child);
  }
  for (auto [_, children] : groups) {
    const u64 winner = children[0];
    for (u64 i = 1; i < children.size(); ++i) {
      const u64 loser = children[i];

      std::vector<u64> loser_children;
      ChildrenGenerator loser_children_gen(records, loser);
      u64 loser_child;
      while ((loser_child = loser_children_gen.next())) {
        loser_children.push_back(loser_child);
      }
      for (const u64 loser_child : loser_children) {
        detach_search_parent(records, loser_child);
        attach_search_parent(records, loser_child, winner);
      }
      detach_search_parent(records, loser);
    }
  }
}


/**
 * Returns the number of bits in the binary representation
 * of `x`. This is used to determine which collapse function
 * to use.
 *
 * Adapted from https://stackoverflow.com/a/74374791/17332200
 */
int bit_length(const u64 x) { return (8*sizeof x) - std::countl_zero(x); }


/**
 * When consolidating a trie (see below), it may be the
 * case that a parent has duplicate children. This function
 * detects duplicates, chooses a winning duplicate, and
 * attaches all of the losers' children to the winner.
 *
 * Dispatches to implementation functions based on the differentia size, as
 * determined by the max_differentia field of the records.
 *
 * @see consolidate_trie
 *
 */
void collapse_indistinguishable_nodes(Records & records, const u64 node) {
  switch (bit_length(records.max_differentia)) {
    case 0:
    case 1:  // single-bit case
      collapse_indistinguishable_nodes_small<1>(records, node);
      break;
    case 2:  // two-bit case
      collapse_indistinguishable_nodes_small<2>(records, node);
      break;
    case 3:
    case 4:  // four-bit (hex value) case
      collapse_indistinguishable_nodes_small<4>(records, node);
      break;
    case 5:
    case 6:
    case 7:
    case 8:  // eight-bit (byte value) case
      collapse_indistinguishable_nodes_small<8>(records, node);
      break;
    default:  // larger than a byte
      collapse_indistinguishable_nodes_large(records, node);
  }
}


/**
 * Artifacts are sorted by number of strata deposited ascending,
 * so when the function comes across a rank that has been dropped,
 * we know it is irrelevant throughout the rest of the run. Therefore,
 * this function drops all *search* children (note, true parent
 * data is still stored in `ancestor_id`) and attaches the search
 * children of those children to the node. Then, attaching children
 * becomes much faster, avoiding deep searches.
 *
 * @see collapse_indistinguishable_nodes
 */
void consolidate_trie(Records &records, const u64 &rank, const u64 node) {
  const auto children_range = ChildrenView(records, node);
  if (
    children_range.begin() == children_range.end()
    || records.rank[*children_range.begin()] == rank
  ) return;

  std::vector<u64> node_stack;
  std::ranges::copy(children_range, std::back_inserter(node_stack));

  // drop children and attach grandchildren
  while (!node_stack.empty()) {
    const u64 popped_node = node_stack.back();
    node_stack.pop_back();
    detach_search_parent(records, popped_node);

    std::vector<u64> grandchildren;
    const auto grandchildren_range = ChildrenView(records, popped_node);
    std::ranges::copy(grandchildren_range, std::back_inserter(grandchildren));

    for (const u64 grandchild : grandchildren) {
      if (records.rank[grandchild] >= rank) {
        detach_search_parent(records, grandchild);
        attach_search_parent(records, grandchild, node);
      } else {
        node_stack.push_back(grandchild);
      }
    }
  }

  collapse_indistinguishable_nodes(records, node);
}


/**
 * Adds a record to the searchtable. Note that this
 * is the only function that adds records.
 */
u64 create_offstring(
  Records &records,
  const u64 parent,
  const u64 rank,
  const u64 differentia,
  const u64 data_id
) {
  const u64 node = records.size();
  records.addRecord(data_id, node, parent, node, node, node, rank, differentia);
  attach_search_parent(records, node, parent);
  return node;
}


/**
 * Inserts one rank-differentia pair into the trie.
 *
 * @see insert_artifact
 */
u64 place_allele(
  Records &records,
  const u64 cur_node,
  const u64 rank,
  const u64 differentia
) {
  const auto range = ChildrenView(records, cur_node);
  const auto match = std::ranges::find_if(
    range,
    [rank, differentia, &records](const u64 child){
      return (
        rank == records.rank[child]
        && differentia == records.differentia[child]
      );
    }
  );
  if (match != range.end()) {
    return *match;
  } else {
    const u64 dummy_data_id{u64_max};
    return create_offstring(
      records, cur_node, rank, differentia, dummy_data_id
    );
  }
}


/**
 * A simple iterator over a py::array_t. For more details,
 * view py_array_span.
 *
 * @see py_array_span
 */
template <typename T> struct py_array_span_iter {
  const py::detail::unchecked_reference<T, 1> &data_accessor;
  u64 index;

  using difference_type = std::ptrdiff_t;
  using value_type = T;
  using pointer = T*;
  using reference = T&;
  using iterator_category = std::input_iterator_tag;

  py_array_span_iter(
    const py::detail::unchecked_reference<T, 1> &data_accessor,
    const u64 index
  ) : data_accessor(data_accessor), index(index) {}

  u64 operator*() const { return this->data_accessor[this->index]; }

  py_array_span_iter & operator++() { ++this->index; return *this; }

  bool operator!=(const py_array_span_iter &other) const {
    return this->index != other.index;
  }

  bool operator==(const py_array_span_iter &other) const {
    return this->index == other.index;
  }

};


/**
 * A makeshift span over a pybind11::array_t using an
 * unchecked_reference. Only supports the indexing and
 * a .size() call. The unchecked_reference is used for
 * performance reasons, avoiding index validation.
 */
template <typename T> struct py_array_span {

  const py::detail::unchecked_reference<T, 1> &data_accessor;
  const u64 begin_;
  const u64 end_;

  u64 size() const { return this->end_ - this->begin_; }

  u64 operator[](const u64 index) const {
    return this->data_accessor[this->begin_ + index];
  }

  auto begin() { return py_array_span_iter{data_accessor, this->begin_}; }

  auto end() { return py_array_span_iter{data_accessor, this->end_}; }

  py_array_span(
    const py::detail::unchecked_reference<T, 1> &data,
    const u64 begin,
    const u64 end
  ) : data_accessor(data), begin_(begin), end_(end) {};

};


/**
 * Adds a single artifact (a.k.a specimen, column) to the
 * searchtable. Accesses the artifact using a span.
 *
 * @see py_array_span
 * @see place_allele
 */
template <typename SPAN_T>
void insert_artifact(
  Records &records,
  SPAN_T &&ranks,
  SPAN_T &&differentiae,
  const u64 data_id,
  const u64 num_strata_deposited
) {
  assert(ranks.size() == differentiae.size());
  u64 cur_node = 0;
  for (u64 i = 0; i < ranks.size(); ++i) {
    const u64 r = ranks[i];
    const u64 d = differentiae[i];
    consolidate_trie(records, r, cur_node);
    cur_node = place_allele(records, cur_node, r, d);
  }
  create_offstring(records, cur_node, num_strata_deposited - 1, -1, data_id);
}


/**
 * Consumes the given sequence and uses its data to create
 * a py::array_t without needing to do any copy operations.
 *
 * https://github.com/pybind/pybind11/issues/1042#issuecomment-2262727578
 */
template <typename Sequence>
inline pybind11::array_t<typename Sequence::value_type> as_pyarray(
  Sequence &&seq
) {
    const auto seq_size = seq.size();
    const auto seq_data = seq.data();
    std::unique_ptr<Sequence> seq_ptr = std::make_unique<Sequence>(
      std::move(seq)
    );
    auto capsule = pybind11::capsule(
      seq_ptr.get(),
      [](void *p) {
        std::unique_ptr<Sequence>(reinterpret_cast<Sequence *>(p));
      }
    );
    seq_ptr.release();

    return pybind11::array(
      {seq_size},
      {sizeof(typename Sequence::value_type)},
      seq_data,
      capsule
    );
}


/**
 * Converts a Records object to a py::dict of numpy arrays.
 *
 * Data is moved out of the Records object, so no copies are made. The Records
 * object is left in a valid but unspecified state.
 */
py::dict records_to_dict(Records &records) {
  std::unordered_map<std::string, py::array_t<u64>> return_mapping;
  return_mapping.insert(
    {"rank", as_pyarray(std::move(records.rank))}
  );
  return_mapping.insert(
    {"differentia", as_pyarray(std::move(records.differentia))}
  );
  return_mapping.insert(
    {"id", as_pyarray(std::move(records.id))}
  );
  return_mapping.insert(
    {"ancestor_id", as_pyarray(std::move(records.ancestor_id))}
  );
  return_mapping.insert(
    {"dstream_data_id", as_pyarray(std::move(records.dstream_data_id))}
  );
  return py::cast(return_mapping);
}


struct ProgressBar {

  py::object _pbar;

  ProgressBar(py::object pbar) : _pbar(pbar) {}

  ~ProgressBar() { this->_pbar.attr("close")(); }

  void operator()() { this->_pbar.attr("update")(1); }

};


/**
 * Constructs the trie in the case where each element in each
 * of the below vectors represents a unique artifact. Includes
 * logging and an optional tqdm progress bar.
 *
 * @see build_trie_searchtable_exploded
 */
py::dict build_trie_searchtable_nested(
  const std::vector<u64> &data_ids,
  const std::vector<u64> &num_strata_depositeds,
  const std::vector<std::vector<u64>> &ranks,
  const std::vector<std::vector<u64>> &differentiae,
  const py::handle &progress_ctor
) {
  Records records{static_cast<u64>(data_ids.size())};
  assert(
    data_ids.size() == num_strata_depositeds.size()
    && data_ids.size() == ranks.size()
    && data_ids.size() == differentiae.size()
  );

  if (!data_ids.size()) { return py::dict{}; }

  const auto logging_info = py::module::import("logging").attr("info");
  logging_info("nested searchtable cpp begin");

  {
    ProgressBar pbar{progress_ctor("total"_a=ranks.size())};

    for (u64 i = 0; i < ranks.size(); ++i) {
      insert_artifact(
        records,
        std::span<const u64>(ranks[i]),
        std::span<const u64>(differentiae[i]),
        data_ids[i],
        num_strata_depositeds[i]
      );
      pbar();
    }

  }  // end progress bar scope

  logging_info("nested searchtable cpp complete");
  return records_to_dict(records);
}


/**
 * A helper function to count the number of unique items in an
 * array. This is similar to std::unique but does not mutate.
 */
template <typename ITER>
u64 count_unique_elements(ITER begin, ITER end) {

  if (begin == end) { return 0; }

  return std::count_if(
    begin,
    end,
    [last = *begin](const auto &item) mutable {
      const bool is_unique = last != item;
      last = item;
      return is_unique;
    }
  ) + 1;

}


/**
 * Extends a records object with new artifacts. This function allows for
 * source data to be exploded in chunks, reducing memory pressure. The supplied
 * records object is modified in place.
 *
 * Note that sequential calls to this function must be made with artifacts in
 * ascending order by num_strata_deposited and that the data_ids array must be
 * partitioned cleanly across calls (i.e., no data_id should be split across
 * calls).
 *
 * Includes logging and an optional tqdm progress bar.
 *
 * @see build_trie_searchtable_exploded : performs a one-pass (non-chunked)
 * build
 */
void extend_trie_searchtable_exploded(
  Records &records,
  const py::array_t<u64> &data_ids,
  const py::array_t<u64> &num_strata_depositeds,
  const py::array_t<u64> &ranks,
  const py::array_t<u64> &differentiae,
  const py::handle &progress_ctor
) {
  assert(
    data_ids.size() == num_strata_depositeds.size()
    && data_ids.size() == ranks.size()
    && data_ids.size() == differentiae.size()
  );

  if (!data_ids.size()) { return; }

  const auto data_ids_ = data_ids.unchecked<1>();
  const auto num_strata_depositeds_ = num_strata_depositeds.unchecked<1>();
  const auto ranks_ = ranks.unchecked<1>();
  const auto differentiae_ = differentiae.unchecked<1>();

  const auto logging_info = py::module::import("logging").attr("info");
  logging_info("exploded searchtable cpp begin");

  {
    const u64 total = [&data_ids_](){
      py_array_span<u64> span{
        data_ids_, 0, static_cast<u64>(data_ids_.size())
      };
      return count_unique_elements(span.begin(), span.end());
    }();
    ProgressBar pbar{progress_ctor("total"_a=total)};

    u64 end;
    for (u64 begin = 0; begin < static_cast<u64>(ranks.size()); begin = end) {
      for (end = begin; end < static_cast<u64>(ranks.size()); ++end) {
        if (data_ids_[begin] != data_ids_[end]) break;
      }  // ... fast forward to end of segment with contiguous identical data_id values

      insert_artifact(
        records,
        py_array_span<u64>(ranks_, begin, end),
        py_array_span<u64>(differentiae_, begin, end),
        data_ids_[begin],
        num_strata_depositeds_[begin]
      );
      pbar();

    }

    assert(std::cmp_greater_equal(records.size(), total));
  }  // end progress bar scope

  logging_info(
    py::str(
      "exploded searchtable cpp extension complete, num records is {}"
    ).format(records.size())
  );
}


/**
 * Constructs a trie from 1-dimensional representing a complete exploded
 * DataFrame. Unlike extend_trie_searchtable_exploded, this function creates and
 * a new Records object internally and returns a py::dict with construction
 * results.
 *
 * Includes logging and an optional tqdm progress bar.
 *
 * @see build_trie_searchtable_nested
 */
py::dict build_trie_searchtable_exploded(
  const py::array_t<u64> &data_ids,
  const py::array_t<u64> &num_strata_depositeds,
  const py::array_t<u64> &ranks,
  const py::array_t<u64> &differentiae,
  const py::handle &progress_ctor
) {
  Records records{static_cast<u64>(data_ids.size())};
  extend_trie_searchtable_exploded(
    records, data_ids, num_strata_depositeds, ranks, differentiae, progress_ctor
  );

  const auto logging_info = py::module::import("logging").attr("info");
  logging_info("exploded searchtable cpp complete");
  return records_to_dict(records);
}


PYBIND11_MODULE(_build_tree_searchtable_cpp_impl, m) {
  py::class_<Records>(m, "Records")
      .def(py::init<u64>(), py::arg("init_size"));
  m.def(
    "collapse_dropped_unifurcations",
    &collapse_dropped_unifurcations,
    py::arg("records")
  );
  m.def(
    "records_to_dict",
    &records_to_dict,
    py::arg("records")
  );
  m.def(
    "extend_tree_searchtable_cpp_from_exploded",
    &extend_trie_searchtable_exploded,
    py::arg("records"),
    py::arg("data_ids"),
    py::arg("num_strata_depositeds"),
    py::arg("ranks"),
    py::arg("differentiae"),
    py::arg("progress_bar")
  );
  m.def(
    "build_tree_searchtable_cpp_from_exploded",
    &build_trie_searchtable_exploded,
    py::arg("data_ids"),
    py::arg("num_strata_depositeds"),
    py::arg("ranks"),
    py::arg("differentiae"),
    py::arg("progress_bar")
  );
  m.def(
    "build_tree_searchtable_cpp_from_nested",
    &build_trie_searchtable_nested,
    py::arg("data_ids"),
    py::arg("num_strata_depositeds"),
    py::arg("ranks"),
    py::arg("differentiae"),
    py::arg("progress_bar")
  );
}


/*
<%
cfg['extra_compile_args'] = ['-std=c++20', '-Wall', '-Wextra', '-DDEBUG']
setup_pybind11(cfg)
%>
*/
