# Lifecycle Policy

## 状态机

`draft -> active -> deprecated -> archived`

## 规则

- draft: 可实验，不默认加载
- active: 可被正常召回
- deprecated: 保留但提示替代技能
- archived: 不再召回，仅历史留档

## 与 Skills Curator 的联动

- Curator 负责状态迁移动作（如 active -> deprecated -> archived）
- 每次 Curator 执行后，必须同步更新 `registry/skill-index.yaml`
- CI 以 registry 为准校验“唯一 canonical skill”与状态一致性

## 变更要求

- 每次改动必须更新版本号
- 重大改动（breaking）必须写迁移说明
- 每月至少执行一次冲突扫描与老化扫描
