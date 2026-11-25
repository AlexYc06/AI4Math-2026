# G6 抽样 01：`proposition_2_8` 的命题保真度

> 对象：论文 Prop 2.8（`euler_cc.txt` L1093–1104）vs Lean `Paper.Statement.proposition_2_8`（`S2_Statements.lean` L329–346）
> 判定等级：**R**（人读比对）
> 结论：**忠实，且在一处更强**（常数被显式化）。未发现 (b) 假设削弱或 (d) 语义不同。

---

## 1. 两边的原文

### 1.1 论文（L1093–1104）

> **Proposition 2.8.** Assume (2.7), let $a$ be the amplitude vector of Lemma 2.6, with the couplings of Lemma 2.7, and suppose that $0<\varepsilon_+\le\varepsilon/32$ and $T\ge2(\varepsilon\varepsilon_+)^{-1/2}$. Then the interval $\tau_m\le\tau\le2(\varepsilon\varepsilon_+)^{-1/2}$, where $\tau_m\ge2/\varepsilon$ is the zero of $Y$ (Lemma 2.5), contains a crossing. At every crossing in this interval the strength $\sigma_+=\|a(\tau)\|\,\|k(\tau)\|$ satisfies
> $$C^{-1}(\varepsilon\varepsilon_+)^{-1/2}\ \le\ \frac{\sigma_+}{\lambda\max_{[0,T]}|a|}\ \le\ C(\varepsilon\varepsilon_+)^{-1/2}.\tag{2.23}$$
> Moreover
> $$|a(\tau)|\le \exp\!\bigl(3-\varepsilon^{-1/2}\bigr)\max_{[0,T]}|a|\qquad(0\le\tau\le1).\tag{2.24}$$

### 1.2 Lean（L329–346，逐子句）

```lean
def proposition_2_8 : Prop :=
  ∃ N : ℕ, ∀ {C₀ : ℕ}, N ≤ C₀ →
  ∀ {I : Set ℝ} {t₀ T lam εplus : ℝ} (w : PhysicalAmplification I t₀) {k a : ℝ → Vec3},
    2 ≤ T → MapsTo w.clock (Icc 0 T) I → FiniteSmallness w T C₀ → NewWaveVector w lam k →
    AmplitudeVector w k a → a t₀ = (-w.shear⁻¹) • w.basis t₀ 0 + w.basis t₀ 1 →
    0 < εplus → εplus ≤ w.ratio / 32 → 2 / Real.sqrt (w.ratio * εplus) ≤ T →
    let ε := w.ratio
    let H := 2 / Real.sqrt (ε * εplus)
    let ratioPlus := fun τ => w.physicalEta k a (w.clock τ) / w.physicalNu k a (w.clock τ)
    let σplus := fun τ => ‖a (w.clock τ)‖ * ‖k (w.clock τ)‖
    ∃ τm : ℝ, (∀ Y : ℝ → ℝ, ReferenceSlope ε Y → ∀ τ ∈ Ici (0:ℝ), Y τ = 0 ↔ τ = τm) ∧
      2 / ε ≤ τm ∧
      (∃ τ ∈ Icc τm H, ratioPlus τ = εplus) ∧
      ∃ peak : ℝ, IsGreatest ((fun τ => ‖a (w.clock τ)‖) '' Icc 0 T) peak ∧
        (∀ τ ∈ Icc τm H, ratioPlus τ = εplus →
          Real.exp (-1) / 4 * (Real.sqrt (ε * εplus))⁻¹ ≤ σplus τ / (lam * peak) ∧
          σplus τ / (lam * peak) ≤ 18 * Real.exp 3 * (Real.sqrt (ε * εplus))⁻¹) ∧
        (∀ τ ∈ Icc (0:ℝ) 1, ‖a (w.clock τ)‖ ≤ Real.exp (3 - (Real.sqrt ε)⁻¹) * peak)
```

---

## 2. 逐条对照

| # | 论文 | Lean | 判定 |
|---|---|---|---|
| 1 | 假设 (2.7)（小性条件） | `FiniteSmallness w T C₀`，且 `∃ N, ∀ C₀ ≥ N` | ✅ **忠实，且阈值显式化**：论文的 (2.7) 是"对某常数充分小"，Lean 把它写成"存在 $N$，对所有 $C_0\ge N$" |
| 2 | $a$ 是 Lemma 2.6 的振幅向量（耦合取 Lemma 2.7） | `AmplitudeVector w k a` + `a t₀ = (-w.shear⁻¹) • basis t₀ 0 + basis t₀ 1` | ✅ 见 §3 |
| 3 | $0<\varepsilon_+\le\varepsilon/32$ | `0 < εplus` 与 `εplus ≤ w.ratio / 32` | ✅ 逐字 |
| 4 | $T\ge2(\varepsilon\varepsilon_+)^{-1/2}$ | `2 / Real.sqrt (w.ratio * εplus) ≤ T` | ✅ 逐字（注意 $2/\sqrt{\cdot}$ = $2(\varepsilon\varepsilon_+)^{-1/2}$） |
| 5 | $\tau_m\ge2/\varepsilon$ 是 $Y$ 的零点 | `∀ Y, ReferenceSlope ε Y → ∀ τ ≥ 0, Y τ = 0 ↔ τ = τm` 且 `2/ε ≤ τm` | ✅ **更强**：把"零点"写成**双条件**（存在性与唯一性一并断言） |
| 6 | 区间 $\tau_m\le\tau\le2(\varepsilon\varepsilon_+)^{-1/2}$ 含一个 crossing | `∃ τ ∈ Icc τm H, ratioPlus τ = εplus`，其中 `H = 2/√(ε*εplus)` | ✅ 逐字；`ratioPlus = η₊/ν₊`，"crossing"即 `ratioPlus = εplus` |
| 7 | 在每个 crossing 处 (2.23) 成立 | `∀ τ ∈ Icc τm H, ratioPlus τ = εplus → 下界 ∧ 上界` | ✅ 逐字 |
| 8 | (2.23) 的常数 $C$ 未指明 | `e⁻¹/4`（下界）与 `18e³`（上界） | ✅ **更强：常数被显式化** |
| 9 | (2.24) 对 $0\le\tau\le1$ | `∀ τ ∈ Icc 0 1, ‖a (w.clock τ)‖ ≤ exp(3 − (√ε)⁻¹) * peak` | ✅ 逐字 |
| 10 | —— | 额外假设 `2 ≤ T` | ⚠️ **多出的小假设**，见 §4 |

