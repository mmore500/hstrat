// cppimport

#include "pybind11/pytypes.h"
#include <algorithm>
#include <cassert>
#include <optional>
#include <ranges>
#include <span>
#include <unordered_map>
#include <vector>

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

using namespace pybind11::literals;
namespace py = pybind11;

typedef uint64_t u64;


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
 *  @see build_trie_searchtable_normal
 *  @see build_trie_searchtable_exploded
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

  void addRecord(u64 data_id = 0, u64 id = 0, u64 ancestor_id = 0,
                 u64 search_ancestor_id = 0, u64 search_first_child_id = 0,
                 u64 search_next_sibling_id = 0, u64 rank = 0,
                 u64 differentia = 0) {
    this->dstream_data_id.push_back(data_id);
    this->id.push_back(id);
    this->search_first_child_id.push_back(search_first_child_id);
    this->search_next_sibling_id.push_back(search_next_sibling_id);
    this->search_ancestor_id.push_back(search_ancestor_id);
    this->ancestor_id.push_back(ancestor_id);
    this->differentia.push_back(differentia);
    this->rank.push_back(rank);
  }

  u64 size() const { return this->dstream_data_id.size(); }

  void reset(u64 init_size) {
    this->dstream_data_id = std::vector<u64>{};
    this->id = std::vector<u64>{};
    this->search_first_child_id = std::vector<u64>{};
    this->search_next_sibling_id = std::vector<u64>{};
    this->search_ancestor_id = std::vector<u64>{};
    this->ancestor_id = std::vector<u64>{};
    this->differentia = std::vector<u64>{};
    this->rank = std::vector<u64>{};

    this->dstream_data_id.reserve(init_size);
    this->id.reserve(init_size);
    this->search_first_child_id.reserve(init_size);
    this->search_next_sibling_id.reserve(init_size);
    this->search_ancestor_id.reserve(init_size);
    this->ancestor_id.reserve(init_size);
    this->differentia.reserve(init_size);
    this->rank.reserve(init_size);

    this->addRecord();
  }
};


/**
 * A makeshift iterator for children, called like this:
 *
 *   ChildrenIterator iter(records, node);
 *   while ((child = iter.next())) {
 *     ...
 *   }
 *
 * Returns a value of 0 when there is no more children.
 */
