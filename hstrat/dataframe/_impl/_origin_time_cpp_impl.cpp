// cppimport
// Tree-free pairwise origin-time estimates over surface tips, for the
// hstrat.dataframe build_trie_crosspair, build_trie_upgma, and
// build_brute_upgma subpackages.
//
// Each tip pair's estimate depends on r, the last rank where the two tips
// agree; m, the first comparable rank where they differ; and m', the next
// comparable rank after m. With c0 the midpoint of [r, m) and c1 the
// midpoint of [m, m'), the estimate (c0 - p * c1) / (1 - p) is unbiased with
// respect to spurious differentia collisions, which occur with probability
// p. Two tips can compare exactly the older tip's retained ranks below the
// younger tip's T, because a dropped rank is never retained again.
//
// Cross-pair sums: for each branching node w of a reconstructed trie, tips
// under w are swept in ascending T through a local trie of their
// differentiae at ranks below w. A new tip b walks its own ranks. At each
// rank, earlier tips on branches with a different differentia first
// mismatch b there, and earlier tips whose data ended at the current node
// agreed with b all the way. Both groups are summed in bulk from per-node
// tallies. Ranks no longer retained are removed lazily, only at nodes a walk
// visits ("consolidation"). The sweep at w counts all pairs under w;
// cross-child sums are w's total minus its children's totals.
//
// Scaffold UPGMA: average-linkage clustering over deduplicated tips, with
// candidate neighbors from a trie walk, a nearest-neighbor chain, exact
// linkage values for small cluster pairs and sampled values otherwise.
// Merges decided on sampled values get exact heights from one weighted
// sweep, and inversions are pooled, keeping the all-pairs total of
// estimates exact.
//
// Brute UPGMA: average-linkage clustering over the dense matrix of all
// pairwise estimates.

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <limits>
#include <numeric>
#include <random>
#include <span>
#include <stdexcept>
#include <tuple>
#include <unordered_map>
#include <vector>

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

typedef int64_t i64;
typedef uint64_t u64;

namespace {

constexpr int NIL = -1;
constexpr i64 PAST_END = std::numeric_limits<i64>::max();

/** Count and sum of T over a group of tips. */
struct Tally {
  i64 n = 0;
  double sum_T = 0.0;

  void add(const double T) {
    n += 1;
    sum_T += T;
  }
  Tally &operator+=(const Tally &o) {
    n += o.n;
    sum_T += o.sum_T;
    return *this;
  }
};

/** Collision-corrected pairwise estimate, summed over a group of earlier
 *  tips, each with T at most the new tip's. Ranks are offset by t0 and
 *  clamped at 0; c0 = midpoint of [r, m), c1 = midpoint of [m, m'), and the
 *  estimate is (c0 - p * c1) / (1 - p). */
struct Estimator {
  double p, t0;

  double off(const double x) const { return std::max(x - t0, 0.0); }

  /** Group agreed through rank r, then its data ended: midpoint of [r, T). */
  double terminal(const Tally &ended, const double r) const {
    return (ended.n * (off(r) - 1) + (ended.sum_T - t0 * ended.n)) / 2;
  }

  /** Group agreed through r, differs at m. Tips still holding m' have
   *  interval [m, m'); tips that ended (T <= m') have [m, T). */
  double mismatch(
    const Tally &all, const Tally &ended, const double r, const double m,
    const i64 m_next
  ) const {
    const double c0 = (off(r) + off(m) - 1) / 2;
    const i64 n_hold = all.n - ended.n;
    const double sum_hi = (m_next == PAST_END ? 0.0 : n_hold * off((double)m_next))
      + (ended.sum_T - t0 * ended.n);
    const double sum_c1 = (all.n * (off(m) - 1) + sum_hi) / 2;
    return (all.n * c0 - p * sum_c1) / (1 - p);
  }
};

/** Retained ranks and differentiae of each tip (CSR). */
struct Tips {
  const i64 *T, *off, *ranks;
  const u64 *diffs;

  std::span<const i64> ranks_of(const i64 t) const {
    return {ranks + off[t], ranks + off[t + 1]};
  }
  std::span<const u64> diffs_of(const i64 t) const {
    return {diffs + off[t], diffs + off[t + 1]};
  }
};

struct TrieNode {
  i64 rank;
  u64 d;
  int first_child = NIL;
  int next_sibling = NIL;
  Tally passing;  // tips with data at this node's rank
  Tally ended;  // tips whose data ends here
};

/** Local trie for one branching node, in a pool reused across nodes. */
struct LocalTrie {
  std::vector<TrieNode> pool;
  int used = 0;

  TrieNode &operator[](const int i) { return pool[i]; }

  int alloc(const i64 rank, const u64 d) {
    if (used == (int)pool.size()) pool.emplace_back();
    pool[used] = TrieNode{rank, d, NIL, NIL, {}, {}};
    return used++;
  }

  void reset(const i64 root_rank) {
    used = 0;
    alloc(root_rank, 0);
  }

  void link(const int parent, const int child) {
    pool[child].next_sibling = pool[parent].first_child;
    pool[parent].first_child = child;
  }

  int find_child(const int parent, const i64 rank, const u64 d) {
    for (int c = pool[parent].first_child; c != NIL; c = pool[c].next_sibling) {
      if (pool[c].rank == rank && pool[c].d == d) return c;
    }
    return NIL;
  }

  /** Attach subtree g under parent, merging with an equal sibling. */
  void attach(const int parent, const int g) {
    const int e = find_child(parent, pool[g].rank, pool[g].d);
    if (e == NIL) {
      link(parent, g);
      return;
    }
    pool[e].passing += pool[g].passing;
    pool[e].ended += pool[g].ended;
    for_each_child(g, [&](const int gg) { attach(e, gg); });
  }

  template <typename F>
  void for_each_child(const int parent, F &&f) {
    for (int c = pool[parent].first_child; c != NIL;) {
      const int next = pool[c].next_sibling;  // f may relink c
      f(c);
      c = next;
    }
  }

