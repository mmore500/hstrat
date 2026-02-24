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

typedef int64_t i64;
typedef uint64_t u64;
constexpr u64 placeholder_value = std::numeric_limits<int64_t>::max();

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
  std::vector<u64> search_prev_sibling_id;
  std::vector<u64> search_next_sibling_id;
  std::vector<u64> search_ancestor_id;
  std::vector<u64> ancestor_id;
  std::vector<u64> differentia;
  std::vector<i64> rank;
  u64 max_differentia = 0;

  explicit Records(const u64 init_size, const bool init_root=true) {
    this->dstream_data_id.reserve(init_size);
    this->id.reserve(init_size);
    this->search_first_child_id.reserve(init_size);
    this->search_prev_sibling_id.reserve(init_size);
    this->search_next_sibling_id.reserve(init_size);
    this->search_ancestor_id.reserve(init_size);
    this->ancestor_id.reserve(init_size);
    this->differentia.reserve(init_size);
    this->rank.reserve(init_size);

    if (init_root) {
      this->addRecord(placeholder_value, 0, 0, 0, 0, 0, 0, 0, 0); // root node
    }
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
    const u64 search_prev_sibling_id,
    const u64 search_next_sibling_id,
    const i64 rank,
    const u64 differentia
  ) {
    assert(search_first_child_id >= id);
    assert(this->size() == 0 || ancestor_id != id);
    assert(this->size() == 0 || this->rank[ancestor_id] <= rank);
    this->dstream_data_id.push_back(data_id);
    this->id.push_back(id);
    this->search_first_child_id.push_back(search_first_child_id);
    this->search_prev_sibling_id.push_back(search_prev_sibling_id);
    this->search_next_sibling_id.push_back(search_next_sibling_id);
    this->search_ancestor_id.push_back(search_ancestor_id);
    this->ancestor_id.push_back(ancestor_id);
    this->differentia.push_back(differentia);
    this->rank.push_back(rank);
    max_differentia = std::max(max_differentia, differentia);
    assert(
      search_ancestor_id == placeholder_value
      || this->rank[search_ancestor_id] <= rank
    );
  }

  u64 size() const { return this->dstream_data_id.size(); }

};


/**
 *  Delete records w/ one parent and one child (unifurcations) to save memory.
 *
 *  If dropped_only=True, removes record entries that are unifurcations and are
 *  associated with dropped ranks (i.e., by current num_strata_deposited,
 *  differentiae at those ranks have been purged. This operation may be called
 *  at any point(s) during trie construction.
 *
 *  Note that detection of dropped ranks is incomplete, as it is based on the
 *  reconfiguration of the search trie. A more comprehensive approach could
 *  collate dropped ranks across all records.
 *
 *  If dropped_only=False, removes all unifurcations. Note that this should only
 *  be called if no more records will be added to the trie (i.e., reconstruction
 *  is complete).
 */
