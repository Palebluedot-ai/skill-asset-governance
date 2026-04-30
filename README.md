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
python3 scripts/lint_skill_assets.py --root .
python3 scripts/build_skill_report.py --root . --out reports/skill-report.md
```

## 防崩溃结论（先给答案）

Skills 多了不会直接导致“系统崩溃”，但会导致：
1. 召回冲突（同类技能被误选）
2. 指令冲突（两个技能给相反步骤）
3. 维护漂移（旧技能长期不更新）

本仓库通过“规则 + 脚本 + CI”把上述风险前置为可检测问题。