  /** Remove children at ranks below r, whose ranks are no longer retained:
   *  tips that ended there now end at parent, and their children are lifted. */
  void consolidate(const int parent, const i64 r) {
    while (true) {
      int prev = NIL, c = pool[parent].first_child;
      while (c != NIL && pool[c].rank >= r) {
        prev = c;
        c = pool[c].next_sibling;
      }
      if (c == NIL) return;
      (prev == NIL ? pool[parent].first_child : pool[prev].next_sibling) = pool[c].next_sibling;
      pool[parent].ended += pool[c].ended;
      for_each_child(c, [&](const int g) { attach(parent, g); });
    }
  }
};

/** Children lists and, for each node, its range in a depth-first tip order. */
struct Tree {
  std::vector<i64> kid_off, kid_ids, tip_order, lo, hi;

  Tree(const i64 n, const i64 *anc, const i64 *tip_of_node) : kid_off(n + 1, 0), lo(n), hi(n) {
    for (i64 i = 0; i < n; ++i) {
      if (anc[i] != i) ++kid_off[anc[i] + 1];
    }
    for (i64 i = 0; i < n; ++i) kid_off[i + 1] += kid_off[i];
    kid_ids.resize(kid_off[n]);
    std::vector<i64> fill(kid_off.begin(), kid_off.end() - 1);
    for (i64 i = 0; i < n; ++i) {
      if (anc[i] != i) kid_ids[fill[anc[i]]++] = i;
    }
    std::vector<std::pair<i64, bool>> stack;  // (node, finished)
    for (i64 root = 0; root < n; ++root) {
      if (anc[root] != root) continue;
      stack.emplace_back(root, false);
      while (!stack.empty()) {
        const auto [v, finished] = stack.back();
        stack.pop_back();
        if (finished) {
          hi[v] = tip_order.size();
          continue;
        }
        lo[v] = tip_order.size();
        if (tip_of_node[v] >= 0) tip_order.push_back(tip_of_node[v]);
        stack.emplace_back(v, true);
        for (const i64 k : kids(v)) stack.emplace_back(k, false);
      }
    }
  }

