// cppimport
// C++ unit tests for internal functions in _build_tree_searchtable_cpp_impl.
//
// Each test_* function performs assertions and throws std::runtime_error on
// failure (so failures propagate cleanly through pybind11 into pytest).
// The implementation is brought in via #include with the module-definition
// guard so only one PYBIND11_MODULE is compiled.

#define HSTRAT_SEARCHTABLE_IMPL_INCLUDE_ONLY
#include "_build_tree_searchtable_cpp_impl.cpp"
#undef HSTRAT_SEARCHTABLE_IMPL_INCLUDE_ONLY

#include <sstream>
#include <stdexcept>
#include <string>

// ---------------------------------------------------------------------------
// Assertion helper
// ---------------------------------------------------------------------------

#define CPP_TEST_ASSERT(cond, msg)                                             \
  do {                                                                         \
    if (!(cond)) {                                                             \
      std::ostringstream _oss;                                                 \
      _oss << "C++ test assertion failed [" __FILE__ ":" << __LINE__ << "]: " \
           << (msg);                                                           \
      throw std::runtime_error(_oss.str());                                   \
    }                                                                          \
  } while (false)

// ---------------------------------------------------------------------------
// Helper: build a fresh root-only Records object
// ---------------------------------------------------------------------------
static Records make_root() {
  // Records(1) automatically inserts the root node at index 0
  return Records(/*init_size=*/16);
}

// ---------------------------------------------------------------------------
// Records::addRecord
// ---------------------------------------------------------------------------

void test_records_root_state() {
  // A freshly constructed Records has exactly one node (the root).
  Records r = make_root();
  CPP_TEST_ASSERT(r.size() == 1, "expected 1 record after construction");
  CPP_TEST_ASSERT(r.rank[0] == 0, "root rank should be 0");
  CPP_TEST_ASSERT(r.differentia[0] == 0, "root differentia should be 0");
  CPP_TEST_ASSERT(r.ancestor_id[0] == 0, "root is its own ancestor");
  CPP_TEST_ASSERT(
    r.search_first_child_id[0] == 0,
    "root search_first_child_id should self-ref"
  );
}

void test_records_add_child() {
  // Adding a second record updates size and stores correct fields.
  Records r = make_root();
  // id=1, ancestor=0, search_ancestor=0 (placeholder not used here),
  // search_first_child=1 (self), prev_sibling=1, next_sibling=1,
  // rank=3, differentia=7
  r.addRecord(
    /*data_id=*/42,
    /*id=*/1,
    /*ancestor_id=*/0,
    /*search_ancestor_id=*/0,
    /*search_first_child_id=*/1,
    /*search_prev_sibling_id=*/1,
    /*search_next_sibling_id=*/1,
    /*rank=*/3,
    /*differentia=*/7
  );
  CPP_TEST_ASSERT(r.size() == 2, "expected 2 records");
  CPP_TEST_ASSERT(r.dstream_data_id[1] == 42, "data_id mismatch");
  CPP_TEST_ASSERT(r.id[1] == 1, "id mismatch");
  CPP_TEST_ASSERT(r.ancestor_id[1] == 0, "ancestor_id mismatch");
  CPP_TEST_ASSERT(r.rank[1] == 3, "rank mismatch");
  CPP_TEST_ASSERT(r.differentia[1] == 7, "differentia mismatch");
  CPP_TEST_ASSERT(r.max_differentia == 7, "max_differentia mismatch");
}

void test_records_max_differentia_tracked() {
  // max_differentia tracks the running maximum across all addRecord calls.
  Records r = make_root();
  r.addRecord(0, 1, 0, 0, 1, 1, 1, 1, 5);
  CPP_TEST_ASSERT(r.max_differentia == 5, "expected 5");
  r.addRecord(0, 2, 1, 1, 2, 2, 2, 2, 12);
  CPP_TEST_ASSERT(r.max_differentia == 12, "expected 12");
  r.addRecord(0, 3, 2, 2, 3, 3, 3, 3, 3);
  CPP_TEST_ASSERT(r.max_differentia == 12, "still 12 -- lower value doesn't decrease max");
}

