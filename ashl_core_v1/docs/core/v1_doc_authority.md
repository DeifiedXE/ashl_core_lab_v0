# ASHL Core v1 文件權威順序

## 第一層：精簡核心文件

1. `ashl_core_v1/docs/core/v1_master_construction_blueprint.md`
2. `ashl_core_v1/docs/core/v1_core_overview.md`
3. `ashl_core_v1/docs/core/v1_module_requirements.md`
4. `ashl_core_v1/docs/core/v1_learning_memory_flow.md`
5. `ashl_core_v1/docs/core/v1_deferred_lines.md`
6. `ashl_core_v1/docs/core/v1_concept_source_map.md`
7. `ashl_core_v1/docs/core/v1_doc_authority.md`

## 第二層：v1 原始對齊文件

8. `ashl_core_v1/docs/nine_line_definition_v0.md`
9. `ashl_core_v1/docs/observation_aligned_product_imagination_v0.md`
10. `ashl_core_v1/docs/legacy_design_doc_alignment_index_v0.md`
11. `ashl_core_v1/docs/clean_rewrite_bootstrap_v1.md`

## 第三層：封存概念來源

12. `docs_archive/v1_concept_sources_2026_06_27/**`

封存來源只作為概念標本。若封存文件與精簡核心文件衝突，以精簡核心文件為準。

## 使用規則

後續 v1 dataclass、module、runtime 設計，先讀總施工藍圖，再讀第一層其他核心文件。需要追溯來源時才讀第三層。

舊文件不再直接驅動 v1 設計；它們只透過精簡核心文件轉譯後進入 v1。
