// cppimport

#include <algorithm>
#include <cassert>
#include <chrono>
#include <format>
#include <iostream>
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

struct Record {
        u64 data_id;
        u64 id;
        u64 search_first_child_id;
        u64 search_next_sibling_id;
        u64 search_ancestor_id;
        u64 ancestor_id;
        u64 differentia;
        u64 rank;

        Record(
                u64 data_id = 0,
                u64 id = 0,
                u64 ancestor_id = 0,
                u64 search_ancestor_id = 0,
                u64 search_first_child_id = 0,
                u64 search_next_sibling_id = 0,
                u64 rank = 0,
                u64 differentia = 0
       ) : data_id(data_id), id(id), search_first_child_id(search_first_child_id),
           search_next_sibling_id(search_next_sibling_id), search_ancestor_id(search_ancestor_id),
           ancestor_id(ancestor_id), differentia(differentia), rank(rank) {};
};


class ChildrenIterator {
private:
        const std::vector<Record> &records;
        u64 prev;
        const u64 node;
public:
        ChildrenIterator(const std::vector<Record> &records, u64 node) :
                records(records), prev(0), node(node) {}
        u64 next() {  // potentially use a std::span arg instead of referencing the vector
                u64 cur;
                if (!this->prev) {
                        this->prev = node;
                        cur = this->records[this->node].search_first_child_id;
                } else {
                        cur = this->records[this->prev].search_next_sibling_id;
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
struct ChildrenIterator2 {

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
    ChildrenIterator2(const RecordsBegin records_begin, const u64 current_id)
        : records_begin(records_begin), current_id(current_id) {}

    // Dereference operator
    u64 operator*() const { return current_id; }

    // Pre-increment operator
    ChildrenIterator2& operator++() {
        assert(current_id);

        const Record& current_record = *std::next(records_begin, current_id);
        u64 next_sibling_id = current_record.search_next_sibling_id;

        assert(next_sibling_id);
        current_id = next_sibling_id == current_id ? 0 : next_sibling_id;
        return *this;
    }

    // Post-increment operator
    ChildrenIterator2 operator++(int) {
        ChildrenIterator2 tmp = *this;
        ++(*this);
        return tmp;
    }

    // Equality comparison between iterators
    bool operator==(const ChildrenIterator2& other) const {
        return current_id == other.current_id;
    }
    bool operator!=(const ChildrenIterator2& other) const {
        return current_id != other.current_id;
    }

};

template<typename RecordsBegin>
bool operator==(
        const ChildrenSentinel&,
        const ChildrenIterator2<RecordsBegin>& iter
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

    ChildrenIterator2<RecordsBegin> begin() {
        return ChildrenIterator2{records_begin, node_id};
    }

    ChildrenSentinel end() { return ChildrenSentinel{}; }
};

using RecordsBegin = decltype(std::vector<Record>().begin());

static_assert(std::input_iterator<ChildrenIterator2<RecordsBegin>>);
static_assert(std::sentinel_for<ChildrenSentinel, ChildrenIterator2<RecordsBegin>>);


void detach_search_parent(std::vector<Record> &records, u64 node) {
        u64 parent = records[node].search_ancestor_id;
        u64 next_sibling = records[node].search_next_sibling_id;
        bool is_last_child = next_sibling == node;

        if (records[parent].search_first_child_id == node) {
                records[parent].search_first_child_id = is_last_child ? parent : next_sibling;
        } else {

                // removes from the linked list of children
                ChildrenIterator iter1(records, parent), iter2(records, parent);
                u64 child1, child2 = iter2.next();
                while ((child1 = iter1.next()) && (child2 = iter2.next())) {
                        if (child2 == node) {
                                records[child1].search_next_sibling_id = is_last_child ? child1 : next_sibling;
                                break;
                        }
                }
        }

        records[node].search_next_sibling_id = records[node].search_ancestor_id = node;
}


void attach_search_parent(std::vector<Record> &records, u64 node, u64 parent) {
        if (records[node].search_ancestor_id == parent) {
                return;
        }

        records[node].search_ancestor_id = parent;

        u64 ancestor_first_child = records[parent].search_first_child_id;
        bool is_first_child = ancestor_first_child == parent;
        records[node].search_next_sibling_id = is_first_child ? node : ancestor_first_child;
        records[parent].search_first_child_id = node;
}

// setup
constexpr int ix_rank = 0;
constexpr int ix_diff = 1;
constexpr int ix_child = 2;
constexpr int ix_gchild = 3;
using item_t = std::tuple<u64, u64, u64, u64>;

void collapse_indistinguishable_nodes(std::vector<Record> &records, const u64 node) {

        // extract all grandchildren
        static std::vector<item_t> grandchildren;
        grandchildren.resize(0);
        std::ranges::for_each(
                ChildrenRange{records.cbegin(), node},
                [&records](const u64 child) {
                        std::ranges::transform(
                                ChildrenRange{records.cbegin(), child},
                                std::back_inserter(grandchildren),
                                [&records, child](const u64 gchild) {
                                        return item_t{
                                                records[gchild].rank,
                                                records[gchild].differentia,
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


void consolidate_trie(std::vector<Record> &records, const u64 &rank, const u64 node) {
        ChildrenIterator iter(records, node);
        u64 child = iter.next();
        if (child == 0 || records[child].rank == rank) {
                return;
        }
        std::vector<u64> node_stack = {child};
        while ((child = iter.next())) {
                node_stack.push_back(child);
        }

        // drop children and attach grandchildren
        while (!node_stack.empty()) {
                u64 popped_node = node_stack.back(), grandchild;
                node_stack.pop_back();
                detach_search_parent(records, popped_node);

                static std::vector<u64> grandchildren;
                grandchildren.resize(0);
                ChildrenIterator grandchild_iter(records, popped_node);
                while ((grandchild = grandchild_iter.next())) {
                        grandchildren.push_back(grandchild);
                }
                for (const u64 &grandchild : grandchildren) {
                        if (records[grandchild].rank >= rank) {
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
        std::vector<Record> &records,
        const u64 parent,
        const u64 rank,
        const u64 differentia,
        const u64 data_id
) {
        u64 node = records.size();
        records.emplace_back(
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
        std::vector<Record> &records,
        u64 cur_node,
        const u64 rank,
        const u64 differentia
) {
        u64 child;
        ChildrenIterator iter(records, cur_node);
        while ((child = iter.next())) {
                if (rank == records[child].rank && differentia == records[child].differentia) {
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
        std::vector<Record> &records,
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


py::dict build_trie_searchtable(
        const py::array_t<u64> &data_ids,
        const py::array_t<u64> &num_strata_depositeds,
        const py::array_t<u64> &ranks,
        const py::array_t<u64> &differentiae
) {
        const static py::detail::str_attr_accessor logging_info = py::module::import("logging").attr("info");

        assert(data_ids.size() == num_strata_depositeds.size()
               && data_ids.size() == ranks.size()
               && data_ids.size() == differentiae.size());
        if (!data_ids.size()) {
                return py::cast(std::unordered_map<std::string, std::vector<u64>>{});
        }

        const py::detail::unchecked_reference<u64, 1> data_ids_accessor = data_ids.unchecked<1>();
        const py::detail::unchecked_reference<u64, 1> num_strata_depositeds_accessor = num_strata_depositeds.unchecked<1>();
        const py::detail::unchecked_reference<u64, 1> ranks_accessor = ranks.unchecked<1>();
        const py::detail::unchecked_reference<u64, 1> differentiae_accessor = differentiae.unchecked<1>();

        logging_info("begin searchtable cpp");

        std::vector<Record> records{Record()};  // root node
        records.reserve(data_ids.size());

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
                }
        }
        insert_artifact(
                records,
                py_array_span<u64>(ranks_accessor, start, ranks.size()),
                py_array_span<u64>(differentiae_accessor, start, differentiae.size()),
                start_data_id, num_strata_depositeds_accessor[start]
        );

        logging_info("end searchtable cpp");
        std::unordered_map<std::string, std::vector<u64>> ret;
        for (const Record &rec : records) {
                ret["dstream_data_id"].push_back(rec.data_id);
                ret["id"].push_back(rec.id);
                // ret["search_first_child_id"].push_back(rec.search_first_child_id);
                // ret["search_next_sibling_id"].push_back(rec.search_next_sibling_id);
                // ret["search_ancestor_id"].push_back(rec.search_ancestor_id);
                ret["ancestor_id"].push_back(rec.ancestor_id);
                ret["differentia"].push_back(rec.differentia);
                ret["rank"].push_back(rec.rank);
        }
        logging_info("exit searchtable cpp");
        return py::cast(ret);
}


PYBIND11_MODULE(build_tree_searchtable_cpp, m) {
        m.def("build", &build_trie_searchtable, py::arg("data_ids"), py::arg("num_strata_depositeds"), py::arg("ranks"), py::arg("differentiae"));
}


/*
<%
cfg['extra_compile_args'] = ['-std=c++23', '-O3']
setup_pybind11(cfg)
%>
*/