// ---------------------------------------------------------------------------
// attach_search_parent / detach_search_parent
// ---------------------------------------------------------------------------

// Helper: create an offstring manually and attach it, return its id.
static u64 make_and_attach(Records &r, u64 parent, i64 rank, u64 diff) {
  const u64 node = r.size();
  r.addRecord(
    placeholder_value,  // data_id
    node,               // id
    parent,             // ancestor_id
    node,               // search_ancestor_id (self -- attach will fix)
    node,               // search_first_child_id (self)
    node,               // search_prev_sibling_id (self)
    node,               // search_next_sibling_id (self)
    rank,               // rank
    diff                // differentia
  );
  attach_search_parent(r, node, parent);
  return node;
}

void test_attach_single_child() {
  // Attaching one child: parent's first_child should point to child, and the
  // child's prev/next siblings should self-reference (it's the only child).
  Records r = make_root();
  const u64 child = make_and_attach(r, 0, 5, 3);

  CPP_TEST_ASSERT(
    r.search_first_child_id[0] == child,
    "parent first_child should be child"
  );
  CPP_TEST_ASSERT(
    r.search_ancestor_id[child] == 0,
    "child search_ancestor should be root"
  );
  CPP_TEST_ASSERT(
    r.search_prev_sibling_id[child] == child,
    "sole child prev_sibling should self-ref"
  );
  CPP_TEST_ASSERT(
    r.search_next_sibling_id[child] == child,
    "sole child next_sibling should self-ref"
  );
}

void test_attach_two_children_rank_order() {
  // Attach a low-rank child then a high-rank child; list must stay sorted
  // ascending by rank.
  Records r = make_root();
  const u64 lo = make_and_attach(r, 0, 2, 1);
  const u64 hi = make_and_attach(r, 0, 8, 2);

  CPP_TEST_ASSERT(
    r.search_first_child_id[0] == lo,
    "lower-rank child should be first"
  );
  CPP_TEST_ASSERT(
    r.search_next_sibling_id[lo] == hi,
    "lo -> hi in sibling list"
  );
  CPP_TEST_ASSERT(
    r.search_next_sibling_id[hi] == hi,
    "hi is last, should self-ref"
  );
  CPP_TEST_ASSERT(
    r.search_prev_sibling_id[hi] == lo,
    "hi's prev should be lo"
  );
  CPP_TEST_ASSERT(
    r.search_prev_sibling_id[lo] == lo,
    "lo is first, prev should self-ref"
  );
}

void test_attach_insert_middle() {
  // Insert mid-rank child between lo and hi; list order: lo < mid < hi.
  Records r = make_root();
  const u64 lo  = make_and_attach(r, 0, 2, 1);
  const u64 hi  = make_and_attach(r, 0, 8, 2);
  const u64 mid = make_and_attach(r, 0, 5, 3);

  CPP_TEST_ASSERT(r.search_first_child_id[0] == lo, "lo first");
  CPP_TEST_ASSERT(r.search_next_sibling_id[lo] == mid, "lo->mid");
  CPP_TEST_ASSERT(r.search_next_sibling_id[mid] == hi, "mid->hi");
  CPP_TEST_ASSERT(r.search_next_sibling_id[hi] == hi, "hi self-ref");
  CPP_TEST_ASSERT(r.search_prev_sibling_id[mid] == lo, "mid.prev=lo");
  CPP_TEST_ASSERT(r.search_prev_sibling_id[hi] == mid, "hi.prev=mid");
}

