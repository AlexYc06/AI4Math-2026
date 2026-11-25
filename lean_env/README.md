# lean_env —— 最小 Lean 工程（验证工具链可用）

本目录只为验证 `lean-4.36.0-local` 工具链能在本机离线工作。

## 配置

- `lean-toolchain` = `lean-4.36.0-local`（指向 `E:\Program Files\lean\lean-4.36.0-windows` 的 junction）
- `lakefile.toml`：单库目标 `Main`
- `Main.lean`：hello world

## 验证结果（2026-11-23）

```
Lean  (version 4.36.0, x86_64-w64-windows-gnu, commit 611c117bfaf7b7ae1cfcf246ce6fba31e8f509e9, Release)
Lake  version 5.0.0-src+611c117 (Lean version 4.36.0)

lake build Main
  ✔ [2/4] Built Main (687ms)
  Build completed successfully (4 jobs)
  → .lake/build/lib/Main.olean  (16,976 bytes)
```

**无需联网。** Lake 明确报告 "toolchain not updated; already up-to-date"，即它接受了本地的 `lean-4.36.0-local`。

## 怎么用（重要）

**不要**走 elan 的 shim（`C:\Users\yichen\.elan\bin\lean.exe`）。在本会话里它会触发下载并失败：

```
error: error during download
caused by: [35] SSL connect error (schannel: AcquireCredentialsHandle failed: SEC_E_NO_CREDENTIALS)
```

这是本会话 shell 的 TLS 限制（与之前 `curl.exe` 失败同因），不是 elan 或工具链的问题。

**改用真实二进制目录：**

```powershell
$env:PATH = "E:\Program Files\lean\lean-4.36.0-windows\bin;$env:PATH"
lean --version
lake build
```

或者在你自己的终端里（不受此限）执行一次：

```powershell
elan default lean-4.36.0-local
```

之后 shim 就会指向本地工具链，不再尝试下载 `stable`。

## 工具链里还带了什么

`bin/` 下除 `lean`、`lake` 外还有：

- `con-leche.exe`、`con-ron.exe` —— 独立内核检查器（RH 验证用过的那两个）
- `lean4lean.exe` —— 独立内核的形式化
- `cadical.exe` —— SAT 求解器
- `clang.exe`、`ld.lld.exe` —— C 编译器与链接器（`@[extern]`/FFI 需要）

完整度足够，可用于导出/检查 `.olean` 与 proof export。

## 尚缺：Mathlib

本机未找到任何 `mathlib` 目录。Euler / NS 两个仓库都依赖 Mathlib（且钉在不同 revision：Euler 用 Lean v4.34.0-rc2、NS 用 v4.33.1），因此：

1. 需要 `lake exe cache get` 下载数 GB 预编译缓存；
2. 这一步需要 HTTPS，**在本会话 shell 里做不到**（同一 TLS 限制）；
3. 请在你自己的终端或 VS Code 里先完成 `cache get`，之后本会话就能用真实二进制离线构建。

两个仓库的 Lean 版本都与 `lean-4.36.0-local` 不同，所以即便拿到 Mathlib，也需要 `lean-toolchain` 分别指向 v4.34.0-rc2 / v4.33.1，由 elan 另外下载。
