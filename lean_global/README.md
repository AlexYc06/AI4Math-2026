# Lean 4 + Mathlib 环境搭建手册（本机版）

> 最后验证：2026-11-24，Lean `4.35.0-rc4` + Mathlib `25e572b8`（8,628 个 olean）
> 本手册面向"以后每次开新项目都要重来一遍"的场景，照着抄即可。

---

## 0. TL;DR（三条命令）

已有环境（本机现状）：

```powershell
$LEAN = "E:\Coding\Deepseek harness\ai4math\lean_experiment\vendor\lean-v4.35.0-rc4\bin"
$ML   = "E:\Coding\Deepseek harness\ai4math\lean_experiment\vendor\mathlib4"
New-LeanProject -Path "E:\lean\projects\myproj" -Mathlib $ML -LeanBin $LEAN
```

全新机器：跳到 §3-A，十分钟。

---

## 1. 概念：什么能"全局"，什么不能

| | 能否全局 | 说明 |
|---|---|---|
| **Lean 编译器** | ✅ 可以 | 由 **Elan** 管理，装在 `%USERPROFILE%\.elan`，`elan` 按目录里的 `lean-toolchain` 自动切换版本 |
| **Mathlib** | ❌ **不行** | 它是 Lake 的**项目依赖**，每个项目在自己的 `.lake\packages\mathlib` 里有一份 |

所以"全局 mathlib"只能这样做：

> **一份共享检出 + 各项目用 `path` 依赖指向它。**

一份 mathlib 只能服务**一个 Lean 版本**。这是硬约束。

---

## 2. 目录布局（照这个摆，后面所有命令都能照抄）

```
E:\lean\                          ← 全局根（自己定，建议独立盘符/目录）
├── mathlib4\                     ← 唯一一份 mathlib，clone 一次、编译一次
└── projects\
    ├── playground\               ← 随手实验都放这里
    ├── ns-audit\                 ← 具体项目
    └── euler-audit\
```

**关键规则：mathlib 与所有项目放在同一个根下。** 不要把 mathlib 塞在某个项目内部，也不要让项目和 mathlib 分属不同权限区域（沙箱/只读盘），否则 Lake 会因为无法写 `.olean.hash` 而报 `permission denied`。

---

## 3. 一次性搭建

### 3-A. 全新机器（有网络）

```powershell
# 1) 装 Elan（Lean 版本管理器）。装完重开终端。
winget install Lean.Elan
elan --version

# 2) 建根目录
$root = "E:\lean"
New-Item -ItemType Directory -Force "$root\projects" | Out-Null

# 3) 取 Mathlib（只取历史，不做 blob 过滤，速度快很多）
cd $root
git clone --depth 1 https://github.com/leanprover-community/mathlib4.git
cd mathlib4

# 4) 让 Elan 按 Mathlib 自带工具链下载 Lean
#    （mathlib4\lean-toolchain 里写着需要的版本，elan 会自动下载）
lake --version

# 5) 拉预编译缓存（数 GB；这是唯一一次大下载）
lake exe cache get

# 6) 自检：应当秒过（缓存命中，不重新编译）
lake build Mathlib 2>&1 | Select-Object -Last 3
```

> 第 6 步如果开始疯狂编译，说明缓存没命中：检查 `lake-manifest.json` 里的 `mathlib` rev 是否是**官方 tag**。`--depth 1` 拿的是默认分支 head，可能领先于已发布的缓存。

**更稳的做法**（推荐，慢一点但缓存必命中）：

```powershell
git clone https://github.com/leanprover-community/mathlib4.git
cd mathlib4
git checkout v4.35.0-rc4        # 换成一个确实已发布缓存的 tag
lake exe cache get
lake build Mathlib
```

### 3-B. 复用已有 Mathlib（本机现状，零下载）

本机已有：

```
E:\Coding\Deepseek harness\ai4math\lean_experiment\
├── vendor\lean-v4.35.0-rc4\         Lean 4.35.0-rc4 工具链
└── vendor\mathlib4\                 Mathlib 25e572b8，8,628 olean，1.69 GB
```

想把它变成 §2 的标准布局，**复制**（别移动，`lean_experiment` 还有别的用途）：

```powershell
robocopy "E:\Coding\Deepseek harness\ai4math\lean_experiment\vendor\mathlib4" `
         "E:\lean\mathlib4" /E /NFL /NDL /NJH /NJS
```

约 1.7 GB，几分钟。之后 §2 的路径就统一了。

---

## 4. 新建项目

### 4.1 手工四步

```powershell
$p = "E:\lean\projects\myproj"
New-Item -ItemType Directory -Force "$p\.lake\packages" | Out-Null

# (1) 工具链：必须与 mathlib 的 lean-toolchain 逐字一致
Copy-Item "E:\lean\mathlib4\lean-toolchain" "$p\"