void test_detach_sole_child() {
  // Detaching the only child reverts parent to an empty child list
  // (first_child self-references back to parent).
  Records r = make_root();
  const u64 child = make_and_attach(r, 0, 3, 1);
  detach_search_parent(r, child);

  CPP_TEST_ASSERT(
    r.search_first_child_id[0] == 0,
    "parent first_child should revert to self after detach"
  );
  CPP_TEST_ASSERT(
    r.search_ancestor_id[child] == child,
    "detached child search_ancestor should self-ref"
  );
  CPP_TEST_ASSERT(
    r.search_prev_sibling_id[child] == child,
    "detached child prev_sibling should self-ref"
  );
  CPP_TEST_ASSERT(
    r.search_next_sibling_id[child] == child,
    "detached child next_sibling should self-ref"
  );
}

void test_detach_first_of_two() {
  // Detach the first child; second becomes the new first child.
  Records r = make_root();
  const u64 first  = make_and_attach(r, 0, 2, 1);
  const u64 second = make_and_attach(r, 0, 5, 2);
  detach_search_parent(r, first);

  CPP_TEST_ASSERT(
    r.search_first_child_id[0] == second,
    "second should become first child"
  );
  CPP_TEST_ASSERT(
    r.search_prev_sibling_id[second] == second,
    "new sole child prev_sibling should self-ref"
  );
  CPP_TEST_ASSERT(
    r.search_next_sibling_id[second] == second,
    "new sole child next_sibling should self-ref"
  );
}

void test_detach_last_of_three() {
  // Detach the last child from a three-child list.
  Records r = make_root();
  const u64 a = make_and_attach(r, 0, 1, 1);
  const u64 b = make_and_attach(r, 0, 4, 2);
  const u64 c = make_and_attach(r, 0, 7, 3);
  detach_search_parent(r, c);

  CPP_TEST_ASSERT(r.search_first_child_id[0] == a, "a still first");
  CPP_TEST_ASSERT(r.search_next_sibling_id[a] == b, "a->b");
  CPP_TEST_ASSERT(r.search_next_sibling_id[b] == b, "b is now last, self-ref");
  CPP_TEST_ASSERT(r.search_prev_sibling_id[b] == a, "b.prev=a");
}

void test_detach_middle_of_three() {
  // Detach the middle child; links should bypass it.
  Records r = make_root();
  const u64 a = make_and_attach(r, 0, 1, 1);
  const u64 b = make_and_attach(r, 0, 4, 2);
  const u64 c = make_and_attach(r, 0, 7, 3);
  detach_search_parent(r, b);

  CPP_TEST_ASSERT(r.search_first_child_id[0] == a, "a still first");
  CPP_TEST_ASSERT(r.search_next_sibling_id[a] == c, "a->c after b removed");
  CPP_TEST_ASSERT(r.search_prev_sibling_id[c] == a, "c.prev=a");
  CPP_TEST_ASSERT(r.search_next_sibling_id[c] == c, "c self-ref (last)");
}

void test_attach_after_detach() {
  // p1 and p2 are created before child so that their IDs are lower --
  // attach_search_parent asserts parent_id <= node_id (parents are always
  // allocated before their children in this data structure).
  Records r = make_root();
  const u64 p1    = make_and_attach(r, 0, 2, 10);  // id=1
  const u64 p2    = make_and_attach(r, 0, 2, 20);  // id=2
  const u64 child = make_and_attach(r, p1, 5, 7);  // id=3

  CPP_TEST_ASSERT(
    r.search_ancestor_id[child] == p1, "initially attached to p1"
  );

  detach_search_parent(r, child);
  attach_search_parent(r, child, p2);

  CPP_TEST_ASSERT(
    r.search_ancestor_id[child] == p2,
    "child should now have p2 as search_ancestor"
  );
  CPP_TEST_ASSERT(
    r.search_first_child_id[p2] == child,
    "p2 first_child should be child"
  );
  CPP_TEST_ASSERT(
    r.search_first_child_id[p1] == p1,
    "p1 child list should be empty after detach"
  );
}

// ---------------------------------------------------------------------------
// consolidate_trie
// ---------------------------------------------------------------------------

