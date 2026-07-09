# 云端 Skill 目录

本仓库 `.cursor/skills/` 下所有 skill 的目录清单与用途说明。

- 已启用 skill（`SKILL.md`）：15 个
- 分类占位目录（`README.md`，尚未填充具体 skill）：`方法类`、`算法类` 的撰写目录、`审查意见答复` 等

## 目录树

```
.cursor/skills/
└── 专利/
    ├── 专利撰写/
    │   ├── 结构类/
    │   │   ├── 权利要求撰写/
    │   │   │   ├── patent-structural-claim-drafting/SKILL.md
    │   │   │   ├── patent-avoid-unnecessary-functional-limitation/SKILL.md
    │   │   │   └── patent-directional-terms-need-reference/SKILL.md
    │   │   └── 说明书撰写/README.md
    │   ├── 方法类/
    │   │   ├── 权利要求撰写/README.md
    │   │   └── 说明书撰写/README.md
    │   ├── 算法类/
    │   │   ├── 权利要求撰写/README.md
    │   │   └── 说明书撰写/README.md
    │   └── 通用/
    │       ├── 撰写策略/
    │       │   └── patent-application-drafting-strategy/SKILL.md
    │       ├── 权利要求撰写/
    │       │   ├── patent-claims-clarity-and-logic/SKILL.md
    │       │   ├── patent-claims-formal-compliance/SKILL.md
    │       │   └── patent-independent-claim-necessary-features-check/SKILL.md
    │       └── 说明书撰写/
    │           ├── patent-technical-field-sentence-pattern/SKILL.md
    │           ├── patent-technical-problem-statement-pattern/SKILL.md
    │           ├── patent-beneficial-effects-statement-pattern/SKILL.md
    │           ├── patent-specific-embodiment-drafting/SKILL.md
    │           ├── patent-drawings-description-drafting/SKILL.md
    │           └── patent-background-technology-drafting/SKILL.md
    ├── 审查意见答复/README.md
    ├── 权利要求质检/
    │   └── patent-claims-quality-review/SKILL.md
    └── 说明书质检/
        └── patent-description-clarity-and-logic/SKILL.md
```

## Skill 清单与用途

### 专利撰写 · 结构类 · 权利要求撰写

| Skill | 用途 |
|---|---|
| `patent-structural-claim-drafting` | 装置类/结构类独立权利要求：先完整列出全部部件，再逐一展开连接关系与结构特征，禁止边列边展开。 |
| `patent-avoid-unnecessary-functional-limitation` | 默认用结构、位置、连接关系限定特征；仅当结构性描述无法表达清楚，或功能性表述更清楚简洁时才用功能性限定。 |
| `patent-directional-terms-need-reference` | 方向/方位类词汇（周向、轴向、径向、转动、平行、垂直等）必须点明参照物（相对哪个轴线/平面/部件）。 |

### 专利撰写 · 通用 · 撰写策略

| Skill | 用途 |
|---|---|
| `patent-application-drafting-strategy` | 撰写全新专利申请前的整体策略规划：商业前景与抵御方向、保护范围与稳定性、侵权判定友好性、竞争对手规避设计、权利要求布局五个维度。 |

### 专利撰写 · 通用 · 权利要求撰写

| Skill | 用途 |
|---|---|
| `patent-claims-clarity-and-logic` | 权利要求清楚性与逻辑自查：孤岛特征、突兀的人为定义术语、模糊用语、歧义与反例、物理/数学常识、术语一致性、编号来源对应。 |
| `patent-claims-formal-compliance` | 从属权利要求形式核对：引用方向、多项从属引用方式、引用编号与主题名称、编号连续性、固定句式等硬性格式规则。 |
| `patent-independent-claim-necessary-features-check` | 检查独立权利要求中每个特征是否为解决所声称技术问题的必要技术特征，避免夹带可降级到从权的内容。 |

### 专利撰写 · 通用 · 说明书撰写

| Skill | 用途 |
|---|---|
| `patent-technical-field-sentence-pattern` | "技术领域"固定句式："本发明/实用新型涉及XXX技术领域，具体涉及（专利名称）。" |
| `patent-technical-problem-statement-pattern` | "要解决的技术问题"固定句式，XXXX 精准对应独权实际解决的技术问题。 |
| `patent-background-technology-drafting` | "背景技术"规范：先客观描述现有技术，再用"然而"归纳 2~3 个与权利要求对应的问题，固定句式收尾。 |
| `patent-beneficial-effects-statement-pattern` | "有益效果"只描述独权核心特征带来的效果，与技术问题陈述一一镜像呼应。 |
| `patent-specific-embodiment-drafting` | "具体实施方式"：先复述对应权利要求，再用"具体而言，"逐条展开每个特征的原理、作用与实施方式。 |
| `patent-drawings-description-drafting` | "附图说明"：依据交底书已有附图撰写、缺图要提醒补充，方法类图1必须是流程图，固定标点排版模版。 |

### 专利 · 质检

| Skill | 用途 |
|---|---|
| `patent-claims-quality-review` | 权利要求书整体质检：保护范围与创造性平衡、从属权利要求梯度防御布局、引用编号、逻辑与表达。 |
| `patent-description-clarity-and-logic` | 说明书"具体实施方式"质检：孤岛特征、人为定义术语、模糊用语、歧义与反例、物理/数学常识与逻辑一致性。 |
