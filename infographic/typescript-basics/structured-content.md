# Structured Content: TypeScript 基础完全指南信息图

## Title
TypeScript 基础：从 JS 超集到能读懂现代前端代码

## Learning Objectives
The viewer will understand:
1. TS 与 JS 的关系及 .ts → 检查 → .js → 运行 的完整链路
2. 编辑时 / 构建时 / 运行时 三套检查各管什么时候
3. 本章核心类型写法（`: string`、`interface`、`A | B`、`<T>`、`as Type`）及场景
4. 何时值得学 TypeScript

---

## 图1: 静态类型检查三阶段（§3）

**Key Concept**: 静态检查防「你写错」；运行时仍要防「数据不符」

**Content**:
- 你写 .ts 源码 → TS 编译器 / IDE → 类型是否一致?
- 否 → 红线 / 编译失败
- 是 → 生成 .js → 浏览器 / Node 运行 → 运行时仍可能因数据不符而崩
- 1. **编辑时**：IDE 用 TS 语言服务标红、补全
- 2. **构建时**：`tsc` 或 Vite/Webpack 里的 TS 插件；可配置「有类型错误是否阻断发布」
- 3. **运行时**：**没有** TS 类型警察；接口返回的 JSON 若与类型不符，仍可能 `undefined` 或逻辑错误

**Visual Element**:
- Type: horizontal linear-progression flow
- Subject: 5-node pipeline from .ts to runtime
- Treatment: macaron cards per stage, arrows between, coral red for error branch

**Text Labels**:
- Headline: "静态类型与动态类型：两套检查各管什么时候"
- Nodes: ".ts 源码" / "TS 编译器·IDE" / "类型一致?" / "生成 .js" / "浏览器·Node 运行"
- Branch: "红线·编译失败" / "运行时仍可能崩"
- Footer: "类型只活在源码与检查阶段；运行的是 JS"

---

## 图2: 综合概念地图（§14）

**Key Concept**: 把本章名词串成一张表，读懂仓库里的常见写法

**Content**（表格 verbatim）:
| 你看到的写法 | 正式名称 | 通俗说 | 典型场景 |
| `: string` | 类型注解 | 这个变量是字符串 | 变量、参数、返回值 |
| `string \| number` | 联合类型 | 二选一 | ID、多种入参 |
| `"a" \| "b"` | 字面量联合 | 只能是这几个值 | 状态、角色 |
| `interface Foo { }` | 接口 | 对象字段清单 | API、props |
| `type Foo = ...` | 类型别名 | 给类型起名 | 联合、工具类型 |
| `T[]` / `Array<T>` | 泛型数组 | 同类型列表 | 列表数据 |
| `[A, B]` | 元组 | 固定列类型 | 坐标、成对返回 |
| `<T>` | 泛型参数 | 类型的占位符 | `useState<T>`、容器 |
| `as Type` | 类型断言 | 你保证是这个类型 | DOM、遗留 JS |
| `x is Foo` | 类型守卫 | 判断后收窄 | 解析 unknown |
| `?:` | 可选 | 可以没有 | 表单字段、配置项 |

**Visual Element**:
- Type: bento-grid with 11 compact module cells
- Subject: each row as a pastel card with code snippet + label
- Treatment: 3×4 grid layout, code in monospace doodle boxes

**Text Labels**:
- Headline: "综合概念地图：本章名词一览"
- Subhead: "类型是你对数据的承诺，不是服务器的承诺"
- Footer: "TypeScript 基础完全指南 · §14"

---

## 图3: 何时上 TypeScript（§16.2）

**Key Concept**: 决策树帮助判断学 TS 的时机

**Content**（决策树 verbatim）:
```
要开始长期维护的前端/Node 项目？
├─ 是 → 用 TS（或团队已规定）
└─ 否 → 脚本极简、一次性？
    ├─ 是 → JS 即可
    └─ 否 → 会读 TS 文档吗？
        ├─ 需要 → 学本篇
        └─ 不需要 → 暂缓
```

**Visual Element**:
- Type: tree-branching decision flow
- Subject: root question branching to 4 terminal outcomes
- Treatment: stick figure at root, macaron nodes per branch

**Text Labels**:
- Headline: "决策树：何时上 TypeScript"
- Root: "长期维护的前端/Node 项目？"
- Leaves: "用 TS" / "JS 即可" / "学本篇" / "暂缓"
- Footer: "TypeScript 基础完全指南 · §16"

---

## Data Points (Verbatim)

### Core Takeaways (§16.1)
1. **TS = JS + 静态类型**；类型在编译后擦掉，运行的是 JS。
2. **静态检查**防的是「你写错」；**运行时**仍要防「数据不符」。
3. **`any` 慎用，`unknown` 更安全**；外部数据先收窄或校验。
4. **`interface` / `type`** 描述对象与别名；**`|` 联合**、**字面量**描述状态与分支。
5. **泛型 `T`** 是类型占位符；`Foo<Bar>` 读作「Foo 里 T 换成 Bar」。

### JS vs TS (§2)
| 维度 | JavaScript | TypeScript |
| 文件扩展名 | `.js`、`.jsx` | `.ts`、`.tsx` |
| 类型信息 | 运行时才知道 | 编辑期、编译期可检查 |
| 浏览器直接执行 | 可以 | **不行**——需先编译/转译为 JS |

---

## Design Instructions

### Style Preferences
- hand-drawn-edu（EXTEND.md）
- Macaron pastels on warm cream (#F5F0E8)
- Coral red (#E8655A) accents for emphasis
- Stick figures, wavy lines, generous whitespace

### Layout Preferences
- landscape 16:9
- 3 separate images matching nextjs series README format

### Other Requirements
- All text Simplified Chinese
- Legible hand-lettered labels, not overcrowded