void test_consolidate_no_children() {
  // A node with no children is a no-op -- no assertion should fire.
  Records r = make_root();
  consolidate_trie(r, /*rank=*/5, /*node=*/0);
  CPP_TEST_ASSERT(r.size() == 1, "no nodes added");
}

void test_consolidate_children_already_at_rank() {
  // When all children are exactly at the target rank, consolidate is a no-op:
  // both children remain reachable and no new nodes are created.
  // Note: attach_search_parent inserts same-rank nodes before existing
  // same-rank siblings, so the second-inserted child ends up as first.
  Records r = make_root();
  const u64 n1 = make_and_attach(r, 0, 5, 1);
  const u64 n2 = make_and_attach(r, 0, 5, 2);
  const u64 sz_before = r.size();
  consolidate_trie(r, /*rank=*/5, /*node=*/0);
  CPP_TEST_ASSERT(r.size() == sz_before, "no nodes added or removed");
  // Both children must still be reachable from root.
  bool found1 = false, found2 = false;
  for (auto c : ChildrenView(r, 0)) {
    if (c == n1) found1 = true;
    if (c == n2) found2 = true;
  }
  CPP_TEST_ASSERT(found1, "n1 still a child of root");
  CPP_TEST_ASSERT(found2, "n2 still a child of root");
}

void test_consolidate_promotes_grandchild_to_rank() {
  // Root -> child(rank=2) -> grandchild(rank=5).
  // consolidate_trie at rank=5 should detach the child and attach the
  // grandchild directly to root.
  Records r = make_root();
  const u64 child      = make_and_attach(r, 0, 2, 7);
  const u64 grandchild = make_and_attach(r, child, 5, 3);

  consolidate_trie(r, /*rank=*/5, /*node=*/0);

  CPP_TEST_ASSERT(
    r.search_first_child_id[0] == grandchild,
    "grandchild should now be direct child of root"
  );
  CPP_TEST_ASSERT(
    r.search_ancestor_id[grandchild] == 0,
    "grandchild search_ancestor should be root"
  );
  // The old intermediate child is detached (search_ancestor self-refs).
  CPP_TEST_ASSERT(
    r.search_ancestor_id[child] == child,
    "intermediate child should be detached"
  );
}

void test_consolidate_two_levels_deep() {
  // Root -> a(rank=1) -> b(rank=3) -> c(rank=7).
  // consolidate_trie at rank=7 should pull c all the way up to root.
  Records r = make_root();
  const u64 a = make_and_attach(r, 0, 1, 1);
  const u64 b = make_and_attach(r, a, 3, 2);
  const u64 c = make_and_attach(r, b, 7, 4);

  consolidate_trie(r, /*rank=*/7, /*node=*/0);

  CPP_TEST_ASSERT(
    r.search_first_child_id[0] == c,
    "c should be promoted to root's direct child"
  );
  CPP_TEST_ASSERT(r.search_ancestor_id[a] == a, "a detached");
  CPP_TEST_ASSERT(r.search_ancestor_id[b] == b, "b detached");
  CPP_TEST_ASSERT(r.search_ancestor_id[c] == 0, "c attached to root");
}

void test_consolidate_multiple_grandchildren() {
  // Root -> child(rank=2) -> gc_a(rank=5, diff=1)
  //                       -> gc_b(rank=5, diff=2)
  // Both grandchildren should be promoted and the child detached.
  Records r = make_root();
  const u64 child = make_and_attach(r, 0, 2, 7);
  const u64 gc_a  = make_and_attach(r, child, 5, 1);
  const u64 gc_b  = make_and_attach(r, child, 5, 2);

  consolidate_trie(r, /*rank=*/5, /*node=*/0);

  CPP_TEST_ASSERT(r.search_ancestor_id[child] == child, "child detached");
  CPP_TEST_ASSERT(r.search_ancestor_id[gc_a] == 0, "gc_a -> root");
  CPP_TEST_ASSERT(r.search_ancestor_id[gc_b] == 0, "gc_b -> root");

  // Both grandchildren should appear in root's children view.
  bool found_a = false, found_b = false;
  for (auto c : ChildrenView(r, 0)) {
    if (c == gc_a) found_a = true;
    if (c == gc_b) found_b = true;
  }
  CPP_TEST_ASSERT(found_a, "gc_a in root children");
  CPP_TEST_ASSERT(found_b, "gc_b in root children");
}

