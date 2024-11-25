// cppimport

#include "pybind11/attr.h"
#include "pybind11/detail/common.h"
#include "pybind11/pytypes.h"
#include <algorithm>
#include <cassert>
#include <optional>
#include <ranges>
#include <span>
#include <unordered_map>
#include <vector>

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

namespace py = pybind11;

typedef uint64_t u64;

// TODO:
//
// consider using std::span for iter

struct Records {
        std::vector<u64> data_id;
        std::vector<u64> id;
        std::vector<u64> search_first_child_id;
        std::vector<u64> search_next_sibling_id;
        std::vector<u64> search_ancestor_id;
        std::vector<u64> ancestor_id;
        std::vector<u64> differentia;
        std::vector<u64> rank;

        void addRecord(
                u64 data_id = 0,
                u64 id = 0,
                u64 ancestor_id = 0,
                u64 search_ancestor_id = 0,
                u64 search_first_child_id = 0,
                u64 search_next_sibling_id = 0,
                u64 rank = 0,
                u64 differentia = 0
        ) {
                this->data_id.push_back(data_id);
                this->id.push_back(id);
                this->search_first_child_id.push_back(search_first_child_id);
                this->search_next_sibling_id.push_back(search_next_sibling_id);
                this->search_ancestor_id.push_back(search_ancestor_id);
                this->ancestor_id.push_back(ancestor_id);
                this->differentia.push_back(differentia);
                this->rank.push_back(rank);
        }

        u64 size() const {
                return this->data_id.size();
        }

