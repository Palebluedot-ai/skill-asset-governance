# Skill Asset Governance

用于治理 Hermes Skills 资产，避免命名冲突、行为冲突、重复技能和不可追溯变更。

## 目标

- 统一 Skills 命名、分类、版本与变更流程
- 在提交前自动检测冲突风险
- 将“技能资产管理”从临时对话变成可审计工程流程

## 仓库结构

```text
skill-asset-governance/
├─ policies/
│  ├─ naming-and-layout.md
│  ├─ conflict-policy.md
│  └─ lifecycle-policy.md
├─ registry/
│  └─ skill-index.yaml
├─ scripts/
│  ├─ lint_skill_assets.py
│  └─ build_skill_report.py
├─ reports/
│  └─ .gitkeep
└─ .github/workflows/
   └─ skill-governance-ci.yml
```

## 快速开始

```bash
cd ~/projects/skill-asset-governance
# 1) 先用 Hermes Skills Curator 做官方整理（去重/归档/重命名）
# 2) 同步 registry（本地执行）
python3 scripts/sync_from_hermes_skills.py --source ~/.hermes/skills --out registry/skill-index.yaml

# 3) 治理检查（check-only，不改写 skills）
python3 scripts/lint_skill_assets.py \
  --source ~/.hermes/skills \
  --waivers policies/waivers.yaml \
  --report-json reports/lint-report.json
python3 scripts/validate_registry.py --registry registry/skill-index.yaml
python3 scripts/build_skill_report.py --root . --out reports/skill-report.md
```

## Curator + Governance 分工

## CI 门禁策略

- `FAIL > 0`：CI **阻断**（红灯）
- `WARN > 0`：默认仅提示（黄灯，不阻断）
- 可选严格模式：本地执行 `python3 scripts/enforce_gate.py --lint-json reports/lint-report.json --fail-on-warn`


- **Skills Curator**：负责“资产整理动作”（清洗、去重、迁移、归档）
- **Governance Repo**：负责“规则执行与审计证据”（policy、lint、report、CI）

原则：**Curator 先执行，Governance 后验收**。

## 审计与回滚

```bash
# Curator 运行前后分别保存 index 快照，然后生成审计报告
cp registry/skill-index.yaml reports/index-before.yaml
# ... run curator + sync ...
cp registry/skill-index.yaml reports/index-after.yaml
python3 scripts/curator_audit.py \
  --before reports/index-before.yaml \
  --after reports/index-after.yaml \
  --out reports/curator-run-latest.md

# 若需要回滚 registry 到某次提交
python3 scripts/rollback_registry.py --to <commit_sha>
```


## 防崩溃结论（先给答案）

Skills 多了不会直接导致“系统崩溃”，但会导致：
1. 召回冲突（同类技能被误选）
2. 指令冲突（两个技能给相反步骤）
3. 维护漂移（旧技能长期不更新）

本仓库通过“规则 + 脚本 + CI”把上述风险前置为可检测问题。
