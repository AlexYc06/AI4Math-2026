# 技术笔记 A：Euler 证明的数学内核（Craik–Criminale 级联）

> 对应论文：`sources/euler_cc.txt`（Alpöge–Buckmaster–Coiculescu，56 页）
> 定位：为审计表提供"我确认理解了"的基线。凡本笔记与论文表述不一致处，均显式标出。
> 数值核对脚本：`code/cc_amplification.py`

---

## 1. 构造的总图景

从静止剪切流出发，逐级叠加**局部化**的 Craik–Criminale 波。每一级包含四个动作：

```
(1) 前一级的剪切放大新波        → 增益 ≈ exp(ε^{-1/2})
(2) 新波在放大过程中转向        → 为下一级提供 ε_+ < ε 的框架
(3) 用"端点问题"选初值消除误差   → 一阶位移在步末归零
(4) 频率截断、记账              → 残差成为下一级的"父残差"
```

关键点：**速度有界而涡量发散**，且增长区间总长有限。这与自相似爆破（速率 $(T-t)^{-\alpha}$）是完全不同的机制——Euler 这一侧**不是**自相似构造。

---

## 2. 精确波：Craik–Criminale 方程

设 $D(t)$ 光滑、$\operatorname{tr}D=0$、$D'+D^2$ 对称。则 $U(t,x)=D(t)x$ 是 Euler 方程的精确解，压力 $p_D=-\tfrac12 x\cdot(D'+D^2)x$。

在其上叠加

$$w(t,x)=a(t)F(k(t)\cdot x),\qquad a\cdot k=0,$$

其中 $F$ 是光滑奇 $1$-周期剖面。$\operatorname{rank}(a\otimes k)=1$ 使 $(w\cdot\nabla)w\equiv0$，于是 $u=Dx+w$ 精确求解当且仅当

$$\boxed{\;k'=-D^{\mathsf T}k,\qquad a'=-Da+p_wk,\qquad p_w=\frac{2\,k\cdot Da}{|k|^2},\qquad k\cdot a=0\;}\tag{2.1}$$

压力为 $p=p_D-p_wP(k\cdot x)$，$P'=F$。归一化 $F'(0)=1$ 给出

$$\nabla w(t,0)=a\otimes k.$$

> **可读性要点 1**：式 (2.1) 的第三个式子不是"额外的守恒律"，而是**保持 $a\cdot k=0$ 的补偿项**。验证：$\frac{d}{dt}(a\cdot k)=a'\cdot k+a\cdot k'=(-Da+p_wk)\cdot k+a\cdot(-D^{\mathrm T}k)=-2a\cdot Dk+2a\cdot Dk+p_w|k|^2$，其中 $-Da\cdot k=-a\cdot D^{\mathrm T}k$，两项相消，故 $p_w$ 的存在使约束自动保持。数值上 $|a\cdot k|$ 始终 $\sim10^{-19}$（见 §5 表）。

---

## 3. 放大机制：为什么是 $e^{\varepsilon^{-1/2}}$

### 3.1 框架与三个参数

设前一级波的波矢 $k_p$、振幅 $a_p$ 非零，令

$$E_1=\frac{k_p}{|k_p|},\quad E_2=\frac{a_p}{|a_p|},\quad E_3=E_1\times E_2,\quad \sigma=|a_p|\,|k_p|.$$

前一级在原点贡献梯度 $a_p\otimes k_p=\sigma E_2\otimes E_1$。新波看到的梯度为

$$D=B+\sigma E_2\otimes E_1,$$

其中 $B$ 是更早的背景。在动标架中取 $B$ 只有两个非零分量、且为常数：

$$B_{12}=E_1\cdot BE_2=\nu>0,\qquad B_{32}=E_3\cdot BE_2=\eta>0,\qquad \varepsilon:=\eta/\nu\ll1.$$

新波在 $t=0$ 启动时取 $k=\lambda E_3$。