void test_consolidate_merges_indistinguishable_grandchildren() {
  // Root -> child(rank=2) -> gc_a(rank=5, diff=3)
  //                       -> gc_b(rank=5, diff=3)   <- same rank+diff as gc_a
  // After consolidation + collapse, only one (rank=5, diff=3) child of root.
  Records r = make_root();
  const u64 child = make_and_attach(r, 0, 2, 7);
  const u64 gc_a  = make_and_attach(r, child, 5, 3);
  const u64 gc_b  = make_and_attach(r, child, 5, 3);

  consolidate_trie(r, /*rank=*/5, /*node=*/0);

  // Count root's children -- after collapse there should be exactly one.
  u64 count = 0;
  for (auto c : ChildrenView(r, 0)) { ++count; }
  CPP_TEST_ASSERT(count == 1, "duplicate grandchildren should be collapsed to 1");
}

// ---------------------------------------------------------------------------
// collapse_indistinguishable_nodes
// ---------------------------------------------------------------------------

void test_collapse_no_duplicates_unchanged() {
  // Three children with distinct (rank, diff) -- nothing should change.
  Records r = make_root();
  make_and_attach(r, 0, 3, 1);
  make_and_attach(r, 0, 3, 2);
  make_and_attach(r, 0, 3, 3);

  collapse_indistinguishable_nodes(r, 0);

  u64 count = 0;
  for (auto c : ChildrenView(r, 0)) { ++count; }
  CPP_TEST_ASSERT(count == 3, "three distinct children should remain");
}

void test_collapse_two_identical_children() {
  // Two children with the same (rank=3, diff=5): one must be collapsed.
  Records r = make_root();
  make_and_attach(r, 0, 3, 5);
  make_and_attach(r, 0, 3, 5);

  collapse_indistinguishable_nodes(r, 0);

  u64 count = 0;
  for (auto c : ChildrenView(r, 0)) { ++count; }
  CPP_TEST_ASSERT(count == 1, "two identical children collapse to one");
}

void test_collapse_loser_children_reparented() {
  // winner(rank=3,diff=5) and loser(rank=3,diff=5) both have their own child.
  // After collapse, both children end up under the winner.
  Records r = make_root();
  const u64 winner = make_and_attach(r, 0, 3, 5);
  const u64 loser  = make_and_attach(r, 0, 3, 5);
  const u64 wc     = make_and_attach(r, winner, 7, 1);
  const u64 lc     = make_and_attach(r, loser,  7, 2);

  collapse_indistinguishable_nodes(r, 0);

  // Root should have one child (winner).
  u64 root_children = 0;
  u64 surviving_parent = placeholder_value;
  for (auto c : ChildrenView(r, 0)) { ++root_children; surviving_parent = c; }
  CPP_TEST_ASSERT(root_children == 1, "one child of root after collapse");

  // That surviving child should have two children (wc and lc).
  u64 winner_children = 0;
  bool has_wc = false, has_lc = false;
  for (auto c : ChildrenView(r, surviving_parent)) {
    ++winner_children;
    if (c == wc) has_wc = true;
    if (c == lc) has_lc = true;
  }
  CPP_TEST_ASSERT(winner_children == 2, "winner should have 2 children");
  CPP_TEST_ASSERT(has_wc, "winner's original child retained");
  CPP_TEST_ASSERT(has_lc, "loser's child reparented to winner");
}

// ---------------------------------------------------------------------------
// place_allele
// ---------------------------------------------------------------------------