  std::span<const i64> kids(const i64 v) const {
    return {kid_ids.data() + kid_off[v], kid_ids.data() + kid_off[v + 1]};
  }
  std::span<const i64> tips_under(const i64 v) const {
    return {tip_order.data() + lo[v], tip_order.data() + hi[v]};
  }
};

/** Sum of estimates over all tip pairs under branching node w. */
void sweep(
  const Tips &tips, const Estimator &est, const std::span<const i64> under_w,
  const i64 rank_w, LocalTrie &trie, std::vector<std::pair<i64, i64>> &order,
  double &sum, i64 &count
) {
  order.clear();
  for (const i64 t : under_w) order.emplace_back(tips.T[t], t);
  std::sort(order.begin(), order.end());
  trie.reset(rank_w);
  sum = 0.0;
  count = 0;

  for (const auto &[T_int, b] : order) {
    const double T = (double)T_int;
    const auto ranks = tips.ranks_of(b);
    const auto diffs = tips.diffs_of(b);
    // b's ranks at or above w are shared with every tip under w
    size_t i = std::upper_bound(ranks.begin(), ranks.end(), rank_w) - ranks.begin();
    double r_prev = i ? (double)ranks[i - 1] : std::numeric_limits<double>::lowest();
    int node = 0;

    while (true) {
      // b's next rank; past its last rank, everything below is dropped
      const i64 r = i < ranks.size() ? ranks[i] : PAST_END;
      trie.consolidate(node, r);

      // earlier tips whose data ended here agreed with b throughout
      sum += est.terminal(trie[node].ended, r_prev);
      count += trie[node].ended.n;
      trie[node].passing.add(T);
      if (r == PAST_END) {
        trie[node].ended.add(T);
        break;
      }

      // earlier tips on other branches first differ from b at rank r
      const u64 d = diffs[i];
      const i64 m_next = i + 1 < ranks.size() ? ranks[i + 1] : PAST_END;
      int match = NIL;
      trie.for_each_child(node, [&](const int c) {
        if (trie[c].d == d) {
          match = c;
          return;
        }
        // one level down, tips that ended are exactly those with T <= m'
        if (m_next != PAST_END) trie.consolidate(c, m_next);
        const Tally &ended = m_next == PAST_END ? trie[c].passing : trie[c].ended;
        sum += est.mismatch(trie[c].passing, ended, r_prev, (double)r, m_next);
        count += trie[c].passing.n;
      });

      if (match == NIL) {
        match = trie.alloc(r, d);
        trie.link(node, match);
      }
      node = match;
      r_prev = (double)r;
      ++i;
    }
  }
}


// ===========================================================================
// Scaffold UPGMA over deduplicated tips. Tips with identical T and
// differentiae are one object with a count; every sum is count-weighted.
// ===========================================================================

/** Collision-corrected estimate for one tip pair (tree-free). */
double pair_estimate(const Tips &tips, const Estimator &est, i64 a, i64 b) {
  if (tips.T[a] > tips.T[b]) std::swap(a, b);  // a younger, b older
  const i64 Ta = tips.T[a], Tb = tips.T[b];
  const auto ra = tips.ranks_of(a), rb = tips.ranks_of(b);
  const auto da = tips.diffs_of(a), db = tips.diffs_of(b);
  double r_prev = -1.0;
  size_t ia = 0;
  for (size_t ib = 0; ib < rb.size() && rb[ib] < Ta; ++ib) {
    const i64 r = rb[ib];
    while (ra[ia] < r) ++ia;
    if (da[ia] != db[ib]) {
      i64 m_next = PAST_END;
      if (ib + 1 < rb.size() && rb[ib + 1] < Ta) m_next = rb[ib + 1];
      const double m2 = m_next == PAST_END ? (double)std::min(Ta, Tb) : (double)m_next;
      const double c0 = (est.off(r_prev) + est.off((double)r) - 1) / 2;
      const double c1 = (est.off((double)r) + est.off(m2) - 1) / 2;
      return (c0 - est.p * c1) / (1 - est.p);
    }
    r_prev = (double)r;
  }
  return (est.off(r_prev) + est.off((double)std::min(Ta, Tb)) - 1) / 2;
}

/** Objects: groups of identical tips. rep = one member tip; count = size. */
struct Objects {
  std::vector<i64> rep, count;
  std::vector<i64> of_tip;  // tip -> object
  std::vector<std::vector<i64>> tips;  // object -> member tips
};

Objects deduplicate(const Tips &tips, const i64 n) {
  std::vector<u64> h(n);
  for (i64 t = 0; t < n; ++t) {
    u64 x = 1469598103934665603ULL ^ (u64)tips.T[t];
    for (const u64 d : tips.diffs_of(t)) x = (x ^ d) * 1099511628211ULL;
    h[t] = x;
  }
  std::vector<i64> order(n);
  std::iota(order.begin(), order.end(), 0);
  std::sort(order.begin(), order.end(), [&](i64 a, i64 b) {
    return h[a] != h[b] ? h[a] < h[b] : a < b;
  });
  auto same = [&](i64 a, i64 b) {
    if (tips.T[a] != tips.T[b]) return false;
    const auto da = tips.diffs_of(a), db = tips.diffs_of(b);
    return std::equal(da.begin(), da.end(), db.begin(), db.end());
  };
  Objects o;
  o.of_tip.assign(n, -1);
  for (i64 i = 0; i < n;) {
    i64 j = i;
    while (j < n && h[order[j]] == h[order[i]]) ++j;
    // within one hash bucket, split exactly (collisions are vanishingly rare)
    for (i64 a = i; a < j; ++a) {
      const i64 t = order[a];
      if (o.of_tip[t] >= 0) continue;
      const i64 obj = o.rep.size();
      o.rep.push_back(t);
      o.tips.push_back({t});
      o.of_tip[t] = obj;
      for (i64 b = a + 1; b < j; ++b) {
        const i64 u = order[b];
        if (o.of_tip[u] < 0 && same(t, u)) {
          o.of_tip[u] = obj;
          o.tips.back().push_back(u);
        }
      }
      o.count.push_back(o.tips.back().size());
    }
    i = j;
  }
  return o;
}

/** Sum of estimates over all tip pairs between distinct objects in objs,
 *  each object weighted by its count (crosspair2s sweep, weighted). */
void weighted_sweep(
  const Tips &tips, const Estimator &est, const Objects &ob, const std::vector<i64> &objs,
  LocalTrie &trie, std::vector<std::pair<i64, i64>> &order, double &sum, double &count
) {
  order.clear();
  for (const i64 o : objs) order.emplace_back(tips.T[ob.rep[o]], o);
  std::sort(order.begin(), order.end());
  trie.reset(-1);
  sum = 0.0;
  count = 0.0;
  for (const auto &[T_int, o] : order) {
    const double T = (double)T_int;
    const double c = (double)ob.count[o];
    const i64 b = ob.rep[o];
    const auto ranks = tips.ranks_of(b);
    const auto diffs = tips.diffs_of(b);
    size_t i = 0;
    double r_prev = std::numeric_limits<double>::lowest();
    int node = 0;
    while (true) {
      const i64 r = i < ranks.size() ? ranks[i] : PAST_END;
      trie.consolidate(node, r);
      sum += c * est.terminal(trie[node].ended, r_prev);
      count += c * trie[node].ended.n;
      trie[node].passing.n += (i64)c;
      trie[node].passing.sum_T += c * T;
      if (r == PAST_END) {
        trie[node].ended.n += (i64)c;
        trie[node].ended.sum_T += c * T;
        break;
      }
      const u64 d = diffs[i];
      const i64 m_next = i + 1 < ranks.size() ? ranks[i + 1] : PAST_END;
      int match = NIL;
      trie.for_each_child(node, [&](const int k) {
        if (trie[k].d == d) {
          match = k;
          return;
        }
        if (m_next != PAST_END) trie.consolidate(k, m_next);
        const Tally &ended = m_next == PAST_END ? trie[k].passing : trie[k].ended;
        sum += c * est.mismatch(trie[k].passing, ended, r_prev, (double)r, m_next);
        count += c * trie[k].passing.n;
      });
      if (match == NIL) {
        match = trie.alloc(r, d);
        trie.link(node, match);
      }
      node = match;
      r_prev = (double)r;
      ++i;
    }
  }
}

/** Trie of object lists for candidate discovery, with lazy consolidation. */
struct ListTrie {
  struct Node {
    i64 rank;
    u64 d;
    int first_child, next_sibling;
    std::vector<int> tips, ends;
  };
  std::vector<Node> pool;

  ListTrie() { pool.push_back(Node{-1, 0, NIL, NIL, {}, {}}); }