**差异类型统计**：(a) 记法 3 处；(b) 假设加强 1 处（`2 ≤ T`）；(c) 结论加强 2 处（常数显式、零点唯一性并入）；(d) 语义不同 **0 处**。

---

## 3. 那个看起来像差异、其实不是的地方

Lean 的假设是

$$a(t_0)=-\text{shear}^{-1}\cdot E_1+E_2 .$$

我 W01 独立推出的增长特征向量是 $E_2-\sqrt{2\nu/(\sigma-\nu)}\,E_1$，**带平方根**，看起来对不上。

查 `S2_Vocabulary.lean` L28 的定义：

> `w.rate = r = √(2νσ)`，**`w.shear = S = σ/r`**，`w.ratio = ε = η/ν`

于是

$$\text{shear}^{-1}=\frac{r}{\sigma}=\frac{\sqrt{2\nu\sigma}}{\sigma}=\sqrt{\frac{2\nu}{\sigma}}.$$

所以 Lean 的初值是 $E_2-\sqrt{2\nu/\sigma}\,E_1$——**正是论文 L153–155 写的"the growing direction to leading order for $\sigma\gg\nu$"**。

> 这是一次**假警报**，但值得记录：论文用领先阶方向，我 W01 的数值脚本用精确特征向量。两者在 $\sigma\gg\nu$ 时一致，我的数值（$\sigma=10..1000$、$\nu=1$）因此仍匹配 $\sqrt{2\nu(\sigma-\nu)}$ 到 $10^{-8}$。**如果不查 `shear` 的定义，这里会被误判为 (d) 类语义差异。**

---

## 4. 唯一的真差异：`2 ≤ T`

论文只在 (2.24) 里用到 $\tau\le1$，没有假设 $T\ge2$。Lean 显式加了 `2 ≤ T`。

**它是否冗余？** 由第 4 条假设 $T\ge2(\varepsilon\varepsilon_+)^{-1/2}$ 与 $\varepsilon_+\le\varepsilon/32$：

$$(\varepsilon\varepsilon_+)^{-1/2}\ \ge\ \Bigl(\varepsilon\cdot\frac{\varepsilon}{32}\Bigr)^{-1/2}=\frac{4\sqrt2}{\varepsilon}.$$

若 $\varepsilon\le 2\sqrt2$（小性条件 (2.7) 下必然成立），则 $T\ge 2\cdot\frac{4\sqrt2}{\varepsilon}\ge 2$。**所以 `2 ≤ T` 是冗余的。**

**但冗余假设不影响正确性**：它使定理的适用范围略微缩小（对 $\varepsilon>2\sqrt2$ 的情形不适用），而那种情形本来就在 `FiniteSmallness` 之外。**判定：无害。**

> 一个可做的微改进（若将来提 PR）：从 `proposition_2_8` 的前提里去掉 `2 ≤ T`，看 `VerifySpine` 是否仍通过。这能顺便检验 `FiniteSmallness` 是否真的蕴含 $\varepsilon$ 小。

---

## 5. 对 G6 的意义

**这是 42 个节点里的第 1 个抽样。** 结论：

1. Lean 的命题**不是**论文命题的弱化版；两处反而更强（常数显式、零点唯一性）。
2. "看起来像差异"的一处（`shear⁻¹`）查定义后消失。
3. 唯一真差异（`2 ≤ T`）是无害的冗余。

**如果剩下 9 个抽样也是这个质量，G6 可以从 R 降到"抽样通过"**——那将是本审计第一个由 R 升级的缺口。

同时得到一个**副产品**：Lean 把 (2.23) 的 $C$ 定为 $18e^3$。这在 §1.5 的参数阶梯里会被用到（`T4_late_values` 的 $\sigma$ 上界也带 $C$）。**论文读者看不到这个数，Lean 读者看得到**——这正是"形式化反而更可读"的一个具体例子。

---

## 6. 下一个抽样

按 `11_引用台账判定全表.md` §4.2 的优先级，下一个是 `proposition_8_2`（`setting` 非空、导出 `curl_lower`，且是 G7/G9 的交汇处）。