void test_place_allele_creates_new_node() {
  // Placing an allele with no matching child creates a new node.
  Records r = make_root();
  const u64 new_node = place_allele(r, /*cur_node=*/0, /*rank=*/4, /*diff=*/7);
  CPP_TEST_ASSERT(new_node == 1, "new node should get id=1");
  CPP_TEST_ASSERT(r.rank[new_node] == 4, "rank stored correctly");
  CPP_TEST_ASSERT(r.differentia[new_node] == 7, "differentia stored correctly");
  CPP_TEST_ASSERT(
    r.search_ancestor_id[new_node] == 0,
    "new node should be attached to root"
  );
}

void test_place_allele_finds_existing_match() {
  // Placing the same (rank, diff) twice should return the same node both times.
  Records r = make_root();
  const u64 first  = place_allele(r, 0, 4, 7);
  const u64 second = place_allele(r, 0, 4, 7);
  CPP_TEST_ASSERT(first == second, "should return same node for matching allele");
  CPP_TEST_ASSERT(r.size() == 2, "only one extra node created total");
}

void test_place_allele_different_diff_creates_new() {
  // Same rank but different differentia -> separate nodes.
  Records r = make_root();
  const u64 n1 = place_allele(r, 0, 4, 7);
  const u64 n2 = place_allele(r, 0, 4, 8);
  CPP_TEST_ASSERT(n1 != n2, "different diff -> different nodes");
  CPP_TEST_ASSERT(r.size() == 3, "root + two allele nodes");
}

void test_place_allele_different_rank_creates_new() {
  // Same differentia but different rank -> separate nodes.
  Records r = make_root();
  const u64 n1 = place_allele(r, 0, 3, 5);
  const u64 n2 = place_allele(r, 0, 9, 5);
  CPP_TEST_ASSERT(n1 != n2, "different rank -> different nodes");
  CPP_TEST_ASSERT(r.size() == 3, "root + two allele nodes");
}

// ---------------------------------------------------------------------------
// create_offstring
// ---------------------------------------------------------------------------

void test_create_offstring_stores_data_id() {
  Records r = make_root();
  const u64 node = create_offstring(r, /*parent=*/0, /*rank=*/10, /*diff=*/99, /*data_id=*/42);
  CPP_TEST_ASSERT(r.dstream_data_id[node] == 42, "data_id stored");
  CPP_TEST_ASSERT(r.rank[node] == 10, "rank stored");
  CPP_TEST_ASSERT(r.differentia[node] == 99, "differentia stored");
  CPP_TEST_ASSERT(r.ancestor_id[node] == 0, "ancestor_id is parent");
}

void test_create_offstring_attaches_to_parent() {
  Records r = make_root();
  const u64 node = create_offstring(r, 0, 5, 1, 99);
  CPP_TEST_ASSERT(
    r.search_ancestor_id[node] == 0,
    "node should be attached as search child of root"
  );
  CPP_TEST_ASSERT(
    r.search_first_child_id[0] == node,
    "root's first child should be the new node"
  );
}

void test_create_offstring_sequential_ids() {
  // create_offstring assigns the next available id.
  Records r = make_root();
  const u64 n1 = create_offstring(r, 0, 3, 1, 10);
  const u64 n2 = create_offstring(r, 0, 5, 2, 20);
  CPP_TEST_ASSERT(n1 == 1 && n2 == 2, "ids assigned sequentially");
}

// ---------------------------------------------------------------------------
// insert_artifact
// ---------------------------------------------------------------------------

void test_insert_artifact_single_rank() {
  // An artifact with one retained rank + its leaf.
  // Trie should have: root -> allele(r=3, d=7) -> leaf(r=T-1, d=-1).
  Records r = make_root();
  const std::vector<i64> ranks{3};
  const std::vector<u64> diffs{7};
  insert_artifact(r, std::span<const i64>(ranks), std::span<const u64>(diffs),
                  /*data_id=*/5, /*num_strata_deposited=*/10);

  // root + allele + leaf = 3 nodes
  CPP_TEST_ASSERT(r.size() == 3, "3 nodes expected");
  // The leaf (id=2) should carry the artifact's data_id.
  CPP_TEST_ASSERT(r.dstream_data_id[2] == 5, "leaf carries data_id");
  CPP_TEST_ASSERT(r.rank[2] == 9, "leaf rank = num_strata_deposited - 1");
}