class ChildrenIterator {
private:
  const Records &records;
  u64 prev;
  const u64 node;

public:
  ChildrenIterator(const Records &records, u64 node)
      : records(records), prev(0), node(node) {}
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
 * Removes `node` from the children of its parent. See the
 * information on Records for how children are stored.
 *
 * @see attach_search_parent
 * @see Records
 */
void detach_search_parent(Records &records, u64 node) {
  u64 parent = records.search_ancestor_id[node];
  u64 next_sibling = records.search_next_sibling_id[node];
  bool is_last_child = next_sibling == node;

  if (records.search_first_child_id[parent] == node) {
    records.search_first_child_id[parent] =
        is_last_child ? parent : next_sibling;
  } else {

    // removes from the linked list of children
    ChildrenIterator gen1(records, parent), gen2(records, parent);
    u64 child1, child2 = gen2.next();
    while ((child1 = gen1.next()) && (child2 = gen2.next())) {
      if (child2 == node) {
        records.search_next_sibling_id[child1] =
            is_last_child ? child1 : next_sibling;
        break;
      }
    }
  }

  records.search_ancestor_id[node] = records.search_next_sibling_id[node] =
      node;
}


/**
 * Attaches `node` to the children of `parent`.
 *
 * @see detach_search_parent
 * @see Records
 */
void attach_search_parent(Records &records, u64 node, u64 parent) {
  if (records.search_ancestor_id[node] == parent) {
    return;
  }

  records.search_ancestor_id[node] = parent;

  u64 ancestor_first_child = records.search_first_child_id[parent];
  bool is_first_child = ancestor_first_child == parent;
  records.search_next_sibling_id[node] =
      is_first_child ? node : ancestor_first_child;
  records.search_first_child_id[parent] = node;
}

struct TupleHash {
  u64 operator()(const std::tuple<u64, u64> &obj) const {
    return std::get<0>(obj) ^ std::get<1>(obj);
  }
};


/**
 * When consolidating a trie (see below), it may be the
 * case that a parent has duplicate children. This function
 * detects duplicates, chooses a winning duplicate, and
 * attaches all of the losers' children to the winner.
 *
 * @see consolidate_trie
 */
void collapse_indistinguishable_nodes(Records &records, const u64 node) {
  std::unordered_map<std::tuple<u64, u64>, std::vector<u64>, TupleHash> groups;
  ChildrenIterator gen(records, node);
  u64 child;
  while ((child = gen.next())) {  // consider what we are using as the key here
    std::vector<u64> &items =
        groups[{records.rank[child], records.differentia[child]}];
    items.insert(std::lower_bound(items.begin(), items.end(), child), child);
  }
  for (auto [_, children] : groups) {
    u64 winner = children[0];
    for (u64 i = 1; i < children.size(); ++i) {
      u64 loser = children[i], loser_child;

      std::vector<u64> loser_children;
      ChildrenIterator loser_children_gen(records, loser);
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
  ChildrenIterator gen(records, node);
  u64 child = gen.next();
  if (child == 0 || records.rank[child] == rank) {
    return;
  }
  std::vector<u64> node_stack = {child};
  while ((child = gen.next())) {
    node_stack.push_back(child);
  }

  // drop children and attach grandchildren
  while (!node_stack.empty()) {
    u64 popped_node = node_stack.back(), grandchild;
    node_stack.pop_back();
    detach_search_parent(records, popped_node);

    static std::vector<u64> grandchildren;
    grandchildren.resize(0);
    ChildrenIterator grandchild_gen(records, popped_node);
    while ((grandchild = grandchild_gen.next())) {
      grandchildren.push_back(grandchild);
    }
    for (const u64 &grandchild : grandchildren) {
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
u64 create_offstring(Records &records, const u64 parent, const u64 rank,
                     const u64 differentia, const u64 data_id) {
  u64 node = records.size();
  records.addRecord(data_id, node, parent, node, node, node, rank, differentia);
  attach_search_parent(records, node, parent);
  return node;
}

/**
 * Inserts one rank-differentia pair into the trie.
 *
 * @see insert_artifact
 */
u64 place_allele(Records &records, u64 cur_node, const u64 rank,
                 const u64 differentia) {
  u64 child;
  ChildrenIterator gen(records, cur_node);
  while ((child = gen.next())) {
    if (rank == records.rank[child] &&
        differentia == records.differentia[child]) {
      return child;
    }
  }
  return create_offstring(records, cur_node, rank, differentia,
                          0 // data_id doesn't matter, inner node
  );
}

/**
 * A makeshift span over a pybind11::array_t using an
 * unchecked_reference. Only supports the indexing and
 * a .size() call.
 */
template <typename T> struct py_array_span {
  const py::detail::unchecked_reference<T, 1> &data_accessor;
  const u64 start;
  const u64 end;

  u64 size() const { return this->end - this->start; }
  u64 operator[](u64 index) const {
    return this->data_accessor[this->start + index];
  }

  py_array_span(const py::detail::unchecked_reference<T, 1> &data,
                const u64 start, const u64 end)
      : data_accessor(data), start(start), end(end) {};
};

/**
 * Adds a single artifact (a.k.a specimen, column) to the
 * searchtable. Accesses the artifact using a span.
 *
 * @see py_array_span
 * @see place_allele
 */
template <typename span_type>
void insert_artifact(Records &records, span_type &&ranks,
                     span_type &&differentiae, const u64 data_id,
                     u64 num_strata_deposited) {
  assert(ranks.size() == differentiae.size());
  u64 cur_node = 0;
  for (u64 i = 0; i < ranks.size(); ++i) {
    const u64 &r = ranks[i], &d = differentiae[i];
    consolidate_trie(records, r, cur_node);
    cur_node = place_allele(records, cur_node, r, d);
  }
  create_offstring(records, cur_node, num_strata_deposited - 1, -1, data_id);
}

template <typename Sequence>
inline pybind11::array_t<typename Sequence::value_type> as_pyarray(Sequence &&seq) {
    auto size                         = seq.size();
    auto data                         = seq.data();
    std::unique_ptr<Sequence> seq_ptr = std::make_unique<Sequence>(std::move(seq));
    auto capsule = pybind11::capsule(seq_ptr.get(), [](void *p) { std::unique_ptr<Sequence>(reinterpret_cast<Sequence *>(p)); });
    seq_ptr.release();
    return pybind11::array({size}, {sizeof(typename Sequence::value_type)}, data, capsule);
}

py::dict records_to_dict(Records &records) {
  std::unordered_map<std::string, py::array_t<u64>> return_mapping;
  return_mapping.insert({"rank", as_pyarray(std::move(records.rank))});
  return_mapping.insert({"differentia", as_pyarray(std::move(records.differentia))});
  return_mapping.insert({"id", as_pyarray(std::move(records.id))});
  return_mapping.insert({"ancestor_id", as_pyarray(std::move(records.ancestor_id))});
  return_mapping.insert({"dstream_data_id", as_pyarray(std::move(records.dstream_data_id))});
  return py::cast(return_mapping);
}

const py::object get_pbar(const py::handle &pbar_ctor, u64 len) {
      return pbar_ctor.is_none() ? py::none{} : pbar_ctor("total"_a = len);
}

const std::optional<py::detail::str_attr_accessor> get_pbar_updater(const py::object &pbar) {
      return pbar.is_none()
          ? std::optional<py::detail::str_attr_accessor>{}
          : std::optional<py::detail::str_attr_accessor>(
                pbar.attr("update"));
}


/**
 * Constructs the trie in the case where each element in each
 * of the below vectors represents a unique artifact. Includes
 * logging and an optional tqdm progress bar.
 *
 * @see build_trie_searchtable_exploded
 */
py::dict build_trie_searchtable_normal(
    const std::vector<u64> &data_ids,
    const std::vector<u64> &num_strata_depositeds,
    const std::vector<std::vector<u64>> &ranks,
    const std::vector<std::vector<u64>> &differentiae,
    const py::handle &tqdm_progress_ctor = py::none{}) {
  Records records;
  records.reset(data_ids.size());
  assert(data_ids.size() == num_strata_depositeds.size() &&
         data_ids.size() == ranks.size() &&
         data_ids.size() == differentiae.size());
  if (!data_ids.size()) {
    return py::dict{};
  }

  const py::detail::str_attr_accessor logging_info =
      py::module::import("logging").attr("info");
  logging_info("begin searchtable cpp");

  const py::object tqdm_progress_bar = get_pbar(tqdm_progress_ctor, data_ids.size());
  const auto progress_bar_updater = get_pbar_updater(tqdm_progress_bar);

  for (u64 i = 0; i < ranks.size(); ++i) {
    insert_artifact<std::span<const u64>>(
        records, std::span<const u64>(ranks[i]),
        std::span<const u64>(differentiae[i]), data_ids[i],
        num_strata_depositeds[i]);
    if (progress_bar_updater.has_value()) {
      progress_bar_updater.value()(1);
      if (i == ranks.size() - 1) {
        tqdm_progress_bar.attr("close")();
      }
    }
  }

  return records_to_dict(records);
}


/**
 * A helper function to count the nunber of unique items in an
 * array. This is similar to std::unique but does not mutate.
 */
u64 count_unique_elements(const py::detail::unchecked_reference<u64, 1> &arr,
                          const u64 n) {
  u64 ele = arr[0], result = 1;
  for (u64 i = 1; i < n; ++i) {
    if (arr[i] != ele) {
      ele = arr[i];
      ++result;
    }
  }
  return result;
}

/**
 * Constructs the trie in the case where each of the below
 * arrays are 1-dimensional representing an exploded DataFrame.
 * This is used in 'hstrat.dataframe.surface_unpack_reconstruct'.
 * Includes logging and an optional tqdm progress bar.
 *
 * @see build_trie_searchtable_normal
 */
py::dict build_trie_searchtable_exploded(
    const py::array_t<u64> &data_ids,
    const py::array_t<u64> &num_strata_depositeds,
    const py::array_t<u64> &ranks, const py::array_t<u64> &differentiae,
    const py::handle &tqdm_progress_ctor = py::none{}) {
  Records records;
  records.reset(data_ids.size());
  assert(data_ids.size() == num_strata_depositeds.size() &&
         data_ids.size() == ranks.size() &&
         data_ids.size() == differentiae.size());
  if (!data_ids.size()) {
    return py::dict{};
  }

  const py::detail::unchecked_reference<u64, 1> data_ids_accessor =
      data_ids.unchecked<1>();
  const py::detail::unchecked_reference<u64, 1> num_strata_depositeds_accessor =
      num_strata_depositeds.unchecked<1>();
  const py::detail::unchecked_reference<u64, 1> ranks_accessor =
      ranks.unchecked<1>();
  const py::detail::unchecked_reference<u64, 1> differentiae_accessor =
      differentiae.unchecked<1>();

  const py::detail::str_attr_accessor logging_info =
      py::module::import("logging").attr("info");
  logging_info("begin searchtable cpp");

  const py::object tqdm_progress_bar = get_pbar(tqdm_progress_ctor, count_unique_elements(data_ids_accessor, data_ids.size()));
  const auto progress_bar_updater = get_pbar_updater(tqdm_progress_bar);

  u64 start = 0, start_data_id = data_ids_accessor[0];
  for (u64 i = 1; i < (u64)ranks.size(); ++i) {
    if (start_data_id != data_ids_accessor[i]) {
      insert_artifact<py_array_span<u64>>(
          records, py_array_span<u64>(ranks_accessor, start, i),
          py_array_span<u64>(differentiae_accessor, start, i), start_data_id,
          num_strata_depositeds_accessor[start]);
      start = i;
      start_data_id = data_ids_accessor[start];
      if (progress_bar_updater.has_value()) {
        progress_bar_updater.value()(1);
      }
    }
  }
  insert_artifact(
      records, py_array_span<u64>(ranks_accessor, start, ranks.size()),
      py_array_span<u64>(differentiae_accessor, start, differentiae.size()),
      start_data_id, num_strata_depositeds_accessor[start]);
  if (progress_bar_updater.has_value()) {
    progress_bar_updater.value()(1);
    tqdm_progress_bar.attr("close")();
  }
  logging_info("done searchtable cpp");
  return records_to_dict(records);
}

PYBIND11_MODULE(_build_tree_searchtable_cpp_impl, m) {
  m.def("build_exploded", &build_trie_searchtable_exploded, py::arg("data_ids"),
        py::arg("num_strata_depositeds"), py::arg("ranks"),
        py::arg("differentiae"), py::arg("tqdm_progress_bar") = py::none{});
  m.def("build_normal", &build_trie_searchtable_normal, py::arg("data_ids"),
        py::arg("num_strata_depositeds"), py::arg("ranks"),
        py::arg("differentiae"), py::arg("tqdm_progress_bar") = py::none{});
}

/*
<%
cfg['extra_compile_args'] = ['-std=c++20', '-Wall', '-Wextra']
setup_pybind11(cfg)
%>
*/
