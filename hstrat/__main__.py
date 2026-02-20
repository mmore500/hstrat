from ._auxiliary_lib import get_hstrat_version

if __name__ == "__main__":
    print(f"hstrat v{get_hstrat_version()}")
    print(
        """
Available commands (stabilized API):
$ python3 -m hstrat.dataframe.surface_build_tree
$ python3 -m hstrat.dataframe.surface_unpack_reconstruct
$ python3 -m hstrat.dataframe.surface_postprocess_trie

Available commands (experimental API):
$ python3 -m hstrat._auxiliary_lib._alifestd_add_global_root
$ python3 -m hstrat._auxiliary_lib._alifestd_add_inner_knuckles_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_add_inner_leaves
$ python3 -m hstrat._auxiliary_lib._alifestd_add_inner_niblings_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_as_newick_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_assign_contiguous_ids
$ python3 -m hstrat._auxiliary_lib._alifestd_assign_contiguous_ids_polars
$ python3 -m hstrat._auxiliary_lib._alifestd_assign_root_ancestor_token
$ python3 -m hstrat._auxiliary_lib._alifestd_chronological_sort
$ python3 -m hstrat._auxiliary_lib._alifestd_coerce_chronological_consistency
$ python3 -m hstrat._auxiliary_lib._alifestd_collapse_trunk_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_collapse_unifurcations
$ python3 -m hstrat._auxiliary_lib._alifestd_collapse_unifurcations_polars
$ python3 -m hstrat._auxiliary_lib._alifestd_count_root_nodes
$ python3 -m hstrat._auxiliary_lib._alifestd_delete_trunk_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_delete_trunk_asexual_polars
$ python3 -m hstrat._auxiliary_lib._alifestd_delete_unifurcating_roots_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_downsample_tips_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_downsample_tips_canopy_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_downsample_tips_canopy_polars
$ python3 -m hstrat._auxiliary_lib._alifestd_downsample_tips_clade_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_downsample_tips_polars
$ python3 -m hstrat._auxiliary_lib._alifestd_drop_topological_sensitivity
$ python3 -m hstrat._auxiliary_lib._alifestd_drop_topological_sensitivity_polars
$ python3 -m hstrat._auxiliary_lib._alifestd_from_newick
$ python3 -m hstrat._auxiliary_lib._alifestd_from_newick_polars
$ python3 -m hstrat._auxiliary_lib._alifestd_join_roots
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_ancestor_origin_time_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_clade_duration_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_clade_duration_ratio_sister_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_clade_faithpd_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_clade_fblr_growth_children_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_clade_fblr_growth_sister_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_clade_leafcount_ratio_sister_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_clade_logistic_growth_children_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_clade_logistic_growth_sister_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_clade_nodecount_ratio_sister_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_clade_subtended_duration_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_clade_subtended_duration_ratio_sister_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_colless_index_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_colless_index_corrected_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_colless_like_index_mdm_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_colless_like_index_sd_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_colless_like_index_var_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_is_left_child_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_is_right_child_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_leaves
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_leaves_polars
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_left_child_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_max_descendant_origin_time_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_node_depth_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_node_depth_asexual_polars
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_num_children_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_num_children_polars
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_num_descendants_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_num_leaves_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_num_leaves_sibling_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_num_preceding_leaves_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_oldest_root
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_origin_time_delta_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_ot_mrca_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_right_child_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_root_id
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_roots
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_roots_polars
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_sackin_index_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_mark_sister_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_prefix_roots
$ python3 -m hstrat._auxiliary_lib._alifestd_prefix_roots_polars
$ python3 -m hstrat._auxiliary_lib._alifestd_prune_extinct_lineages_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_prune_extinct_lineages_polars
$ python3 -m hstrat._auxiliary_lib._alifestd_reroot_at_id_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_splay_polytomies
$ python3 -m hstrat._auxiliary_lib._alifestd_test_leaves_isomorphic_asexual
$ python3 -m hstrat._auxiliary_lib._alifestd_to_working_format
$ python3 -m hstrat._auxiliary_lib._alifestd_topological_sort
$ python3 -m hstrat._auxiliary_lib._alifestd_try_add_ancestor_id_col
$ python3 -m hstrat._auxiliary_lib._alifestd_try_add_ancestor_id_col_polars
$ python3 -m hstrat._auxiliary_lib._alifestd_try_add_ancestor_list_col
$ python3 -m hstrat._auxiliary_lib._alifestd_try_add_ancestor_list_col_polars

For information on a command, invoke it with the --help flag.
""",
    )