        void reset(u64 init_size) {
                this->data_id = std::vector<u64>{};
                this->id = std::vector<u64>{};
                this->search_first_child_id = std::vector<u64>{};
                this->search_next_sibling_id = std::vector<u64>{};
                this->search_ancestor_id = std::vector<u64>{};
                this->ancestor_id = std::vector<u64>{};
                this->differentia = std::vector<u64>{};
                this->rank = std::vector<u64>{};

                this->data_id.reserve(init_size);
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



class ChildrenGenerator {
private:
        const Records &records;
        u64 prev;
        const u64 node;
public:
        ChildrenGenerator(const Records &records, u64 node) :
                records(records), prev(0), node(node) {}
        u64 next() {  // potentially use a std::span arg instead of referencing the vector
                u64 cur;
                if (!this->prev) {
                        this->prev = node;
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

// Sentinel type to mark the end of iteration
struct ChildrenSentinel {};

// ChildrenIterator using the sentinel pattern
template<typename RecordsBegin>
struct ChildrenIterator {

    // Iterator traits
    using iterator_category = std::input_iterator_tag;
    using value_type = u64;
    using difference_type = std::ptrdiff_t;
    using pointer = const u64*;
    using reference = const u64&;

    // Iterator to the vector's begin (or any offset for random access)
    RecordsBegin records_begin;
    u64 current_id;

    // Constructor
    ChildrenIterator(const RecordsBegin records_begin, const u64 current_id)
        : records_begin(records_begin), current_id(current_id) {}

    // Dereference operator
    u64 operator*() const { return current_id; }

    // Pre-increment operator
    ChildrenIterator& operator++() {
        assert(current_id);

        u64 next_sibling_id = *std::next(records_begin, current_id);

        assert(next_sibling_id);
        current_id = next_sibling_id == current_id ? 0 : next_sibling_id;
        return *this;
    }

    // Post-increment operator
    ChildrenIterator operator++(int) {
        ChildrenIterator tmp = *this;
        ++(*this);
        return tmp;
    }

    // Equality comparison between iterators
    bool operator==(const ChildrenIterator& other) const {
        return current_id == other.current_id;
    }
    bool operator!=(const ChildrenIterator& other) const {
        return current_id != other.current_id;
    }

};

template<typename RecordsBegin>
bool operator==(
        const ChildrenSentinel&,
        const ChildrenIterator<RecordsBegin>& iter
) {
    return iter.current_id == 0;
}

template<typename RecordsBegin>
class ChildrenRange
        : public std::ranges::view_interface<ChildrenRange<RecordsBegin>> {

    RecordsBegin records_begin;
    u64 node_id;

public:
    ChildrenRange(const RecordsBegin records_begin, const u64 node_id)
        : records_begin(records_begin), node_id(node_id) {}

    ChildrenIterator<RecordsBegin> begin() {
        return ChildrenIterator{records_begin, node_id};
    }

    ChildrenSentinel end() { return ChildrenSentinel{}; }
};

using RecordsBegin = decltype(std::vector<u64>().begin());

static_assert(std::input_iterator<ChildrenIterator<RecordsBegin>>);
static_assert(std::sentinel_for<ChildrenSentinel, ChildrenIterator<RecordsBegin>>);


void detach_search_parent(Records &records, u64 node) {
        u64 parent = records.search_ancestor_id[node];
        u64 next_sibling = records.search_next_sibling_id[node];
        bool is_last_child = next_sibling == node;

        if (records.search_first_child_id[parent] == node) {
                records.search_first_child_id[parent] = is_last_child ? parent : next_sibling;
        } else {

                // removes from the linked list of children
                ChildrenGenerator gen1(records, parent), gen2(records, parent);
                u64 child1, child2 = gen2.next();
                while ((child1 = gen1.next()) && (child2 = gen2.next())) {
                        if (child2 == node) {
                                records.search_next_sibling_id[child1] = is_last_child ? child1 : next_sibling;
                                break;
                        }
                }
        }

        records.search_ancestor_id[node] = records.search_next_sibling_id[node] = node;
}


void attach_search_parent(Records &records, u64 node, u64 parent) {
        if (records.search_ancestor_id[node] == parent) {
                return;
        }

        records.search_ancestor_id[node] = parent;

        u64 ancestor_first_child = records.search_first_child_id[parent];
        bool is_first_child = ancestor_first_child == parent;
        records.search_next_sibling_id[node] = is_first_child ? node : ancestor_first_child;
        records.search_first_child_id[parent] = node;
}

// setup
constexpr int ix_rank = 0;
constexpr int ix_diff = 1;
constexpr int ix_child = 2;
constexpr int ix_gchild = 3;
using item_t = std::tuple<u64, u64, u64, u64>;

void collapse_indistinguishable_nodes(Records &records, const u64 node) {

        // extract all grandchildren
        static std::vector<item_t> grandchildren;
        grandchildren.resize(0);
        std::ranges::for_each(
                ChildrenRange{records.search_next_sibling_id.cbegin(), node},
                [&records](const u64 child) {
                        std::ranges::transform(
                                ChildrenRange{records.search_next_sibling_id.cbegin(), child},
                                std::back_inserter(grandchildren),
                                [&records, child](const u64 gchild) {
                                        return item_t{
                                                records.rank[gchild],
                                                records.differentia[gchild],
                                                child,
                                                gchild
                                        };
                                }
                        );
                }
        );
        std::sort(std::begin(grandchildren), std::end(grandchildren));

        // group by rank and differentia
        auto groups = std::views::chunk_by(
                grandchildren,
                [](const item_t &a, const item_t &b) {
                        return (
                                std::get<ix_rank>(a) == std::get<ix_rank>(b)
                                && std::get<ix_diff>(a) == std::get<ix_diff>(b)
                        );
                }
        );
        for (const auto &group : groups) {

                // find the winner and losers
                // reassign losers' children to winner
                const u64 winner = std::get<ix_child>(group.front());


                auto losers_view = std::views::drop_while(
                        [&winner](const item_t &item) {
                                return std::get<ix_child>(item) == winner;
                        }
                );
                auto losers = group | losers_view;

                u64 prev = 0;
                for (const auto &gloser : losers) {
                        const u64 loser = std::get<ix_child>(gloser);
                        const u64 loser_child = std::get<ix_gchild>(gloser);
                        detach_search_parent(records, loser_child);
                        attach_search_parent(records, loser_child, winner);
                        if (loser != prev) {
                                detach_search_parent(records, loser);
                                prev = loser;
                        }
                }

        }

}


void consolidate_trie(Records &records, const u64 &rank, const u64 node) {
        ChildrenGenerator gen(records, node);
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
                ChildrenGenerator grandchild_gen(records, popped_node);
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

u64 create_offstring(
        Records &records,
        const u64 parent,
        const u64 rank,
        const u64 differentia,
        const u64 data_id
) {
        u64 node = records.size();
        records.addRecord(
                data_id,
                node,
                parent,
                node,
                node,
                node,
                rank,
                differentia
        );
        attach_search_parent(records, node, parent);
        return node;
}

u64 place_allele(
        Records &records,
        u64 cur_node,
        const u64 rank,
        const u64 differentia
) {
        u64 child;
        ChildrenGenerator gen(records, cur_node);
        while ((child = gen.next())) {
                if (rank == records.rank[child] && differentia == records.differentia[child]) {
                        return child;
                }
        }
        return create_offstring(
                records, cur_node, rank, differentia, 0  // data_id doesn't matter, inner node
        );
}

template <typename T>
struct py_array_span {
        const py::detail::unchecked_reference<T, 1> &data_accessor;
        const u64 start;
        const u64 end;

        u64 size() const {
                return this->end - this->start;
        }
        u64 operator[](u64 index) const {
                return this->data_accessor[this->start + index];
        }

        py_array_span(const py::detail::unchecked_reference<T, 1> &data, const u64 start, const u64 end)
          : data_accessor(data), start(start), end(end) { };
};


void insert_artifact(
        Records &records,
        py_array_span<u64> &&ranks,
        py_array_span<u64> &&differentiae,  // ranks.size() == diff.size()
        const u64 data_id,
        u64 num_strata_deposited
) {
        u64 cur_node = 0;
        for (u64 i = 0; i < ranks.size(); ++i) {
                const u64 &r = ranks[i], &d = differentiae[i];
                consolidate_trie(records, r, cur_node);
                cur_node = place_allele(records, cur_node, r, d);
        }
        create_offstring(records, cur_node, num_strata_deposited - 1, -1, data_id);
}


Records build_trie_searchtable(
        const py::array_t<u64> &data_ids,
        const py::array_t<u64> &num_strata_depositeds,
        const py::array_t<u64> &ranks,
        const py::array_t<u64> &differentiae,
        std::optional<py::handle> tqdm_progress_bar = std::optional<py::handle>{}
) {
        const py::detail::str_attr_accessor logging_info = py::module::import("logging").attr("info");
        const std::optional<py::detail::str_attr_accessor> progress_bar_updater = tqdm_progress_bar.and_then(
                [] (auto a) {return std::optional<py::detail::str_attr_accessor>(a.attr("update"));}
        );

        Records records;
        records.reset(data_ids.size());
        assert(data_ids.size() == num_strata_depositeds.size()
               && data_ids.size() == ranks.size()
               && data_ids.size() == differentiae.size());
        if (!data_ids.size()) {
                return records;
        }

        const py::detail::unchecked_reference<u64, 1> data_ids_accessor = data_ids.unchecked<1>();
        const py::detail::unchecked_reference<u64, 1> num_strata_depositeds_accessor = num_strata_depositeds.unchecked<1>();
        const py::detail::unchecked_reference<u64, 1> ranks_accessor = ranks.unchecked<1>();
        const py::detail::unchecked_reference<u64, 1> differentiae_accessor = differentiae.unchecked<1>();

        logging_info("begin searchtable cpp");

        u64 start = 0, start_data_id = data_ids_accessor[0];
        for (u64 i = 1; i < ranks.size(); ++i) {
                if (start_data_id != data_ids_accessor[i]) {
                        insert_artifact(
                                records,
                                py_array_span<u64>(ranks_accessor, start, i),
                                py_array_span<u64>(differentiae_accessor, start, i),
                                start_data_id, num_strata_depositeds_accessor[start]
                        );
                        start = i;
                        start_data_id = data_ids_accessor[start];
                        if (progress_bar_updater.has_value()) {
                                progress_bar_updater.value()(1);
                        }
                }
        }
        insert_artifact(
                records,
                py_array_span<u64>(ranks_accessor, start, ranks.size()),
                py_array_span<u64>(differentiae_accessor, start, differentiae.size()),
                start_data_id, num_strata_depositeds_accessor[start]
        );
        if (progress_bar_updater.has_value()) {
                progress_bar_updater.value()(1);
                tqdm_progress_bar.value().attr("close")();
        }

        return records;

        // logging_info("end searchtable cpp");
        // std::unordered_map<std::string, py::memoryview> ret;
        // ret.insert({"dstream_data_id", py::memoryview::from_memory(records.data_id.data(), records.data_id.size() * sizeof(u64))});
        // ret.insert({"id", py::memoryview::from_memory(records.id.data(), records.id.size() * sizeof(u64))});
        // ret.insert({"ancestor_id", py::memoryview::from_memory(records.ancestor_id.data(), records.ancestor_id.size() * sizeof(u64))});
        // ret.insert({"differentia", py::memoryview::from_memory(records.differentia.data(), records.differentia.size() * sizeof(u64))});
        // ret.insert({"rank", py::memoryview::from_memory(records.rank.data(), records.rank.size() * sizeof(u64))});
        // logging_info("exit searchtable cpp");
        // return py::cast(ret);
}


PYBIND11_MODULE(build_tree_searchtable_cpp, m) {
        m.def("build", &build_trie_searchtable,
              py::arg("data_ids"),
              py::arg("num_strata_depositeds"),
              py::arg("ranks"),
              py::arg("differentiae"),
              py::arg("tqdm_progress_bar") = std::optional<py::handle>{});
        py::class_<Records>(m, "Records")
                .def_property_readonly("differentia", [] (const Records &records) {
                        return py::memoryview::from_memory(records.differentia.data(), records.differentia.size() * sizeof(u64));
                }, py::return_value_policy::reference_internal)
                .def_property_readonly("rank", [] (const Records &records) {
                        return py::memoryview::from_memory(records.rank.data(), records.rank.size() * sizeof(u64));
                }, py::return_value_policy::reference_internal)
                .def_property_readonly("ancestor_id", [] (const Records &records) {
                        return py::memoryview::from_memory(records.ancestor_id.data(), records.ancestor_id.size() * sizeof(u64));
                }, py::return_value_policy::reference_internal)
                .def_property_readonly("dstream_data_id", [] (const Records &records) {
                        return py::memoryview::from_memory(records.data_id.data(), records.data_id.size() * sizeof(u64));
                }, py::return_value_policy::reference_internal)
                .def_property_readonly("id", [] (const Records &records) {
                        return py::memoryview::from_memory(records.id.data(), records.id.size() * sizeof(u64));
                }, py::return_value_policy::reference_internal);
}


/*
<%
cfg['extra_compile_args'] = ['-std=c++23', '-O3']
setup_pybind11(cfg)
%>
*/
