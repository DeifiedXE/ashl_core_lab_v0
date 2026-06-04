# ASHL Hotfix Smoke Runner

把 `run_all_smoke_tests.py` 放進你的 `ashl_core_lab_v0` 資料夾後執行：

```powershell
chcp 65001
$env:PYTHONUTF8="1"
python -X utf8 run_all_smoke_tests.py
```

成功時會看到 `[PASS]`，並產生 `smoke_test_report.json`。