void test_insert_artifact_builds_path() {
  // Two-rank artifact: root -> a(r=0,d=1) -> b(r=4,d=3) -> leaf(r=T-1).
  Records r = make_root();
  const std::vector<i64> ranks{0, 4};
  const std::vector<u64> diffs{1, 3};
  insert_artifact(r, std::span<const i64>(ranks), std::span<const u64>(diffs),
                  /*data_id=*/7, /*num_strata_deposited=*/8);

  CPP_TEST_ASSERT(r.size() == 4, "root + 2 allele nodes + leaf = 4");
  CPP_TEST_ASSERT(r.rank[1] == 0, "allele 1 at rank 0");
  CPP_TEST_ASSERT(r.differentia[1] == 1, "allele 1 diff=1");
  CPP_TEST_ASSERT(r.rank[2] == 4, "allele 2 at rank 4");
  CPP_TEST_ASSERT(r.differentia[2] == 3, "allele 2 diff=3");
  // Leaf is the child of allele 2.
  CPP_TEST_ASSERT(r.ancestor_id[3] == 2, "leaf's ancestor is allele 2");
  CPP_TEST_ASSERT(r.dstream_data_id[3] == 7, "leaf carries data_id");
}

void test_insert_artifact_shared_prefix() {
  // Two artifacts sharing (r=0,d=5): should reuse the same allele node.
  Records r = make_root();
  const std::vector<i64>  r1{0, 3};
  const std::vector<u64>  d1{5, 1};
  insert_artifact(r, std::span<const i64>(r1), std::span<const u64>(d1), 10, 5);
  // After first artifact: root(0) + allele(r=0,d=5)(1) + allele(r=3,d=1)(2) + leaf(3) = 4

  const std::vector<i64>  r2{0, 3};
  const std::vector<u64>  d2{5, 2};  // same root allele, different rank-3 diff
  insert_artifact(r, std::span<const i64>(r2), std::span<const u64>(d2), 11, 5);
  // Shared node (r=0,d=5) should be reused; new nodes: allele(r=3,d=2) + leaf = 2 more

  CPP_TEST_ASSERT(r.size() == 6, "4 + 2 new nodes for second artifact");
  CPP_TEST_ASSERT(
    r.dstream_data_id[1] == placeholder_value,
    "shared allele node has placeholder data_id, not an artifact id"
  );
}

void test_insert_artifact_gap_consolidates() {
  // First artifact: dense ranks 0,1,2,3,4 all diff=1.
  // Second artifact: sparse ranks 0,4 both diff=1 (gap over 1,2,3).
  // consolidate_trie during second artifact should collapse 1-2-3 chain.
  Records r = make_root();
  const std::vector<i64>  r1{0, 1, 2, 3, 4};
  const std::vector<u64>  d1{1, 1, 1, 1, 1};
  insert_artifact(r, std::span<const i64>(r1), std::span<const u64>(d1), 10, 6);
  // root + 5 allele nodes + leaf = 7

  const std::vector<i64>  r2{0, 4};
  const std::vector<u64>  d2{1, 1};
  insert_artifact(r, std::span<const i64>(r2), std::span<const u64>(d2), 11, 8);
  // After inserting r2: consolidate_trie at rank=4 pulls (r=4,d=1) node up
  // to be a direct child of (r=0,d=1), bypassing ranks 1-3.

  // The allele at (rank=0,diff=1) should now have (rank=4,diff=1) as a direct
  // search child (the chain 1->2->3 is collapsed away from the search trie).
  const u64 allele_0 = 1;  // (r=0,d=1) was the first node created
  CPP_TEST_ASSERT(r.rank[allele_0] == 0, "allele_0 check");
  CPP_TEST_ASSERT(r.differentia[allele_0] == 1, "allele_0 diff check");

  bool found_rank4 = false;
  for (auto c : ChildrenView(r, allele_0)) {
    if (r.rank[c] == 4) { found_rank4 = true; break; }
  }
  CPP_TEST_ASSERT(found_rank4, "(r=4,d=1) should be direct child of (r=0,d=1) after consolidation");
}