Records collapse_unifurcations(Records &records, const bool dropped_only) {
  assert(std::equal(
    std::begin(records.id),
    std::end(records.id),
    CountingIterator<u64>{}
  ));
  if (records.size() == 0) return Records(0, /* init_root= */ false);
  else if (records.size() == 1) return Records(1, /* init_root= */ true);

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
      // increment preventing overflow (anything past 2 is equivalent)
      ref_count = std::min(ref_count + 1, 2);
    }
  );

  // a.k.a. should_keeps; ref to save memory
  auto& is_not_selected_unifurcation = ancestor_ref_counts;
  std::transform(
    std::begin(records.id),
    std::end(records.id),
    std::begin(ancestor_ref_counts),
    std::begin(is_not_selected_unifurcation),  // output iterator
    [&records, dropped_only](
      const u64 id, const uint8_t ancestor_ref_count
    ) {
      const bool is_unifurcation = ancestor_ref_count == 1;
      const bool is_dropped = (
        records.ancestor_id[id] != id
        and records.search_ancestor_id[id] == id
      );
      const bool is_selected = dropped_only ? is_dropped : true;
      const bool is_selected_unifurcation = is_unifurcation and is_selected;
      return !is_selected_unifurcation;
    }
  );

  // maps position [old id] to new, contiguously assigned id
  std::vector<u64> id_remap;
  id_remap.reserve(records.size());

  // set up id_remap ansatz; number of preceding kept items
  assert(!is_not_selected_unifurcation.empty());
  id_remap.push_back(0);
  std::partial_sum(
    as_u64_iterator(std::begin(is_not_selected_unifurcation)),
    as_u64_iterator(std::prev(std::end(is_not_selected_unifurcation))),
    std::back_inserter(id_remap),
    std::plus<u64>{}
  );

  // fill id_remap with reassigned ids
  std::transform(
    std::begin(records.id),
    std::end(records.id),
    std::begin(id_remap),
    std::begin(id_remap),
    [&id_remap, &records, &is_not_selected_unifurcation](
      const u64 id, const u64 ansatz
    ) {
      const bool should_keep = is_not_selected_unifurcation[id];
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
    [&is_not_selected_unifurcation, &id_remap, &new_records, &records, dropped_only](
      const u64 old_id, const u64 new_id
    ) {
        const bool should_keep = is_not_selected_unifurcation[old_id];
        if (!should_keep) return int{}; // no-op return value

        assert(new_id == new_records.size());
        assert(new_id <= old_id);

        if (dropped_only) {
          assert(is_not_selected_unifurcation[
            records.search_ancestor_id[old_id]
          ]);
          assert(is_not_selected_unifurcation[
            records.search_first_child_id[old_id]
          ]);
          assert(is_not_selected_unifurcation[
            records.search_next_sibling_id[old_id]
          ]);
        }

        assert(records.search_ancestor_id[old_id] <= old_id);
        assert(id_remap[records.search_ancestor_id[old_id]] <= new_id);
        assert(records.rank[old_id] >= records.rank[
          records.search_ancestor_id[old_id]
        ]);

        new_records.addRecord(
          records.dstream_data_id[old_id],  // dstream_data_id
          new_id,  // id
          id_remap[  // ancestor_id
            records.ancestor_id[old_id]
          ],
          dropped_only ? id_remap[  // search_ancestor_id
            records.search_ancestor_id[old_id]
          ] : placeholder_value,
          dropped_only ? id_remap[  // search_first_child_id
            records.search_first_child_id[old_id]
          ] : placeholder_value,
          dropped_only ? id_remap[  // search_prev_sibling_id
            records.search_prev_sibling_id[old_id]
          ] : placeholder_value,
          dropped_only ? id_remap[  // search_next_sibling_id
            records.search_next_sibling_id[old_id]
          ] : placeholder_value,
          records.rank[old_id],
          records.differentia[old_id]
      );

      assert(records.rank[old_id] >= new_records.rank[
        id_remap[records.search_ancestor_id[old_id]]
      ]);
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
  using iterator_category = std::forward_iterator_tag;
  using iterator_concept = std::forward_iterator_tag;

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
  { assert(this->current != placeholder_value); }

  bool operator==(const ChildrenIterator &it) const {
    return this->current == it.current;
  }
  bool operator!=(const ChildrenIterator &it) const {
    return this->current != it.current;
  }

  u64 operator*() const { return current; }
  ChildrenIterator& operator++() {
    const auto& records = this->records.get();
    const auto next = records.search_next_sibling_id[current];
    assert(next != placeholder_value);
    current = (next == current) ? 0 : next;
    return *this;
  }
  ChildrenIterator operator++(int) {
    ChildrenIterator tmp = *this;
    ++(*this);
    return tmp;
  }

  friend bool operator==(const ChildrenIterator &it, ChildrenSentinel) {
    return it.current == 0;
  }
  friend bool operator==(ChildrenSentinel, const ChildrenIterator &it) {
    return it.current == 0;
  }
  friend bool operator!=(const ChildrenIterator &it, ChildrenSentinel) {
    return it.current != 0;
  }
  friend bool operator!=(ChildrenSentinel, const ChildrenIterator &it) {
    return it.current != 0;
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

static_assert(std::forward_iterator<ChildrenIterator>);
static_assert(std::sentinel_for<ChildrenSentinel, ChildrenIterator>);
static_assert(std::ranges::forward_range<ChildrenView>);


/**
 * Removes `node` from the children of its parent. See the
 * information on Records for how children are stored.
 *
 * @see attach_search_parent
 * @see Records
 */
void detach_search_parent(Records &records, const u64 node) {
  const u64 parent = records.search_ancestor_id[node];
  assert(parent != placeholder_value);
  const u64 next_sibling = records.search_next_sibling_id[node];
  const bool is_last_child = next_sibling == node;

  if (records.search_first_child_id[parent] == node) {
    const u64 child_id = is_last_child ? parent : next_sibling;
    records.search_first_child_id[parent] = child_id;
    // mark next sibling as new first child (otherwise harmlessly mark self)
    if (is_last_child) assert(next_sibling == node);
    records.search_prev_sibling_id[next_sibling] = next_sibling;
  } else if (records.search_next_sibling_id[node] == node) {
    const u64 prev_sibling = records.search_prev_sibling_id[node];
    records.search_next_sibling_id[prev_sibling] = prev_sibling;
  } else {
    const u64 prev_sibling = records.search_prev_sibling_id[node];
    const u64 next_sibling = records.search_next_sibling_id[node];
    records.search_next_sibling_id[prev_sibling] = next_sibling;
    records.search_prev_sibling_id[next_sibling] = prev_sibling;
  }

  records.search_ancestor_id[node] = node;
  records.search_prev_sibling_id[node] = node;
  records.search_next_sibling_id[node] = node;
}


/**
 * Attaches `node` to the children of `parent`.
 *
 * @see detach_search_parent
 * @see Records
 */
void attach_search_parent(Records &records, const u64 node, const u64 parent) {
  assert(records.search_ancestor_id[node] != placeholder_value);
  if (records.search_ancestor_id[node] == parent) {
    return;
  }

  records.search_ancestor_id[node] = parent;
  assert(parent <= node);
  assert(records.rank[parent] <= records.rank[node]);
  assert(records.search_first_child_id[parent] != placeholder_value);

  // insert node into the list of children, choosing its position in order
  // to keep the list in ascending order by rank
  const i64 rank = records.rank[node];
  const auto siblings = ChildrenView(records, parent);
  u64 precursor_id = parent;
  const auto next_sibling_it = std::ranges::find_if(
    siblings,
    [&records, &precursor_id, rank](const u64 sibling){
      const bool res = records.rank[sibling] >= rank;
      if (!res) precursor_id = sibling;
      return res;
    }
  );

  const bool has_next_sibling = next_sibling_it != siblings.end();
  const bool has_prev_sibling = next_sibling_it != siblings.begin();

  if (has_prev_sibling) {
    assert(
      !has_next_sibling
      || records.search_prev_sibling_id[*next_sibling_it] == precursor_id
    );
    assert(precursor_id != parent);
    records.search_next_sibling_id[precursor_id] = node;
    records.search_prev_sibling_id[node] = precursor_id;
  } else {
    assert(precursor_id == parent);
    records.search_first_child_id[parent] = node;
    records.search_prev_sibling_id[node] = node;
  }

  if (has_next_sibling) {
    records.search_prev_sibling_id[*next_sibling_it] = node;
    records.search_next_sibling_id[node] = *next_sibling_it;
  } else {
    records.search_next_sibling_id[node] = node;
  }

  // full sorted check is too expensive to assert, so just check local sort...
  assert(
    records.rank[records.search_prev_sibling_id[node]]
    <= records.rank[node]
  );
  assert(
    records.rank[node]
    <= records.rank[records.search_next_sibling_id[node]]
  );

}


/**
 * Implementation of collapse_indistinguishable_nodes optimized for small
 * differentia sizes (e.g., a byte or less).
 *
 * @see consolidate_trie
 */
template<size_t max_differentia>
void collapse_indistinguishable_nodes_small(Records &records, const u64 node) {

  assert(std::ranges::is_sorted(
    ChildrenView(records, node),
    [&records](const u64 lhs, const u64 rhs) {
      return records.rank[lhs] < records.rank[rhs];
    }
  ));
  assert(std::ranges::all_of(
    ChildrenView(records, node),
    [&records](const u64 child){ return records.rank[child] >= 0; }
  ));

  std::array<std::vector<u64>, max_differentia + 1> losers{};
  std::array<std::vector<u64>, max_differentia + 1> loser_epochs{};
  std::array<std::vector<u64>, max_differentia + 1> epoch_winners{};
  std::array<i64, max_differentia + 1> prev_child_rank{};
  for (const auto child : ChildrenView(records, node)) {
    assert(child > 0);

    const auto child_d = records.differentia[child];
    assert(child_d <= max_differentia);

    const auto child_r = records.rank[child];
    assert(child_r > 0 && child_r >= prev_child_rank[child_d]);

    const auto d = child_d;
    if (child_r != std::exchange(prev_child_rank[d], child_r)) {
      epoch_winners[d].push_back(child);
    } else {
      const auto cur_winner = epoch_winners[d].back();
      assert(cur_winner != child);
      epoch_winners[d].back() = std::min(cur_winner, child);
      const auto cur_loser = std::max(cur_winner, child);
      losers[d].push_back(cur_loser);
      loser_epochs[d].push_back(epoch_winners[d].size() - 1);
    }
  }

  // possible optimization: could track which differentia values have been seen
  for (u64 d = 0; d <= max_differentia; ++d) {

    assert(losers[d].size() == loser_epochs[d].size());
    for (u64 i{}; i < losers[d].size(); ++i) {
      const auto loser = losers[d][i];
      const auto loser_epoch = loser_epochs[d][i];
      const auto corresponding_winner = epoch_winners[d][loser_epoch];

      std::vector<u64> loser_children;
      std::ranges::copy(
        ChildrenView(records, loser), std::back_inserter(loser_children)
      );
      for (const u64 loser_child : loser_children) {
        detach_search_parent(records, loser_child);
        attach_search_parent(records, loser_child, corresponding_winner);
      }
      detach_search_parent(records, loser);
    }

    assert(std::ranges::is_sorted(loser_epochs[d]));
    for (const auto loser_epoch : std::ranges::unique(loser_epochs[d])) {
      const auto true_winner = epoch_winners[d][loser_epoch];
      collapse_indistinguishable_nodes_small<max_differentia>(
        records, true_winner
      );
    }

  }

}

// adapted from https://stackoverflow.com/a/20602159/17332200
struct pairhash {
  size_t operator()(const std::pair<u64, u64>& arr) const {
    return std::hash<u64>{}(arr.first) ^ std::hash<u64>{}(arr.second);
  }
};

/**
 * Implementation of collapse_indistinguishable_nodes optimized for large
 * differentia sizes (e.g., larger than a byte).
 */
void collapse_indistinguishable_nodes_large(Records &records, const u64 node) {
  std::unordered_map<std::pair<i64, u64>, std::vector<u64>, pairhash> groups;
  for (const u64 child : ChildrenView(records, node)) {
    std::vector<u64> &items = groups[
      std::pair{records.rank[child], records.differentia[child]}
    ];
    items.insert(std::lower_bound(items.begin(), items.end(), child), child);
  }
  for (auto [_, children] : groups) {
    const u64 winner = children[0];
    for (u64 i = 1; i < children.size(); ++i) {
      const u64 loser = children[i];

      std::vector<u64> loser_children;
      for (const u64 loser_child : ChildrenView(records, loser)) {
        loser_children.push_back(loser_child);
      }
      for (const u64 loser_child : loser_children) {
        detach_search_parent(records, loser_child);
        attach_search_parent(records, loser_child, winner);
      }
      detach_search_parent(records, loser);
    }

    if (children.size() > 1) {
      collapse_indistinguishable_nodes_large(records, winner);
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
    case 1:  // single-bit case: values 0-1
      collapse_indistinguishable_nodes_small<1>(records, node);
      break;
    case 2:  // two-bit case: values 0-3
      collapse_indistinguishable_nodes_small<3>(records, node);
      break;
    case 3:
    case 4:  // four-bit (hex value) case: values 0-15
      collapse_indistinguishable_nodes_small<15>(records, node);
      break;
    case 5:
    case 6:
    case 7:
    case 8:  // eight-bit (byte value) case: values 0-255
      collapse_indistinguishable_nodes_small<255>(records, node);
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
void consolidate_trie(Records &records, const i64 rank, const u64 node) {
  const auto children_range = ChildrenView(records, node);
  assert(std::ranges::all_of(
    children_range,
    [&records, rank](const u64 child){ return records.rank[child] <= rank; }
  ));

  if (
    children_range.begin() == children_range.end()
    // chidlren are stored in ascending order by rank
    || records.rank[*children_range.begin()] == rank
  ) [[likely]] {
    assert(std::ranges::all_of(
      children_range,
      [&records, rank](const u64 child){ return records.rank[child] == rank; }
    ));
    return;
  }

  // children are stored in ascending order by rank, so this is equivalent
  // to copy_if < rank
  std::vector<u64> node_stack;
  const auto copy_end = std::ranges::find_if(
    children_range,
    [&records, rank](const u64 node){ return records.rank[node] == rank; }
  );
  std::ranges::copy(
    std::ranges::subrange(children_range.begin(), copy_end),
    std::back_inserter(node_stack)
  );

  assert(!node_stack.empty());

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
  const i64 rank,
  const u64 differentia,
  const u64 data_id
) {
  const u64 node = records.size();
  records.addRecord(
    data_id,  // data_id
    node,  // id
    parent,  // ancestor_id
    node,  // search_ancestor_id (note! search parent attached next below)
    node,  // search_first_child_id
    node,  // search_prev_sibling_id
    node,  // search_next_sibling_id
    rank,  // rank
    differentia  // differentia
  );
  const u64 dummy_data_id{placeholder_value};
  if (data_id == dummy_data_id) {  // i.e., not a leaf node
    attach_search_parent(records, node, parent);
  }
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
  const i64 rank,
  const u64 differentia
) {
  assert(records.rank[cur_node] <= rank);
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
    const u64 dummy_data_id{placeholder_value};
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
template <typename ISPAN_T, typename USPAN_T>
void insert_artifact(
  Records &records,
  ISPAN_T &&ranks,
  USPAN_T &&differentiae,
  const u64 data_id,
  const u64 num_strata_deposited
) {
  assert(ranks.size() == differentiae.size());
  u64 cur_node = 0;
  for (u64 i = 0; i < ranks.size(); ++i) {
    const i64 r = ranks[i];
    const u64 d = differentiae[i];
    consolidate_trie(records, r, cur_node);
    cur_node = place_allele(records, cur_node, r, d);
  }
  create_offstring(records, cur_node, num_strata_deposited - 1, 0, data_id);
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
 * Nondestructively converts a Records object to a py::dict of lists.
 */
py::dict copy_records_to_dict(Records &records) {
  std::unordered_map<std::string, std::vector<u64>> return_mapping;
  return_mapping.insert({"dstream_data_id", records.dstream_data_id});
  return_mapping.insert({"id", records.id});
  return_mapping.insert(
    {"search_first_child_id", records.search_first_child_id}
  );
  return_mapping.insert(
    {"search_prev_sibling_id", records.search_prev_sibling_id}
  );
  return_mapping.insert(
    {"search_next_sibling_id", records.search_next_sibling_id}
  );
  return_mapping.insert({"search_ancestor_id", records.search_ancestor_id});
  return_mapping.insert({"ancestor_id", records.ancestor_id});
  return_mapping.insert({"differentia", records.differentia});
  py::dict res = py::cast(return_mapping);
  res["rank"] = records.rank;
  return res;
}


/**
 * Converts a Records object to a py::dict of numpy arrays.
 *
 * Data is moved out of the Records object, so no copies are made. The Records
 * object is left in a valid but unspecified state.
 */
py::dict extract_records_to_dict(Records &records) {
  std::unordered_map<std::string, py::array_t<u64>> return_mapping;
  return_mapping.insert(
    {"dstream_data_id", as_pyarray(std::move(records.dstream_data_id))}
  );
  return_mapping.insert(
    {"id", as_pyarray(std::move(records.id))}
  );
  return_mapping.insert(
    {"search_first_child_id", as_pyarray(
      std::move(records.search_first_child_id)
    )}
  );
  return_mapping.insert(
    {"search_prev_sibling_id", as_pyarray(
      std::move(records.search_prev_sibling_id)
    )}
  );
  return_mapping.insert(
    {"search_next_sibling_id", as_pyarray(
      std::move(records.search_next_sibling_id)
    )}
  );
  return_mapping.insert(
    {"search_ancestor_id", as_pyarray(
      std::move(records.search_ancestor_id)
    )}
  );
  return_mapping.insert(
    {"ancestor_id", as_pyarray(std::move(records.ancestor_id))}
  );
  return_mapping.insert(
    {"differentia", as_pyarray(std::move(records.differentia))}
  );
  py::dict res = py::cast(return_mapping);
  res["rank"] = as_pyarray(std::move(records.rank));
  return res;
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
 * Note that ranks must be in ascending order within each stratum.
 *
 * @see build_trie_searchtable_exploded
 */
py::dict build_trie_searchtable_nested(
  const std::vector<u64> &data_ids,
  const std::vector<u64> &num_strata_depositeds,
  const std::vector<std::vector<i64>> &ranks,
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
        std::span<const i64>(ranks[i]),
        std::span<const u64>(differentiae[i]),
        data_ids[i],
        num_strata_depositeds[i]
      );
      pbar();
    }

  }  // end progress bar scope

  logging_info("nested searchtable cpp complete");
  return extract_records_to_dict(records);
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
 * calls). Within each artifact, ranks must be in ascending order.
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
  const py::array_t<i64> &ranks,
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
        // ranks must be in ascending order
        else assert(begin == end || ranks_[end - 1] < ranks_[end]);
      }  // ... fast fwd to end of seg w/ contiguous identical data_id values

      insert_artifact(
        records,
        py_array_span<i64>(ranks_, begin, end),
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
 * Note that ranks must be in ascending order within each stratum.
 *
 * Includes logging and an optional tqdm progress bar.
 *
 * @see build_trie_searchtable_nested
 */
py::dict build_trie_searchtable_exploded(
  const py::array_t<u64> &data_ids,
  const py::array_t<u64> &num_strata_depositeds,
  const py::array_t<i64> &ranks,
  const py::array_t<u64> &differentiae,
  const py::handle &progress_ctor
) {
  Records records{static_cast<u64>(data_ids.size())};
  extend_trie_searchtable_exploded(
    records, data_ids, num_strata_depositeds, ranks, differentiae, progress_ctor
  );

  const auto logging_info = py::module::import("logging").attr("info");
  logging_info("exploded searchtable cpp complete");
  return extract_records_to_dict(records);
}


/**
 * Checks whether the search trie structure is present (not dismantled).
 * After collapse_unifurcations(dropped_only=false), search fields are set
 * to placeholder_value.
 */
bool _has_search_trie(const Records& records) {
  if (records.size() == 0) return false;
  return records.search_ancestor_id[0] != placeholder_value;
}


/**
 * Checks that record ids are contiguously assigned 0, 1, ..., n-1.
 */
bool check_trie_invariant_contiguous_ids(const Records& records) {
  return std::equal(
    std::begin(records.id), std::end(records.id), CountingIterator<u64>{}
  );
}


/**
 * Checks that ancestor ids reference earlier records (ancestor_id[i] <= i).
 */
bool check_trie_invariant_topologically_sorted(const Records& records) {
  return std::ranges::all_of(
    records.id,
    [&records](const u64 id) {
      return records.ancestor_id[id] <= id;
    }
  );
}


/**
 * Checks that parent ranks are <= child ranks for all non-root nodes.
 */
bool check_trie_invariant_chronologically_sorted(const Records& records) {
  return std::ranges::all_of(
    records.id,
    [&records](const u64 id) {
      return records.rank[records.ancestor_id[id]] <= records.rank[id];
    }
  );
}


/**
 * Checks that there is exactly one root (node with ancestor_id == id).
 */
bool check_trie_invariant_single_root(const Records& records) {
  if (records.size() == 0) return true;
  const u64 root_count = std::ranges::count_if(
    records.id,
    [&records](const u64 id) { return records.ancestor_id[id] == id; }
  );
  return root_count == 1;
}


/**
 * Checks that search child linked lists are well-formed:
 *   - first child's prev_sibling points to itself
 *   - last child's next_sibling points to itself
 *   - forward and backward pointers are consistent
 *   - all children's search_ancestor points to parent
 *   - no cycles in sibling list
 * Skips check if search trie is not present.
 */
bool check_trie_invariant_search_children_valid(const Records& records) {
  if (!_has_search_trie(records)) return true;

  for (u64 i = 0; i < records.size(); ++i) {
    const u64 first_child = records.search_first_child_id[i];
    if (first_child == placeholder_value) return false;

    if (first_child == i) continue;  // no children, OK

    if (first_child >= records.size()) return false;

    // first child's prev_sibling should be itself (signals head of list)
    if (records.search_prev_sibling_id[first_child] != first_child) {
      return false;
    }

    // walk the sibling list
    u64 cur = first_child;
    u64 count = 0;
    while (true) {
      if (cur >= records.size()) return false;

      // child's search_ancestor should point back to parent
      if (records.search_ancestor_id[cur] != i) return false;

      const u64 next = records.search_next_sibling_id[cur];
      if (next == cur) break;  // last sibling, OK

      if (next >= records.size()) return false;

      // backward pointer consistency
      if (records.search_prev_sibling_id[next] != cur) return false;

      cur = next;
      ++count;
      if (count > records.size()) return false;  // cycle detection
    }
  }
  return true;
}


/**
 * Checks that search children are sorted by rank in ascending order.
 * Skips check if search trie is not present.
 */
bool check_trie_invariant_search_children_sorted(const Records& records) {
  if (!_has_search_trie(records)) return true;

  for (u64 i = 0; i < records.size(); ++i) {
    const u64 first_child = records.search_first_child_id[i];
    if (first_child == i) continue;  // no children

    i64 prev_rank = records.rank[first_child];
    u64 cur = first_child;
    while (true) {
      const u64 next = records.search_next_sibling_id[cur];
      if (next == cur) break;

      if (records.rank[next] < prev_rank) return false;
      prev_rank = records.rank[next];
      cur = next;
    }
  }
  return true;
}


/**
 * Checks that no two children of the same parent share the same
 * (rank, differentia) pair.
 * Skips check if search trie is not present.
 */
bool check_trie_invariant_no_indistinguishable_nodes(const Records& records) {
  if (!_has_search_trie(records)) return true;

  for (u64 i = 0; i < records.size(); ++i) {
    const u64 first_child = records.search_first_child_id[i];
    if (first_child == i) continue;

    // collect children (rank, differentia) pairs and check for duplicates
    std::vector<std::pair<i64, u64>> child_pairs;
    for (const u64 child : ChildrenView(records, i)) {
      child_pairs.emplace_back(records.rank[child], records.differentia[child]);
    }

    std::ranges::sort(child_pairs);
    const auto dup = std::ranges::adjacent_find(child_pairs);
    if (dup != child_pairs.end()) return false;
  }
  return true;
}


/**
 * Checks that data nodes (dstream_data_id != placeholder_value) are leaf
 * nodes, i.e., have no search children.
 * Skips check if search trie is not present.
 */
bool check_trie_invariant_data_nodes_are_leaves(const Records& records) {
  if (!_has_search_trie(records)) return true;

  return std::ranges::all_of(
    records.id,
    [&records](const u64 id) {
      if (records.dstream_data_id[id] == placeholder_value) return true;
      return records.search_first_child_id[id] == id;
    }
  );
}


/**
 * Checks that search ancestors are compatible with the lineage trie.
 * For each node with a valid search_ancestor_id, walking up the lineage
 * trie via ancestor_id should find a node that is indistinguishable
 * from (i.e., same rank and differentia as) the search ancestor.
 *
 * Skips check if search trie is not present.
 */
bool check_trie_invariant_search_lineage_compatible(const Records& records) {
  if (!_has_search_trie(records)) return true;

  for (u64 i = 0; i < records.size(); ++i) {
    // only consider tips
    if (records.dstream_data_id[i] == placeholder_value) continue;

    assert(records.search_ancestor_id[i] == i);
    u64 a = records.ancestor_id[i];
    u64 s = a;
    while (a) {
      const auto rank_a = records.rank[a];
      const auto rank_s = records.rank[s];
      if (rank_a == rank_s) {
        if (records.differentia[a] != records.differentia[s]) return false;
      } else if (rank_a > rank_s) {
        a = records.ancestor_id[a];
        assert(records.rank[a] >= rank_s);
      } else if (records.search_ancestor_id[s] == s) {
        break;
      } else if (rank_s > rank_a) {
        s = records.search_ancestor_id[s];
        assert(records.rank[s] <= rank_a);
      } else assert(false);
    }
  }

  return true;
}


/**
 * Checks that all ancestor_id values reference valid indices.
 */
bool check_trie_invariant_ancestor_bounds(const Records& records) {
  return std::ranges::all_of(
    records.id,
    [&records](const u64 id) {
      return records.ancestor_id[id] < records.size();
    }
  );
}


/**
 * Checks that the root node is at index 0 with expected properties:
 *   - ancestor_id[0] == 0 (self-referencing)
 *   - rank[0] == 0
 */
bool check_trie_invariant_root_at_zero(const Records& records) {
  if (records.size() == 0) return true;
  return records.ancestor_id[0] == 0 && records.rank[0] == 0;
}


/**
 * Checks that all nodes have non-negative rank values.
 * Negative ranks would indicate data corruption.
 */
bool check_trie_invariant_ranks_nonnegative(const Records& records) {
  return std::ranges::all_of(
    records.id,
    [&records](const u64 id) {
      return records.rank[id] >= 0;
    }
  );
}


PYBIND11_MODULE(_build_tree_searchtable_cpp_impl, m) {
  m.attr("placeholder_value") = py::int_(placeholder_value);
  py::class_<Records>(m, "Records")
      .def(
        py::init<u64, bool>(),
        py::arg("init_size"),
        py::arg("init_root")=true
      )
      .def("__len__", &Records::size)
      .def("addRecord", &Records::addRecord,
        py::arg("data_id"),
        py::arg("id"),
        py::arg("ancestor_id"),
        py::arg("search_ancestor_id"),
        py::arg("search_first_child_id"),
        py::arg("search_prev_sibling_id"),
        py::arg("search_next_sibling_id"),
        py::arg("rank"),
        py::arg("differentia")
  );
  m.def(
    "collapse_unifurcations",
    &collapse_unifurcations,
    py::arg("records"),
    py::arg("dropped_only")
  );
  m.def(
    "copy_records_to_dict",
    &copy_records_to_dict,
    py::arg("records")
  );
  m.def(
    "extract_records_to_dict",
    &extract_records_to_dict,
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
  m.def(
    "check_trie_invariant_contiguous_ids",
    &check_trie_invariant_contiguous_ids,
    py::arg("records")
  );
  m.def(
    "check_trie_invariant_topologically_sorted",
    &check_trie_invariant_topologically_sorted,
    py::arg("records")
  );
  m.def(
    "check_trie_invariant_chronologically_sorted",
    &check_trie_invariant_chronologically_sorted,
    py::arg("records")
  );
  m.def(
    "check_trie_invariant_single_root",
    &check_trie_invariant_single_root,
    py::arg("records")
  );
  m.def(
    "check_trie_invariant_search_children_valid",
    &check_trie_invariant_search_children_valid,
    py::arg("records")
  );
  m.def(
    "check_trie_invariant_search_children_sorted",
    &check_trie_invariant_search_children_sorted,
    py::arg("records")
  );
  m.def(
    "check_trie_invariant_no_indistinguishable_nodes",
    &check_trie_invariant_no_indistinguishable_nodes,
    py::arg("records")
  );
  m.def(
    "check_trie_invariant_data_nodes_are_leaves",
    &check_trie_invariant_data_nodes_are_leaves,
    py::arg("records")
  );
  m.def(
    "check_trie_invariant_search_lineage_compatible",
    &check_trie_invariant_search_lineage_compatible,
    py::arg("records")
  );
  m.def(
    "check_trie_invariant_ancestor_bounds",
    &check_trie_invariant_ancestor_bounds,
    py::arg("records")
  );
  m.def(
    "check_trie_invariant_root_at_zero",
    &check_trie_invariant_root_at_zero,
    py::arg("records")
  );
  m.def(
    "check_trie_invariant_ranks_nonnegative",
    &check_trie_invariant_ranks_nonnegative,
    py::arg("records")
  );
}


/*
<%
cfg['extra_compile_args'] = ['-std=c++20', '-Wall', '-Wextra', '-DDEBUG', '-D_GLIBCXX_DEBUG', '-D_GLIBCXX_ASSERTIONS']
setup_pybind11(cfg)
%>
*/
