// cppimport

#include <iostream>
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

using namespace pybind11::literals;
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


struct TupleHash {
        u64 operator()(const std::tuple<u64, u64> &obj) const {
                return std::get<0>(obj) ^ std::get<1>(obj);
        }
};

void collapse_indistinguishable_nodes(Records &records, const u64 node) {
        std::unordered_map<std::tuple<u64, u64>, std::vector<u64>, TupleHash> groups;
        ChildrenGenerator gen(records, node);
        u64 child;
        while ((child = gen.next())) {  // consider what we are using as the key here
                std::vector<u64> &items = groups[{records.rank[child], records.differentia[child]}];
                items.insert(std::lower_bound(items.begin(), items.end(), child), child);
        }
        for (auto [_, children] : groups) {
                u64 winner = children[0];
                for (u64 i = 1; i < children.size(); ++i) {
                        u64 loser = children[i], loser_child;

                        std::vector<u64> loser_children;
                        ChildrenGenerator loser_children_gen(records, loser);
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

template <typename span_type>
void insert_artifact(
        Records &records,
        span_type &&ranks,
        span_type &&differentiae,
        const u64 data_id,
        u64 num_strata_deposited
) {
        assert(ranks.size() == differentiae.size());
        u64 cur_node = 0;
        for (u64 i = 0; i < ranks.size(); ++i) {
                const u64 &r = ranks[i], &d = differentiae[i];
                consolidate_trie(records, r, cur_node);
                cur_node = place_allele(records, cur_node, r, d);
        }
        create_offstring(records, cur_node, num_strata_deposited - 1, -1, data_id);
}

Records build_trie_searchtable_normal(
        const std::vector<u64> &data_ids,
        const std::vector<u64> &num_strata_depositeds,
        const std::vector<std::vector<u64>> &ranks,
        const std::vector<std::vector<u64>> &differentiae,
        const py::handle &tqdm_progress_ctor = py::none{}
) {
        Records records;
        records.reset(data_ids.size());
        assert(data_ids.size() == num_strata_depositeds.size()
               && data_ids.size() == ranks.size()
               && data_ids.size() == differentiae.size());
        if (!data_ids.size()) {
                return records;
        }


        const py::detail::str_attr_accessor logging_info = py::module::import("logging").attr("info");
        logging_info("begin searchtable cpp");

        const py::object tqdm_progress_bar = tqdm_progress_ctor.is_none() ? py::none{}
                                             : tqdm_progress_ctor("total"_a=data_ids.size());
        const auto progress_bar_updater =
                tqdm_progress_bar.is_none() ? std::optional<py::detail::str_attr_accessor>{}
                : std::optional<py::detail::str_attr_accessor>(tqdm_progress_bar.attr("update"));

        for (u64 i = 0; i < ranks.size(); ++i) {
                insert_artifact<std::span<const u64>>(
                        records,
                        std::span<const u64>(ranks[i]),
                        std::span<const u64>(differentiae[i]),
                        data_ids[i], num_strata_depositeds[i]
                );
                if (progress_bar_updater.has_value()) {
                        progress_bar_updater.value()(1);
                        if (i == ranks.size() - 1) {
                                tqdm_progress_bar.attr("close")();
                        }
                }
        }

        return records;
}

u64 count_unique_elements(const py::detail::unchecked_reference<u64, 1> &arr, const u64 n) {
        u64 ele = arr[0], result = 1;
        for (u64 i = 1; i < n; ++i) {
                if (arr[i] != ele) {
                        ele = arr[i];
                        ++result;
                }
        }
        return result;
}

Records build_trie_searchtable_exploded(
        const py::array_t<u64> &data_ids,
        const py::array_t<u64> &num_strata_depositeds,
        const py::array_t<u64> &ranks,
        const py::array_t<u64> &differentiae,
        const py::handle &tqdm_progress_ctor = py::none{}
) {
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

        const py::detail::str_attr_accessor logging_info = py::module::import("logging").attr("info");
        logging_info("begin searchtable cpp");

        const py::object tqdm_progress_bar = tqdm_progress_ctor.is_none() ? py::none{}
                                             : tqdm_progress_ctor("total"_a=count_unique_elements(data_ids_accessor, data_ids.size()));
        const auto progress_bar_updater =
                tqdm_progress_bar.is_none() ? std::optional<py::detail::str_attr_accessor>{}
                : std::optional<py::detail::str_attr_accessor>(tqdm_progress_bar.attr("update"));

        u64 start = 0, start_data_id = data_ids_accessor[0];
        for (u64 i = 1; i < ranks.size(); ++i) {
                if (start_data_id != data_ids_accessor[i]) {
                        insert_artifact<py_array_span<u64>>(
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
                tqdm_progress_bar.attr("close")();
        }

        return records;
}


PYBIND11_MODULE(_build_tree_searchtable_cpp, m) {
        m.def("build_exploded", &build_trie_searchtable_exploded,
              py::arg("data_ids"),
              py::arg("num_strata_depositeds"),
              py::arg("ranks"),
              py::arg("differentiae"),
              py::arg("tqdm_progress_bar") = py::none{});
        m.def("build_normal", &build_trie_searchtable_normal,
              py::arg("data_ids"),
              py::arg("num_strata_depositeds"),
              py::arg("ranks"),
              py::arg("differentiae"),
              py::arg("tqdm_progress_bar") = py::none{});
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
cfg['extra_compile_args'] = ['-std=c++20', '-O3']
setup_pybind11(cfg)
%>
*/