  int alloc(const i64 rank, const u64 d) {
    pool.push_back(Node{rank, d, NIL, NIL, {}, {}});
    return (int)pool.size() - 1;
  }
  void link(const int p, const int c) {
    pool[c].next_sibling = pool[p].first_child;
    pool[p].first_child = c;
  }
  int find_child(const int p, const i64 rank, const u64 d) {
    for (int c = pool[p].first_child; c != NIL; c = pool[c].next_sibling) {
      if (pool[c].rank == rank && pool[c].d == d) return c;
    }
    return NIL;
  }
  template <typename F>
  void for_each_child(const int p, F &&f) {
    for (int c = pool[p].first_child; c != NIL;) {
      const int next = pool[c].next_sibling;
      f(c);
      c = next;
    }
  }
  static void append(std::vector<int> &to, std::vector<int> &from) {
    if (to.empty()) {
      to.swap(from);
    } else {
      to.insert(to.end(), from.begin(), from.end());
      std::vector<int>().swap(from);
    }
  }
  void attach(const int p, const int g) {
    const int e = find_child(p, pool[g].rank, pool[g].d);
    if (e == NIL) {
      link(p, g);
      return;
    }
    append(pool[e].tips, pool[g].tips);
    append(pool[e].ends, pool[g].ends);
    for_each_child(g, [&](const int gg) { attach(e, gg); });
  }
  void consolidate(const int p, const i64 r) {
    while (true) {
      int prev = NIL, c = pool[p].first_child;
      while (c != NIL && pool[c].rank >= r) {
        prev = c;
        c = pool[c].next_sibling;
      }
      if (c == NIL) return;
      (prev == NIL ? pool[p].first_child : pool[prev].next_sibling) = pool[c].next_sibling;
      append(pool[p].ends, pool[c].ends);
      for_each_child(c, [&](const int g) { attach(p, g); });
    }
  }
};

/** Each object's top-k closest distinct partners, deepest trie groups first. */
std::vector<std::vector<int>> find_candidates(
  const Tips &tips, const Estimator &est, const Objects &ob, const int k, const int pool_size,
  i64 &pool_pairs
) {
  const i64 m = ob.rep.size();
  std::vector<int> order(m);
  std::iota(order.begin(), order.end(), 0);
  std::stable_sort(order.begin(), order.end(),
                   [&](int x, int y) { return tips.T[ob.rep[x]] < tips.T[ob.rep[y]]; });
  ListTrie trie;
  std::vector<std::vector<int>> nbrs(m);
  std::vector<std::pair<int, int>> groups;
  std::vector<int> chosen;
  std::vector<std::pair<double, int>> scored;
  for (const int o : order) {
    const i64 b = ob.rep[o];
    const auto ranks = tips.ranks_of(b);
    const auto diffs = tips.diffs_of(b);
    groups.clear();
    int node = 0;
    bool matched_all = true;
    for (size_t i = 0; i < ranks.size(); ++i) {
      trie.consolidate(node, ranks[i]);
      if (!trie.pool[node].ends.empty()) groups.emplace_back(4 * (int)i, -node - 1);
      int match = NIL;
      trie.for_each_child(node, [&](const int c) {
        if (trie.pool[c].d == diffs[i]) {
          match = c;
        } else {
          groups.emplace_back(4 * (int)i + 2, c);
        }
      });
      if (match == NIL) {
        matched_all = false;
        break;
      }
      node = match;
    }
    if (matched_all) groups.emplace_back(4 * (int)ranks.size(), node);
    std::stable_sort(groups.begin(), groups.end(), [](auto x, auto y) { return x.first > y.first; });
    chosen.clear();
    for (const auto &[key, g] : groups) {
      const auto &lst = g < 0 ? trie.pool[-g - 1].ends : trie.pool[g].tips;
      for (const int t : lst) {
        if ((int)chosen.size() >= pool_size) break;
        chosen.push_back(t);
      }
      if ((int)chosen.size() >= pool_size) break;
    }
    scored.clear();
    for (const int t : chosen) scored.emplace_back(pair_estimate(tips, est, b, ob.rep[t]), t);
    pool_pairs += chosen.size();
    const int kk = std::min<int>(k, scored.size());
    std::partial_sort(scored.begin(), scored.begin() + kk, scored.end(),
                      [](auto x, auto y) { return x.first > y.first; });
    for (int j = 0; j < kk; ++j) {
      nbrs[o].push_back(scored[j].second);
      nbrs[scored[j].second].push_back(o);
    }
    node = 0;
    trie.pool[node].tips.push_back(o);
    for (size_t i = 0; i < ranks.size(); ++i) {
      trie.consolidate(node, ranks[i]);
      int c = trie.find_child(node, ranks[i], diffs[i]);
      if (c == NIL) {
        c = trie.alloc(ranks[i], diffs[i]);
        trie.link(node, c);
      }
      node = c;
      trie.pool[node].tips.push_back(o);
    }
    trie.pool[node].ends.push_back(o);
  }
  for (auto &v : nbrs) {
    std::sort(v.begin(), v.end());
    v.erase(std::unique(v.begin(), v.end()), v.end());
  }
  return nbrs;
}

struct Link {
  double v;
  bool approx;
};


/** Pool inverted parent/child blocks (child time below parent's), weighted
 *  by w; nodes with w <= 0 are left as is. Keeps the w-weighted total of
 *  times. Returns the number of block merges. */
i64 pool_inversions_impl(const i64 n, const i64 *parent, double *time, const double *w) {
  std::vector<i64> block(n);
  std::iota(block.begin(), block.end(), 0);
  std::vector<double> wsum(w, w + n), tsum(n, 0.0);
  for (i64 u = 0; u < n; ++u) {
    if (w[u] > 0) tsum[u] = w[u] * time[u];
  }
  auto find = [&](i64 v) {
    while (block[v] != v) {
      block[v] = block[block[v]];
      v = block[v];
    }
    return v;
  };
  auto value = [&](const i64 r) { return tsum[r] / wsum[r]; };
  i64 merges = 0;
  bool changed = true;
  while (changed) {
    changed = false;
    for (i64 u = 0; u < n; ++u) {
      const i64 p = parent[u];
      if (p == u || w[u] <= 0 || w[p] <= 0) continue;
      const i64 ru = find(u), rp = find(p);
      if (ru != rp && value(ru) < value(rp) - 1e-12) {
        block[ru] = rp;
        wsum[rp] += wsum[ru];
        tsum[rp] += tsum[ru];
        ++merges;
        changed = true;
      }
    }
  }
  for (i64 u = 0; u < n; ++u) {
    if (w[u] > 0) time[u] = value(find(u));
  }
  return merges;
}

/** Per trie node: sum of estimates and number of tip pairs whose paths
 *  first split at the node (zero except at branching nodes). Nodes must be
 *  topologically sorted, with each ancestor before its descendants. */
void cross_pair_sums_impl(
  const i64 n_nodes, const i64 *anc, const i64 *rank, const i64 *tip_of_node,
  const Tips &tips, const Estimator &est, double *out_sums, i64 *out_counts
) {
  const Tree tree(n_nodes, anc, tip_of_node);
  // all-pairs totals: swept at branching nodes, zero at leaves, and
  // inherited through single-child nodes (children have larger ids)
  std::vector<double> all_sum(n_nodes, 0.0);
  std::vector<i64> all_count(n_nodes, 0);
  LocalTrie trie;
  std::vector<std::pair<i64, i64>> order;
  for (i64 w = n_nodes - 1; w >= 0; --w) {
    const auto kids = tree.kids(w);
    if (kids.size() >= 2) {
      sweep(tips, est, tree.tips_under(w), rank[w], trie, order, all_sum[w], all_count[w]);
    } else if (kids.size() == 1) {
      all_sum[w] = all_sum[kids[0]];
      all_count[w] = all_count[kids[0]];
    }
  }
  for (i64 w = 0; w < n_nodes; ++w) {
    out_sums[w] = all_sum[w];
    out_counts[w] = all_count[w];
    for (const i64 k : tree.kids(w)) {
      out_sums[w] -= all_sum[k];
      out_counts[w] -= all_count[k];
    }
    if (tree.kids(w).size() < 2) out_sums[w] = out_counts[w] = 0;
  }
}

/** Average-linkage UPGMA over all pairwise estimates (larger estimate =
 *  closer). Outputs tips 0..n-1 and merges n..2n-2, parents after children;
 *  the root is its own parent. */
void brute_upgma_impl(
  const i64 n, const Tips &tips, const Estimator &est, i64 *out_parent, double *out_time
) {
  for (i64 v = 0; v < 2 * n - 1; ++v) {
    out_parent[v] = v;
    out_time[v] = std::numeric_limits<double>::quiet_NaN();
  }
  if (n < 2) return;
  std::vector<double> D((size_t)n * n, 0.0);
  for (i64 a = 0; a < n; ++a) {
    for (i64 b = a + 1; b < n; ++b) {
      D[a * n + b] = D[b * n + a] = pair_estimate(tips, est, a, b);
    }
  }
  std::vector<double> size(n, 1.0);
  std::vector<i64> node_of(n);
  std::iota(node_of.begin(), node_of.end(), 0);
  std::vector<char> alive(n, 1);
  std::vector<i64> chain;
  i64 n_alive = n, next_out = n;
  while (n_alive > 1) {
    if (chain.empty()) {
      chain.push_back(std::find(alive.begin(), alive.end(), 1) - alive.begin());
    }
    const i64 X = chain.back();
    const i64 prev = chain.size() > 1 ? chain[chain.size() - 2] : -1;
    i64 best = prev;
    double best_v = prev >= 0 ? D[X * n + prev] : -std::numeric_limits<double>::infinity();
    for (i64 Y = 0; Y < n; ++Y) {
      if (Y != X && alive[Y] && D[X * n + Y] > best_v) {
        best = Y;
        best_v = D[X * n + Y];
      }
    }
    if (best != prev) {
      chain.push_back(best);
      continue;
    }
    chain.pop_back();
    chain.pop_back();
    // merge prev into X's slot
    const i64 A = X, B = prev;
    const i64 u = next_out++;
    out_parent[node_of[A]] = u;
    out_parent[node_of[B]] = u;
    out_time[u] = best_v;
    for (i64 C = 0; C < n; ++C) {
      if (!alive[C] || C == A || C == B) continue;
      const double v = (size[A] * D[A * n + C] + size[B] * D[B * n + C]) / (size[A] + size[B]);
      D[A * n + C] = D[C * n + A] = v;
    }
    size[A] += size[B];
    alive[B] = 0;
    node_of[A] = u;
    --n_alive;
  }
}

void scaffold_upgma_impl(
  const i64 n_tips,
  const i64 *tip_T, const i64 *tip_off, const i64 *tip_ranks, const u64 *tip_diffs,
  const double p, const double t0,
  const i64 n_trie, const i64 *trie_anc, const i64 *trie_tip_of_node,  // reconstructed trie
  const i64 k, const i64 pool_size, const i64 n_samples, const i64 direct_max, const u64 seed,
  i64 *out_parent,  // length 2 n_tips; tips are 0..n-1; parents have larger ids
  double *out_time,  // node times (NaN for tips)
  i64 *out_n_nodes,  // number of nodes used
  i64 *out_stats  // [objects, pool pairs, candidate pairs, direct pairs, sampled,
                  //  height sweeps, sweep work, fallbacks, inversions, pool merges]
) {
  const Tips tips{tip_T, tip_off, tip_ranks, tip_diffs};
  const Estimator est{p, t0};
  const i64 n = n_tips;
  for (int s = 0; s < 10; ++s) out_stats[s] = 0;
  for (i64 v = 0; v < 2 * n; ++v) {
    out_parent[v] = v;
    out_time[v] = std::numeric_limits<double>::quiet_NaN();
  }
  *out_n_nodes = n;
  if (n < 2) return;

  const Objects ob = deduplicate(tips, n);
  const i64 m = ob.rep.size();
  out_stats[0] = m;

  // output ids: tips 0..n-1, then count - 1 nodes per object with count >= 2,
  // then cluster merges; node_of[cluster] is its output node
  i64 next_out = n;
  std::vector<i64> node_of(2 * m - 1, -1);
  for (i64 o = 0; o < m; ++o) {
    if (ob.count[o] == 1) {
      node_of[o] = ob.tips[o][0];
    } else {
      // identical tips merge first, all at their pairwise estimate; output
      // as a binary chain, as UPGMA over individual tips would give
      const double t_same = pair_estimate(tips, est, ob.rep[o], ob.rep[o]);
      i64 below = ob.tips[o][0];
      for (size_t j = 1; j < ob.tips[o].size(); ++j) {
        const i64 u = next_out++;
        out_time[u] = t_same;
        out_parent[below] = u;
        out_parent[ob.tips[o][j]] = u;
        below = u;
      }
      node_of[o] = below;
    }
  }

  if (m == 1) {
    *out_n_nodes = next_out;
    return;
  }

  i64 pool_pairs = 0;
  auto nbrs = find_candidates(tips, est, ob, (int)k, (int)pool_size, pool_pairs);
  out_stats[1] = pool_pairs;

  std::mt19937_64 rng(seed);
  const i64 n_clusters = 2 * m - 1;
  std::vector<std::vector<int>> objs(n_clusters);  // cluster -> objects
  std::vector<std::vector<int>> draws(n_clusters);  // cluster -> object per tip, for sampling
  std::vector<double> size(n_clusters, 0.0);  // tips in cluster
  std::vector<int> owner(m);
  std::vector<std::unordered_map<int, Link>> D(n_clusters);
  for (int o = 0; o < m; ++o) {
    objs[o] = {o};
    draws[o].assign(ob.count[o], o);
    size[o] = ob.count[o];
    owner[o] = o;
  }
  for (int i = 0; i < m; ++i) {
    for (const int j : nbrs[i]) {
      if (i < j) {
        const double v = pair_estimate(tips, est, ob.rep[i], ob.rep[j]);
        D[i][j] = D[j][i] = Link{v, false};
        ++out_stats[2];
      }
    }
  }
  std::vector<std::vector<int>>().swap(nbrs);

  auto compute = [&](const int A, const int B) -> Link {
    const auto &oA = objs[A], &oB = objs[B];
    if ((i64)oA.size() * (i64)oB.size() <= direct_max) {
      double s = 0;
      for (const int a : oA) {
        for (const int b : oB) {
          s += (double)ob.count[a] * ob.count[b] * pair_estimate(tips, est, ob.rep[a], ob.rep[b]);
        }
      }
      out_stats[3] += oA.size() * oB.size();
      return Link{s / (size[A] * size[B]), false};
    }
    const auto &dA = draws[A], &dB = draws[B];  // uniform over tips
    std::uniform_int_distribution<size_t> ua(0, dA.size() - 1), ub(0, dB.size() - 1);
    double s = 0;
    for (i64 j = 0; j < n_samples; ++j) {
      s += pair_estimate(tips, est, ob.rep[dA[ua(rng)]], ob.rep[dB[ub(rng)]]);
    }
    ++out_stats[4];
    return Link{s / n_samples, true};
  };

  const Tree trie_tree(n_trie, trie_anc, trie_tip_of_node);
  std::vector<i64> leaf_of(n, -1);
  for (i64 v = 0; v < n_trie; ++v) {
    if (trie_tip_of_node[v] >= 0) leaf_of[trie_tip_of_node[v]] = v;
  }
  auto add_fallback = [&](const int A) {
    ++out_stats[7];
    i64 v = leaf_of[ob.rep[objs[A][0]]];
    std::vector<int> found;
    while (true) {
      const i64 up = trie_anc[v];
      for (const i64 t : trie_tree.tips_under(up)) {
        const int C = owner[ob.of_tip[t]];
        if (C != A) found.push_back(C);
        if (found.size() >= 200) break;
      }
      if (!found.empty() || up == v) break;
      v = up;
    }
    std::sort(found.begin(), found.end());
    found.erase(std::unique(found.begin(), found.end()), found.end());
    for (const int C : found) {
      if (!D[A].count(C)) {
        const Link l = compute(A, C);
        D[A][C] = D[C][A] = l;
      }
    }
  };

  std::vector<int> chain, pos(n_clusters, -1);
  std::vector<char> alive(n_clusters, 0), sampled_merge(n_clusters, 0);
  std::fill(alive.begin(), alive.begin() + m, 1);
  std::vector<int> kid1(n_clusters, -1), kid2(n_clusters, -1);
  i64 n_alive = m, next_id = m, scan = 0;
  auto push = [&](const int c) {
    pos[c] = chain.size();
    chain.push_back(c);
  };
  auto pop = [&]() {
    pos[chain.back()] = -1;
    chain.pop_back();
  };
  while (n_alive > 1) {
    if (chain.empty()) {
      while (!alive[scan]) ++scan;
      push(scan);
    }
    const int X = chain.back();
    if (D[X].empty()) add_fallback(X);
    const int prev = chain.size() > 1 ? chain[chain.size() - 2] : -1;
    int best = -1;
    double best_v = -std::numeric_limits<double>::infinity();
    for (const auto &[Y, l] : D[X]) {
      if (l.v > best_v || (l.v == best_v && (Y == prev || (best != prev && Y < best)))) {
        best = Y;
        best_v = l.v;
      }
    }
    if (best == prev) {
      pop();
      pop();
      const int A = X, B = best;
      const int U = next_id++;
      const double nA = size[A], nB = size[B];
      sampled_merge[U] = D[A][B].approx;
      // U takes over the larger child's neighbor map (O(1) move); its
      // entries are updated in place, and entries only the smaller child had
      // are spliced in as nodes, with no allocation
      const bool a_big = D[A].size() >= D[B].size();
      const int Bg = a_big ? A : B, Sm = a_big ? B : A;
      const double nBg = a_big ? nA : nB, nSm = a_big ? nB : nA;
      D[U].swap(D[Bg]);
      D[U].erase(Sm);
      D[Sm].erase(Bg);
      auto merged = [&](const Link &big, const Link &sm) {
        return Link{(nBg * big.v + nSm * sm.v) / (nBg + nSm), big.approx || sm.approx};
      };
      // rename C's entry for the larger child to U, dropping the smaller's
      auto rekey = [&](const int C, const int from, const Link &lu) {
        auto nh = D[C].extract(from);
        nh.key() = U;
        nh.mapped() = lu;
        D[C].insert(std::move(nh));
      };
      for (auto &[C, l] : D[U]) {
        auto is = D[Sm].find(C);
        Link ls;
        if (is != D[Sm].end()) {
          ls = is->second;
          D[Sm].erase(is);
          D[C].erase(Sm);
        } else {
          ls = compute(Sm, C);
        }
        l = merged(l, ls);
        rekey(C, Bg, l);
      }
      while (!D[Sm].empty()) {
        auto nh = D[Sm].extract(D[Sm].begin());
        const int C = nh.key();
        const Link lu = merged(compute(Bg, C), nh.mapped());
        nh.mapped() = lu;
        D[U].insert(std::move(nh));
        rekey(C, Sm, lu);
      }
      for (auto *lists : {&objs, &draws}) {
        auto &L = *lists;
        if (L[A].size() < L[B].size()) {
          L[U].swap(L[B]);
          L[U].insert(L[U].end(), L[A].begin(), L[A].end());
        } else {
          L[U].swap(L[A]);
          L[U].insert(L[U].end(), L[B].begin(), L[B].end());
        }
        std::vector<int>().swap(L[A]);
        std::vector<int>().swap(L[B]);
      }
      size[U] = nA + nB;
      for (const int o : objs[U]) owner[o] = U;
      std::unordered_map<int, Link>().swap(D[A]);
      std::unordered_map<int, Link>().swap(D[B]);
      const i64 u = next_out++;
      node_of[U] = u;
      out_parent[node_of[A]] = u;
      out_parent[node_of[B]] = u;
      out_time[u] = best_v;
      kid1[U] = A;
      kid2[U] = B;
      alive[A] = alive[B] = 0;
      alive[U] = 1;
      --n_alive;
    } else if (pos[best] >= 0) {
      while (chain.back() != best) pop();
      push(X);
    } else {
      push(best);
    }
  }
  const i64 n_out = next_out;
  *out_n_nodes = n_out;

  // exact heights where merge decisions used sampled values
  LocalTrie lt;
  std::vector<std::pair<i64, i64>> ord;
  auto objs_of = [&](const int c, std::vector<i64> &out) {
    out.clear();
    std::vector<int> st{c};
    while (!st.empty()) {
      const int x = st.back();
      st.pop_back();
      if (x < m) {
        out.push_back(x);
      } else {
        st.push_back(kid1[x]);
        st.push_back(kid2[x]);
      }
    }
  };
  // all-pairs totals between distinct objects, carried bottom-up:
  // all(U) = all(A) + all(B) + cross(A, B), and cross is exact once the
  // merge's height is, so a sampled merge needs one sweep of A u B only
  std::vector<double> all_sum(n_clusters, 0.0);
  std::vector<i64> both;
  for (i64 U = m; U < n_clusters; ++U) {  // children have smaller ids
    const int A = kid1[U], B = kid2[U];
    const double pairs = size[A] * size[B];
    if (sampled_merge[U]) {
      objs_of(U, both);
      double s_all, c_all;
      weighted_sweep(tips, est, ob, both, lt, ord, s_all, c_all);
      all_sum[U] = s_all;
      out_time[node_of[U]] = (s_all - all_sum[A] - all_sum[B]) / pairs;
      ++out_stats[5];
      out_stats[6] += both.size();
    } else {
      all_sum[U] = all_sum[A] + all_sum[B] + out_time[node_of[U]] * pairs;
    }
  }

  // pool inversions, weighted by cross-pair counts (keeps the all-pairs total)
  std::vector<double> sz(n_out, 0.0), sq(n_out, 0.0), w(n_out, 0.0);
  for (i64 v = 0; v < n; ++v) sz[v] = 1;
  for (i64 v = 0; v < n_out - 1; ++v) {  // children have smaller ids
    if (v >= n) w[v] = (sz[v] * sz[v] - sq[v]) / 2;
    sz[out_parent[v]] += sz[v];
    sq[out_parent[v]] += sz[v] * sz[v];
  }
  const i64 root = n_out - 1;
  w[root] = (sz[root] * sz[root] - sq[root]) / 2;
  for (i64 u = n; u < root; ++u) {
    if (out_time[u] < out_time[out_parent[u]]) ++out_stats[8];
  }
  out_stats[9] = pool_inversions_impl(n_out, out_parent, out_time, w.data());
}

/** CSR tip data, checked and held for the duration of a call. */
struct TipArrays {
  py::array_t<i64, py::array::c_style | py::array::forcecast> T, off, ranks;
  py::array_t<u64, py::array::c_style | py::array::forcecast> diffs;

