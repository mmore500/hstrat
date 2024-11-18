// cppimport

#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <unordered_map>
#include <chrono>
#include <format>
#include <algorithm>
#include <iostream>
#include <span>
#include <vector>

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


struct TupleHash {
        u64 operator()(const std::tuple<u64, u64> &obj) const {
                return std::get<0>(obj) ^ std::get<1>(obj);
        }
};

void collapse_indistinguishable_nodes(std::vector<Record> &records, const u64 node) {
        std::unordered_map<std::tuple<u64, u64>, std::vector<u64>, TupleHash> groups;
        ChildrenIterator iter(records, node);

        u64 child;
        while ((child = iter.next())) {  // consider what we are using as the key here
                std::vector<u64> &items = groups[{records[child].rank, records[child].differentia}];
                items.insert(std::lower_bound(items.begin(), items.end(), child), child);
        }

        for (auto [_, children] : groups) {
                u64 winner = children[0];
                for (u64 i = 1; i < children.size(); ++i) {
                        u64 loser = children[i], loser_child;
                        ChildrenIterator loser_children(records, loser);
                        while ((loser_child = loser_children.next())) {
                                detach_search_parent(records, children[1]);
                                attach_search_parent(records, children[1], winner);
                        }
                        detach_search_parent(records, loser);
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

                thread_local std::vector<u64> grandchildren;
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


void insert_artifact(
        std::vector<Record> &records,
        const std::span<const u64> ranks,
        const std::span<const u64> differentiae,  // ranks.size() == diff.size()
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


std::string timestamp() {
    auto const time = std::chrono::current_zone()
        ->to_local(std::chrono::system_clock::now());
    return std::format("{:%Y-%m-%d %X}", time);
}


py::dict build_trie_searchtable(
        const std::vector<u64> &data_ids,
        const std::vector<u64> &num_strata_depositeds,
        const std::vector<u64> &ranks,
        const std::vector<u64> &differentiae
) {
        if (!data_ids.size()) {
                return py::cast(std::unordered_map<std::string, std::vector<u64>>{});
        }
        assert(data_ids.size() == num_strata_depositeds.size() && data_ids.size() == ranks.size() && data_ids.size() == differentiae.size());
        std::cerr << "ranks.size() " << ranks.size() << std::endl;

        std::cerr << timestamp() << " begin searchtable cpp" << std::endl;

        std::vector<Record> records{Record()};  // root node
        records.reserve(data_ids.size());
        u64 start = 0, start_data_id = data_ids[0];
        std::cerr << '.' << std::flush;
        for (u64 i = 1; i < ranks.size(); ++i) {
                if (start_data_id != data_ids[i]) {
                        insert_artifact(
                                records,
                                std::span<const u64>(ranks.begin() + start, i - start),
                                std::span<const u64>(differentiae.begin() + start, i - start),
                                start_data_id, num_strata_depositeds[start]
                        );
                        start = i;
                        start_data_id = data_ids[start];
                        if ((i & ((1 << 16) - 1)) == 0) {
                                std::cerr << '.' << std::flush;
                        }
                }
        }
        insert_artifact(
                records,
                std::span<const u64>(ranks.begin() + start, ranks.size() - start),
                std::span<const u64>(differentiae.begin() + start, differentiae.size() - start),
                start_data_id, num_strata_depositeds[start]
        );
        std::cerr << std::endl;
        std::cerr << timestamp() << " end searchtable cpp" << std::endl;
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
        std::cerr << "exit searchtable cpp" << std::endl;
        return py::cast(ret);
}


PYBIND11_MODULE(build_tree_searchtable_cpp, m) {
        m.def("build", &build_trie_searchtable, py::arg("data_ids"), py::arg("num_strata_depositeds"), py::arg("ranks"), py::arg("differentiae"));
}


/*
<%
cfg['extra_compile_args'] = ['-std=c++20']
setup_pybind11(cfg)
%>
*/