// ---------------------------------------------------------------------------
// pybind11 module
// ---------------------------------------------------------------------------

PYBIND11_MODULE(_build_tree_searchtable_cpp_impl_test, m) {
  m.doc() = "C++ unit tests for _build_tree_searchtable_cpp_impl internals";

  // Records
  m.def("test_records_root_state",        &test_records_root_state);
  m.def("test_records_add_child",         &test_records_add_child);
  m.def("test_records_max_differentia_tracked", &test_records_max_differentia_tracked);

  // attach / detach
  m.def("test_attach_single_child",        &test_attach_single_child);
  m.def("test_attach_two_children_rank_order", &test_attach_two_children_rank_order);
  m.def("test_attach_insert_middle",       &test_attach_insert_middle);
  m.def("test_detach_sole_child",          &test_detach_sole_child);
  m.def("test_detach_first_of_two",        &test_detach_first_of_two);
  m.def("test_detach_last_of_three",       &test_detach_last_of_three);
  m.def("test_detach_middle_of_three",     &test_detach_middle_of_three);
  m.def("test_attach_after_detach",        &test_attach_after_detach);

  // consolidate_trie
  m.def("test_consolidate_no_children",                &test_consolidate_no_children);
  m.def("test_consolidate_children_already_at_rank",   &test_consolidate_children_already_at_rank);
  m.def("test_consolidate_promotes_grandchild_to_rank",&test_consolidate_promotes_grandchild_to_rank);
  m.def("test_consolidate_two_levels_deep",            &test_consolidate_two_levels_deep);
  m.def("test_consolidate_multiple_grandchildren",     &test_consolidate_multiple_grandchildren);
  m.def("test_consolidate_merges_indistinguishable_grandchildren",
        &test_consolidate_merges_indistinguishable_grandchildren);

  // collapse_indistinguishable_nodes
  m.def("test_collapse_no_duplicates_unchanged",  &test_collapse_no_duplicates_unchanged);
  m.def("test_collapse_two_identical_children",   &test_collapse_two_identical_children);
  m.def("test_collapse_loser_children_reparented",&test_collapse_loser_children_reparented);

  // place_allele
  m.def("test_place_allele_creates_new_node",    &test_place_allele_creates_new_node);
  m.def("test_place_allele_finds_existing_match",&test_place_allele_finds_existing_match);
  m.def("test_place_allele_different_diff_creates_new", &test_place_allele_different_diff_creates_new);
  m.def("test_place_allele_different_rank_creates_new", &test_place_allele_different_rank_creates_new);

  // create_offstring
  m.def("test_create_offstring_stores_data_id",    &test_create_offstring_stores_data_id);
  m.def("test_create_offstring_attaches_to_parent",&test_create_offstring_attaches_to_parent);
  m.def("test_create_offstring_sequential_ids",    &test_create_offstring_sequential_ids);

  // insert_artifact
  m.def("test_insert_artifact_single_rank",     &test_insert_artifact_single_rank);
  m.def("test_insert_artifact_builds_path",     &test_insert_artifact_builds_path);
  m.def("test_insert_artifact_shared_prefix",   &test_insert_artifact_shared_prefix);
  m.def("test_insert_artifact_gap_consolidates",&test_insert_artifact_gap_consolidates);
}


/*
<%
cfg['extra_compile_args'] = ['-std=c++20', '-Wall', '-Wextra', '-DDEBUG']
setup_pybind11(cfg)
%>
*/