  Tips view() const { return Tips{T.data(), off.data(), ranks.data(), diffs.data()}; }
  i64 n() const { return T.size(); }

  void check() const {
    if (off.size() != T.size() + 1) throw std::invalid_argument("tip_off must have len(tip_T) + 1 entries");
    if (ranks.size() != diffs.size()) throw std::invalid_argument("tip_ranks and tip_diffs differ in length");
    if (off.at(0) != 0 || off.at(off.size() - 1) != ranks.size()) {
      throw std::invalid_argument("tip_off must run from 0 to len(tip_ranks)");
    }
  }
};

using i64_array = py::array_t<i64, py::array::c_style | py::array::forcecast>;
using u64_array = py::array_t<u64, py::array::c_style | py::array::forcecast>;
using f64_array = py::array_t<double, py::array::c_style | py::array::forcecast>;

}  // namespace

PYBIND11_MODULE(_origin_time_cpp_impl, m) {
  m.doc() = "Tree-free pairwise origin-time estimates over surface tips.";

  m.def(
    "cross_pair_sums",
    [](const i64_array &ancestor_ids, const i64_array &ranks, const i64_array &tip_of_node,
       const i64_array &tip_T, const i64_array &tip_off, const i64_array &tip_ranks,
       const u64_array &tip_diffs, const double p, const double t0) {
      const TipArrays ta{tip_T, tip_off, tip_ranks, tip_diffs};
      ta.check();
      const i64 n = ancestor_ids.size();
      if (ranks.size() != n || tip_of_node.size() != n) {
        throw std::invalid_argument("node arrays differ in length");
      }
      for (i64 v = 0; v < n; ++v) {
        const i64 a = ancestor_ids.at(v), t = tip_of_node.at(v);
        if (a < 0 || a > v) throw std::invalid_argument("nodes must be topologically sorted, with contiguous ids");
        if (t < -1 || t >= ta.n()) throw std::invalid_argument("tip_of_node out of range");
      }
      f64_array sums(n);
      i64_array counts(n);
      {
        py::gil_scoped_release release;
        cross_pair_sums_impl(n, ancestor_ids.data(), ranks.data(), tip_of_node.data(), ta.view(),
                             Estimator{p, t0}, sums.mutable_data(), counts.mutable_data());
      }
      return std::make_tuple(sums, counts);
    },
    py::arg("ancestor_ids"), py::arg("ranks"), py::arg("tip_of_node"), py::arg("tip_T"),
    py::arg("tip_off"), py::arg("tip_ranks"), py::arg("tip_diffs"), py::arg("p"), py::arg("t0"),
    R"(Per-node sums and counts of pairwise estimates over cross-child tip pairs.)"
  );

  m.def(
    "pool_inversions",
    [](const i64_array &ancestor_ids, const f64_array &times, const f64_array &weights) {
      const i64 n = ancestor_ids.size();
      if (times.size() != n || weights.size() != n) throw std::invalid_argument("arrays differ in length");
      for (i64 v = 0; v < n; ++v) {
        if (ancestor_ids.at(v) < 0 || ancestor_ids.at(v) >= n) throw std::invalid_argument("ancestor_ids out of range");
      }
      f64_array out(n);
      std::copy(times.data(), times.data() + n, out.mutable_data());
      const i64 merges = pool_inversions_impl(n, ancestor_ids.data(), out.mutable_data(), weights.data());
      return std::make_tuple(out, merges);
    },
    py::arg("ancestor_ids"), py::arg("times"), py::arg("weights"),
    R"(Pool inverted parent/child time blocks, keeping weighted totals.)"
  );

  m.def(
    "scaffold_upgma",
    [](const i64_array &tip_T, const i64_array &tip_off, const i64_array &tip_ranks,
       const u64_array &tip_diffs, const double p, const double t0,
       const i64_array &trie_ancestor_ids, const i64_array &trie_tip_of_node, const i64 k,
       const i64 pool_size, const i64 n_samples, const i64 direct_max, const u64 seed) {
      const TipArrays ta{tip_T, tip_off, tip_ranks, tip_diffs};
      ta.check();
      const i64 n = ta.n(), n_trie = trie_ancestor_ids.size();
      if (trie_tip_of_node.size() != n_trie) throw std::invalid_argument("trie arrays differ in length");
      std::vector<char> seen(n, 0);
      for (i64 v = 0; v < n_trie; ++v) {
        const i64 a = trie_ancestor_ids.at(v), t = trie_tip_of_node.at(v);
        if (a < 0 || a >= n_trie) throw std::invalid_argument("trie_ancestor_ids out of range");
        if (t < -1 || t >= n) throw std::invalid_argument("trie_tip_of_node out of range");
        if (t >= 0) seen[t] = 1;
      }
      if (std::find(seen.begin(), seen.end(), 0) != seen.end()) {
        throw std::invalid_argument("every tip must be a trie leaf");
      }
      std::vector<i64> parent(std::max<i64>(2 * n, 1));
      std::vector<double> time(std::max<i64>(2 * n, 1));
      i64 n_nodes = 0;
      std::vector<i64> stats(10, 0);
      {
        py::gil_scoped_release release;
        scaffold_upgma_impl(n, ta.T.data(), ta.off.data(), ta.ranks.data(), ta.diffs.data(), p, t0,
                            n_trie, trie_ancestor_ids.data(), trie_tip_of_node.data(), k, pool_size,
                            n_samples, direct_max, seed, parent.data(), time.data(), &n_nodes,
                            stats.data());
      }
      i64_array out_parent(n_nodes);
      f64_array out_time(n_nodes);
      std::copy(parent.begin(), parent.begin() + n_nodes, out_parent.mutable_data());
      std::copy(time.begin(), time.begin() + n_nodes, out_time.mutable_data());
      const char *names[] = {"objects", "pool_pairs", "candidate_pairs", "direct_pairs", "sampled",
                             "height_sweeps", "sweep_work", "fallbacks",
                             "inversions_before_pooling", "pool_merges"};
      py::dict stat_dict;
      for (int s = 0; s < 10; ++s) stat_dict[names[s]] = stats[s];
      return std::make_tuple(out_parent, out_time, stat_dict);
    },
    py::arg("tip_T"), py::arg("tip_off"), py::arg("tip_ranks"), py::arg("tip_diffs"), py::arg("p"),
    py::arg("t0"), py::arg("trie_ancestor_ids"), py::arg("trie_tip_of_node"), py::arg("k") = 5,
    py::arg("pool_size") = 10, py::arg("n_samples") = 64, py::arg("direct_max") = 64,
    py::arg("seed") = 1,
    R"(Scaffold average-linkage UPGMA over tips; returns (parent, time, stats).)"
  );

  m.def(
    "brute_upgma",
    [](const i64_array &tip_T, const i64_array &tip_off, const i64_array &tip_ranks,
       const u64_array &tip_diffs, const double p, const double t0) {
      const TipArrays ta{tip_T, tip_off, tip_ranks, tip_diffs};
      ta.check();
      const i64 n = ta.n(), n_out = std::max<i64>(2 * n - 1, 0);
      i64_array parent(n_out);
      f64_array time(n_out);
      if (n > 0) {
        py::gil_scoped_release release;
        brute_upgma_impl(n, ta.view(), Estimator{p, t0}, parent.mutable_data(), time.mutable_data());
      }
      return std::make_tuple(parent, time);
    },
    py::arg("tip_T"), py::arg("tip_off"), py::arg("tip_ranks"), py::arg("tip_diffs"), py::arg("p"),
    py::arg("t0"),
    R"(Average-linkage UPGMA over all pairwise estimates; returns (parent, time).)"
  );

  m.def(
    "pair_estimate",
    [](const i64_array &tip_T, const i64_array &tip_off, const i64_array &tip_ranks,
       const u64_array &tip_diffs, const double p, const double t0, const i64 a, const i64 b) {
      const TipArrays ta{tip_T, tip_off, tip_ranks, tip_diffs};
      ta.check();
      if (a < 0 || b < 0 || a >= ta.n() || b >= ta.n()) throw std::out_of_range("tip index");
      return pair_estimate(ta.view(), Estimator{p, t0}, a, b);
    },
    py::arg("tip_T"), py::arg("tip_off"), py::arg("tip_ranks"), py::arg("tip_diffs"), py::arg("p"),
    py::arg("t0"), py::arg("a"), py::arg("b"),
    R"(Pairwise estimate for one tip pair.)"
  );
}

/*
<%
cfg['extra_compile_args'] = ['-std=c++20', '-Wall', '-Wextra']
setup_pybind11(cfg)
%>
*/