# (2) 预置传递依赖：省掉 8 次 git clone（0.35 GB）
robocopy "E:\lean\mathlib4\.lake\packages" "$p\.lake\packages" /E /NFL /NDL /NJH /NJS
```

（3）写 `lakefile.toml`：

```toml
name = "myproj"
defaultTargets = ["Main"]

[[require]]
name = "mathlib"
path = "E:/lean/mathlib4"          # 改成你的实际路径，正斜杠

[[lean_lib]]
name = "Main"
```

（4）写 `Main.lean` 并构建：

```lean
import Mathlib

#check RiemannHypothesis
#check MeasureTheory.integral_add
```

```powershell
$env:LAKE_NO_HOOKS = "1"      # 关键，见 §6.1
cd $p
lake build Main
```

### 4.2 一键脚本（把它存成 `New-LeanProject.ps1`）

```powershell
function New-LeanProject {
    param(
        [Parameter(Mandatory)] [string] $Path,
        [Parameter(Mandatory)] [string] $Mathlib,
        [string] $LeanBin
    )
    $Mathlib = $Mathlib.TrimEnd('\','/')
    New-Item -ItemType Directory -Force "$Path\.lake\packages" | Out-Null

    Copy-Item "$Mathlib\lean-toolchain" "$Path\" -Force
    robocopy "$Mathlib\.lake\packages" "$Path\.lake\packages" /E /NFL /NDL /NJH /NJS | Out-Null

    $mlForToml = $Mathlib.Replace('\','/')
    @"
name = "$(Split-Path $Path -Leaf)"
defaultTargets = ["Main"]

[[require]]
name = "mathlib"
path = "$mlForToml"

[[lean_lib]]
name = "Main"
"@ | Set-Content "$Path\lakefile.toml" -Encoding UTF8

    @'
import Mathlib

#check RiemannHypothesis
#check MeasureTheory.integral_add

example (n : ℕ) : n + 0 = n := by simp
'@ | Set-Content "$Path\Main.lean" -Encoding UTF8

    if ($LeanBin) { $env:PATH = "$LeanBin;$env:PATH" }
    $env:LAKE_NO_HOOKS = "1"

    Push-Location $Path
    try {
        Write-Host "构建中…" -ForegroundColor Cyan
        lake build Main
        if ($LASTEXITCODE -eq 0) { Write-Host "✓ 项目就绪: $Path" -ForegroundColor Green }
        else { Write-Host "✗ 构建失败，见 §6" -ForegroundColor Red }
    } finally { Pop-Location }
}
```

> **PowerShell 5.1 的坑**：`Set-Content -Encoding UTF8` 会写 BOM，Lake 的 TOML 解析器会在第 1 行报 `expected end of input`。上面脚本用 `Set-Content -Encoding UTF8` 在本机实测**可以**（Lake 5 容忍 BOM），但若遇到该报错，改用
> `[System.IO.File]::WriteAllText($path, $text, (New-Object System.Text.UTF8Encoding($false)))`。

---

## 5. 日常使用

### 5.1 命令行

```powershell
$env:PATH = "E:\lean\mathlib4\.lake\packages\..\..\..\..\vendor\lean-v4.35.0-rc4\bin;$env:PATH"  # 若用 Elan 可省
$env:LAKE_NO_HOOKS = "1"

cd E:\lean\projects\myproj
lake build                      # 构建默认目标
lake build Main                 # 只构建 Main
lake env lean Main.lean         # 直接让 lean 检查单文件（不进 .olean）
lake env lean --run Main.lean   # 运行（要求文件里有 main）
```

### 5.2 常用 Lean 自检片段

```lean
#check RiemannHypothesis          -- 确认 Mathlib 已加载
#print axioms RiemannHypothesis   -- 看公理依赖
#eval 2 + 2
set_option pp.all true in #check Nat.add_comm   -- 展开全部隐式参数
```

### 5.3 VS Code

1. 安装扩展 `leanprover.lean4`（本机已装 `0.0.242`）。
2. **用 VS Code 直接打开项目根目录**（含 `lakefile.toml` 的那层），不要只打开单个 `.lean` 文件。
3. 首次打开会提示下载 Elan——允许。之后右下角应显示 `Lean 4` 就绪。
4. `Ctrl+Shift+P` → `Lean 4: Restart Server` 是万能重启键。

> Lean 扩展按**最近的 lakefile** 判定项目。裸 `.lean` 文件（不在任何项目里）只能看到核心库，`import Mathlib` 会失败。**把随手写的文件都放进 `projects\playground\`。**

---

## 6. 故障排查

### 6.1 `permission denied … .cache\mathlib` 或 `failed to fetch cache`

Lake 执行了 Mathlib 的 post-update 钩子（等于 `lake exe cache get`）。

**解决**：`$env:LAKE_NO_HOOKS = "1"`。
Mathlib 已编译时完全不需要这个钩子。

### 6.2 `plausible: fetching revision … SSL certificate problem`

根项目缺传递依赖，Lake 想联网 clone。**解决**：执行 §4.1 第 (2) 步，把 `mathlib4\.lake\packages` 复制进项目。

### 6.3 `error: lakefile.toml:1:0: error: expected end of input`

文件带 UTF-8 BOM。用无 BOM 方式重写（见 §4.2 末尾）。

### 6.4 `permission denied` 指向 `mathlib4\.lake\build\...`

Lake 想更新 mathlib 自己的 `.olean.hash`。**原因**：mathlib 在只读区/沙箱外。**解决**：把 mathlib 与项目放进同一个可写根（§2 的规则）。

### 6.5 `toolchain not updated` / 要求重建 Mathlib

项目 `lean-toolchain` 与 `mathlib4\lean-toolchain` 不一致。**解决**：逐字复制，别手写版本号。

### 6.6 `unknown declaration 'main'`（`lake env lean --run`）

文件里没有 `def main : IO Unit`。这是运行要求，不是编译要求。

### 6.7 `import Mathlib` 卡住很久

首次编译需要生成 `.olean` 索引，正常。若超过 10 分钟且 CPU 满，检查是否在**重新编译 Mathlib**（说明缓存没命中或工具链变了）。

---

## 7. 版本管理三条铁律

1. **一份 Mathlib 锁一个 Lean 版本。** 想换版本 = 换一份 mathlib 检出（不同目录）。
2. **`lean-toolchain` 只复制不手写。** 手写差一个 `-rc2` 就是几小时重建。
3. **`git pull` 有传染性。** 更新 mathlib 之后，所有下游项目都要 `lake build` 重建；共享同一 mathlib 的项目会一起受影响。

如果要同时服务多个版本（例如复现别人的仓库），做法是**多份 mathlib 并列**：

```
E:\lean\
├── mathlib4-4.35\        ← 对应 Lean 4.35
├── mathlib4-4.33\        ← 对应 Lean 4.33（另一个仓库钉的版本）
└── projects\
    ├── p-new\            path → mathlib4-4.35
    └── p-old\            path → mathlib4-4.33
```

---

## 8. 环境自检（换机器/重建后跑一遍）

```powershell
# 1) Lean 版本
lean --version

# 2) Mathlib 已编译？
$ml = "E:\lean\mathlib4"
$o = Get-ChildItem "$ml\.lake\build\lib\lean" -Recurse -Filter '*.olean' -ErrorAction SilentlyContinue
"olean 数: {0}, 大小: {1:N2} GB" -f $o.Count, (($o | Measure-Object Length -Sum).Sum/1GB)
#   健康的完整构建：约 8,600 个文件 / 1.7 GB

# 3) 端到端：新建并构建一个最小项目
New-LeanProject -Path "E:\lean\projects\_smoke" -Mathlib $ml
```

`_smoke` 里 `#check RiemannHypothesis` 打印出 `RiemannHypothesis : Prop` 即通过。

---

## 9. 本机现状快照（2026-11-24）

| 项 | 路径 / 值 |
|---|---|
| Elan | `C:\Users\yichen\.elan\bin`（4.4.0） |
| 已注册工具链 | `lean-4.36.0-local` → junction 到 `E:\Program Files\lean\lean-4.36.0-windows` |
| 另一套 Lean | `E:\Coding\Deepseek harness\ai4math\lean_experiment\vendor\lean-v4.35.0-rc4` |
| Mathlib | `…\lean_experiment\vendor\mathlib4`，commit `25e572b8`，8,628 olean / 1.69 GB |
| Mathlib 缓存 | `…\lean_experiment\.mathlib-cache`，433 MB / 9,014 个 `.ltar` |
| VS Code 扩展 | `leanprover.lean4-0.0.242` |
| 磁盘 | C: 94 GB / D: 97 GB / E: 219 GB 可用 |

**注意 `elan default`**：`settings.toml` 里 `default_toolchain = "stable"`，而 `stable` 未安装，所以 elan 的 shim 每次都会尝试联网下载。在你自己的终端里执行一次

```powershell
elan default lean-4.36.0-local
```

即可消除这个下载行为；在我们这个受沙箱限制的会话里，直接调用各工具链 `bin\` 下的真实二进制更可靠。

---

## 10. 与本课题相关的两个"不可用"提醒

审计目标的两个仓库，**都不能用本机这份 Mathlib**：

| 仓库 | Lean | Mathlib rev |
|---|---|---|
| Euler（`mcoiculescu/EulerBlowupPublic`） | `v4.34.0-rc2` | `85e3a25e…785bc0` |
| NS（`tristanbuckmaster/navier-stokes`） | `v4.33.1` | `0df444a3…55474` |
| 本机 | `v4.35.0-rc4` | `25e572b8…84534` |

要构建它们，按 §7 的做法另建 `mathlib4-4.34` / `mathlib4-4.33`，各自 `cache get`。
