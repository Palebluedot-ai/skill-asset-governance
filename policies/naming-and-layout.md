# Naming & Layout Policy

## 1) 命名规则

- skill 名称必须是 `kebab-case`
- 必须全局唯一（在 `registry/skill-index.yaml` 中不可重复）
- 建议前缀按域划分：
  - `github-*` / `hermes-*` / `otc-*` / `inbox-*`

## 2) 目录规则

- 每个 skill 必须有独立目录，且包含 `SKILL.md`
- 可选资源仅允许：`references/`, `templates/`, `scripts/`, `assets/`
- 禁止跨 skill 相对路径引用（避免隐式耦合）

## 3) 元数据最小集合

`SKILL.md` frontmatter 必须包含：
- `name`
- `description`
- `version`
- `author`
- `license`
