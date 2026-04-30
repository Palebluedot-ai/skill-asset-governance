# Lifecycle Policy

## 状态机

`draft -> active -> deprecated -> archived`

## 规则

- draft: 可实验，不默认加载
- active: 可被正常召回
- deprecated: 保留但提示替代技能
- archived: 不再召回，仅历史留档

## 变更要求

- 每次改动必须更新版本号
- 重大改动（breaking）必须写迁移说明
- 每月至少执行一次冲突扫描与老化扫描