### 3.2 局部线性化（我独立重推，与论文一致）

前一级波在 $D=B$ 下演化，其归一化标架满足（论文 §1.1 给出）

$$E_1'=-\nu E_2,\qquad E_2'=\nu E_1-\eta E_3,\qquad E_3'=\eta E_2. \tag{3.1}$$

设 $\alpha=\sum_i a_iE_i$。一方面 $\alpha'=\sum_i(a_i'E_i+a_iE_i')$，用 (3.1) 得标架分量

$$(\alpha')_1=a_1'+\nu a_2,\qquad (\alpha')_2=a_2'-\nu a_1+\eta a_3,\qquad (\alpha')_3=a_3'+\eta a_2.$$

另一方面由 (2.1)，$\alpha'=-D\alpha+p_wk$，而 $D$ 在标架内的分量为 $D_{12}=\nu,\ D_{21}=\sigma,\ D_{32}=\eta$，故

$$(D\alpha)_1=\nu a_2,\qquad (D\alpha)_2=\sigma a_1,\qquad (D\alpha)_3=\eta a_2.$$

比较得

$$\boxed{\;a_1'=-2\nu a_2+p_wk_1,\qquad a_2'=-(\sigma-\nu)a_1-\eta a_3+p_wk_2,\qquad a_3'=-2\eta a_2+p_wk_3\;}\tag{3.2}$$

在 $t=0$ 附近 $k_1,k_2=O(t^2)$，$a_3=O(t)$、$\eta\ll\nu$，故主导系统为

$$\dot a_1=-2\nu a_2,\qquad \dot a_2=-(\sigma-\nu)a_1. \tag{3.3}$$

> **可读性要点 2**：论文第 3 页写的是 $\dot a_1=-2\nu a_2$，但 $\nu a_2$ 来自 $B$、另 $\nu a_2$ 来自**标架的转动**。读者若只看 (2.1) 会算出 $\dot a_1=-\nu a_2$ 并怀疑系数 2 有误。这里必须把两个来源分开，否则会卡住。（这是本笔记最有实用价值的一条。）
>
> **可读性要点 3**：论文没有写出 $a_3$ 的方程。它形式上与 $a_1$ 同构（$\nu\to\eta$），在 $\eta\ll\nu$ 下是快衰减项，故被略去；但写出来可以避免"$a$ 只有两个分量"的误解。

(3.3) 的特征值是 $\pm\sqrt{2\nu(\sigma-\nu)}$，$\sigma>\nu$ 时有指数增长，增长方向为

$$a\ \propto\ E_2-\sqrt{\tfrac{2\nu}{\sigma-\nu}}\,E_1,$$

$\sigma\gg\nu$ 时 $\approx E_2-\sqrt{2\nu/\sigma}\,E_1$（与论文一致；论文该处的根号在 PDF 文本提取中丢失）。

### 3.3 转向与压力因子

设 $\phi$ 为 $k$ 从 $E_3$ 转向 $E_1$ 的角度，$\tan\phi=(k\cdot E_1)/(k\cdot E_3)$。随标架转向，压力项对新波驱动系数的贡献被乘以

$$\cos^2\phi\,\bigl(1-\varepsilon\tan\phi\bigr) \tag{Lemma 2.3}$$

该因子在 $\tan\phi=1/\varepsilon$ 处**变号**。强剪切极限下，振幅 $|a|$ 的峰值出现在变号**之后**；Proposition 2.8 断言：对该初值方向的扰动波，在指定区间上的增益至少是 $\exp(\varepsilon^{-1/2})$ 的一个固定倍数。

> **为什么这个结构必须如此**：若峰值出现在变号之前，增益就只由线性率 $\sqrt{2\nu\sigma}$ 与到变号的时间决定，无法得到 $e^{\varepsilon^{-1/2}}$ 这种**由 $\varepsilon$ 单独控制**的量级。峰值落在变号之后，使指数中的小参数从 $\varepsilon$ 变成 $\varepsilon^{-1/2}$——这正是级联能在有限时间内收敛的算术根源（见 §6）。

### 3.4 后继框架

新波自己也产生剪切 $\sigma_+E_{2,+}\otimes E_{1,+}$，其中

$$E_{1,+}=\frac{k}{|k|},\quad E_{2,+}=\frac{a}{|a|},\quad \sigma_+=|a|\,|k|,$$

并把更早的 $D$ 在新框架里表示为 $\nu_+=E_{1,+}\cdot DE_{2,+}$、$\eta_+=E_{3,+}\cdot DE_{2,+}$。**必须让 $\varepsilon_+=\eta_+/\nu_+<\varepsilon$**，否则下一级的增益不够大、误差压不住。Lemma 2.7 说：晚时 $\nu_+$ 接近 $\nu$、$\eta_+/\nu_+$ 与 $\cos\phi$ 可比。构造在比值达到预设 $\varepsilon_+$ 时激活下一级。

> 级联能自我维持，靠的不是"放大"，而是"放大 + 转向 + 参数单调下降"这一组三件套。只读"增益 $e^{\varepsilon^{-1/2}}$"会完全错过这一点。

---

## 4. 三个补充机制

### 4.1 端点问题（消除误差）

设 $u$ 在 $[0,T]$ 上解 Euler，流为 $X$。对散度为零的修正 $b$，一阶位移 $\xi$ 满足

$$\partial_t\xi=\nabla u(t,X(t,a))\xi+b(t,X(t,a)),\qquad \xi(0,a)=0.$$

**关键选择**：不规定 $b(0)$，而规定**终点条件** $\xi(T,a)=0$。这等价于求 $b$ 使修正后的流把每个粒子送回原终点（一阶意义）。设 $H=(D_x^2p)\circ X$，则

$$\xi_{tt}+H\xi+(\nabla q)\circ X=f\circ X,\qquad \xi(0)=\xi(T)=0,\qquad \operatorname{div}_x(\xi\circ X^{-1})=0. \tag{4.1}$$

这是 Arnold 意义下沿测地线的 **Jacobi 方程**。乘以 $-\xi$ 分部积分：

$$Q(\xi):=\int_0^T\!\!\int\bigl(|\xi_t|^2-\xi\cdot H\xi\bigr)\,da\,dt=-\int_0^T\!\!\int(f\circ X)\cdot\xi\,da\,dt. \tag{4.2}$$

若 $H\le\mathrm{Id}$ 且 $T\le1$，则由 $|\xi(t,a)|^2\le(T-t)\int_t^T|\xi_\tau|^2d\tau$ 得

$$Q(\xi)\ \ge\ \Bigl(1-\tfrac{T^2}{2}\Bigr)\|\xi_t\|^2_{L^2_{t,a}}\ \ge\ \tfrac12\|\xi_t\|^2_{L^2_{t,a}}. \tag{4.3}$$

于是 $f=0$ 时 $Q=0$ 迫使 $\xi_t=0$，再 $\xi(0)=0$ 得 $\xi\equiv0$，故端点映射 $b(0)\mapsto\xi(T)$ 单射；Theorem 4.2 进一步给 Hölder 逆（App A）。

> **可读性要点 4**：$H\le\mathrm{Id}$ 是整篇论文里最"脆"的假设——它把"压力 Hessian 不要太大"变成一个**可加的预算**，由 §7 把各级贡献加起来验证。读懂 §3.2 的 $F_h$ 与 §7 的求和，就理解了这篇论文的骨架。

### 4.2 剖面 $F_h$：为什么不能用 $\sin$

若 $F=\sin(2\pi s)$，则 $F'(1/2)/F'(0)=-1$，压力 Hessian 的正部太大。构造（Lemma 3.1）改为：奇、$1$-周期、零均值原函数，满足

$$F_h'(0)=1,\qquad -C_h\le F_h'(s)\le1,$$

即"原点斜率仍为 1（保住放大），但不允许深度为负的斜率（压住 Hessian 正部）"。于是对 $p_w>0$ 的区间，

$$\bigl[p_w|k|^2\bigl(-F_h'(k\cdot x)\bigr)\bigr]_+\ \le\ C_h\,p_w|k|^2,$$

而 $h$ 取频率的负幂，使 $C_hp_w|k|^2$ 随级数迅速变小。**代价**：$h\to0$ 时波变成薄剪切层，速度振幅只有 $O(h|a|)$，但原点梯度仍是 $a\otimes k$。

> 这个"变薄以换取 Hessian 可控"的取舍，是全文最漂亮的一处工程。它解释了一个否则很神秘的事实：为什么爆破是"原点涡量发散而速度有界"——梯度集中、速度不集中。

### 4.3 层级展开

加入的速度写成有限展开

$$u_{\text{add}}=\sum_{p=1}^{P}Z_p+C_{P+1},\qquad Z_p=V_p+C_p+B_p,$$

$V_p$ 是垂直于 $\kappa=\nabla\theta$ 的剖面、$C_p$ 是散度修正、$B_p$ 是相位平均。**级别 $p$ 的界是波幅乘以 $\lambda^{-2(p-1)/3}$**。逐级求解：

- 平均部分：$D_tB_2+(\nabla U)B_2+\nabla q=-\langle H_2\rangle_s-R_U$，$\operatorname{div}B_2=0$；
- 振荡部分：$D_tV_2+(\nabla U)V_2+\kappa\partial_s\pi_2=-(H_2-\langle H_2\rangle_s)-(B_2\cdot\kappa)\partial_s(\chi A_1)$，$\kappa\cdot V_2=0$，$\langle V_2\rangle_s=0$。

截断到深度 $P$ 后余项 $\le\lambda^{-2P/3}$（Theorem 5.6）。

---

## 5. 数值核对（本步唯一的计算产出）

脚本 `code/cc_amplification.py` 直接对 (2.1) 积分，标架按 (3.1) 演化，$B(t)=\nu E_1\otimes E_2+\eta E_3\otimes E_2$（即在动标架内分量恒定），$D=B+\sigma E_2\otimes E_1$，初值 $k=\lambda E_3$、$a\propto E_2-\sqrt{2\nu/(\sigma-\nu)}E_1$。取 $\nu=1$、$\lambda=1$、$t\le10^{-3}$、RK45（rtol $10^{-11}$）。

| $\varepsilon$ | $\sigma$ | $\sqrt{2\nu(\sigma-\nu)}$ | 实测 $\frac{d}{dt}\log|a|$ | 相对误差 | $\tan\phi\,/\,[(\sigma+\nu)\eta t^2]$ | $\max|a\cdot k|$ |
|---|---|---|---|---|---|---|
| 0.2 | 10 | 4.2426 | 4.2426 | 1.9e-8 | 1.0000 | 1.9e-19 |
| 0.2 | 100 | 14.0712 | 14.0712 | 7.0e-9 | 1.0000 | 3.0e-19 |
| 0.2 | 1000 | 44.6990 | 44.6990 | 2.2e-9 | 1.0000 | 2.4e-19 |
| 0.1 | 10 | 4.2426 | 4.2426 | 4.9e-9 | 1.0000 | 5.4e-20 |
| 0.1 | 100 | 14.0712 | 14.0712 | 1.8e-9 | 1.0000 | 1.1e-19 |
| 0.1 | 1000 | 44.6990 | 44.6990 | 5.6e-10 | 1.0000 | 8.1e-20 |
| 0.05 | 10 | 4.2426 | 4.2426 | 1.2e-9 | 1.0000 | 6.8e-20 |
| 0.05 | 100 | 14.0712 | 14.0712 | 4.4e-10 | 1.0000 | 4.1e-20 |
| 0.05 | 1000 | 44.6990 | 44.6990 | 1.4e-10 | 1.0000 | 4.7e-20 |

**结论（可写入审计表的 C 级证据）**：

1. 论文 §1.1 的**增长率 $\sqrt{2\nu(\sigma-\nu)}$ 得到独立数值确认**（相对误差 $\le2\times10^{-8}$，纯离散化误差）。
2. 论文的**转向律 $\tan\phi\sim(\sigma+\nu)\eta t^2$** 在动标架意义下系数为 1（打印精度内），且**与 $\varepsilon$ 无关**；这比论文的 "grows like" 更强，是一个可记录的小加强。
3. $a\cdot k=0$ 在整个积分中保持到 $10^{-19}$，确认 (2.1) 中 $p_w$ 项的补偿作用。
4. **未核对**：Proposition 2.8 的增益 $e^{\varepsilon^{-1/2}}$。这需要 §2 的完整渐近（尤其是峰值时刻与 $\varepsilon_+$ 的匹配），留待 W3。

> 一个反面教训：第一次实现时我用固定坐标的第 1、3 分量算 $\phi$，得到与 $(\sigma+\nu)\eta t^2$ 的比值 $0.86/0.99/0.998$，看起来"差不多对"。改成动标架分量 $(k\cdot E_1)/(k\cdot E_3)$ 后比值变成精确的 1。**"差不多对"往往是定义用错了**。这正是"可读化"必须做到位的理由。

---

## 6. 参数阶梯：为什么级联能收敛

论文 §1.5 固定

$$K(s)=320b(s+1),\quad \lambda_j=\lambda_{j-1}^{K_j},\quad \Lambda_j=\lambda_j^{5},\quad L_j=4\log\lambda_{j+1},\quad \varepsilon_{j-1}=L_j^{-2},$$

并取 $q_{j+1}=\max\{1\le s\le q_j+1:\ B(s)\le\lambda_{j-1}\}$，其中 $B$ 满足

$$\log B(s)\ \ge\ 4K(s+1)^3. \tag{1.13}$$

三步误差（展开余项 $\lambda^{-2P/3}$、频率截断、时间截断）都要小于下一级频率的固定负幂。增益是

$$\exp(\varepsilon^{-1/2})=\exp(L_j)=\lambda_{j+1}^{4}=\lambda_j^{4K_j},$$

即"增益 = 下一级频率的四次方"量级。

> **可读性要点 5**：$\varepsilon=L^{-2}$ 而非 $L^{-1}$，是为了让 $\exp(\varepsilon^{-1/2})=\exp(L)$ 与 $\lambda_{j+1}^4$ 精确对齐。这是"用参数选择把指数对齐"的典范；不理解这一行，§7 的求和就是黑箱。而 (1.13) 的 $4K^3$ 是为了让 $q_j$（光滑性阶数）**趋于无穷但足够慢**，以抵消 §7 中损失的 $\log$ 幂次。

---

## 7. 留给审计的问题

| 编号 | 问题 | 对应缺口 |
|---|---|---|
| Q1 | `Paper.Statement.*` 的 42 个节点是否与 TeX 的编号结果一一对应？抽样 10 个 | G6 |
| Q2 | 每个 `Paper.Proof.R_of` 的"frontier = TeX 引用集合"是否成立？`ledger-decisions.md` 的 D1–D29 是否覆盖了全部偏离？ | G6 |
| Q3 | Corollary 8.3 用 Prop 8.2 的涡量下界替代 BKM 判据，这一步是否严格？ | G7 |
| Q4 | §1.6 "Provenance" 与 §1.7 "AI statement" 所述的重写过程，是否影响了定理陈述（而非仅影响可读性）？ | G8 |

Q1 与 Q2 都不需要 Lean，只需要读 `formalization/lean/TorusEuler/` 下的声明与 `spine.json`。
