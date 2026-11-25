"""
Craik-Criminale 局部放大机制：论文 §1.1 所断言的两条局部渐近律的数值核对。

核对对象（Alpoge-Buckmaster-Coiculescu, §1.1, eq. (1.4) 附近）：
  (A) 在 t=0 处，被放大的新波满足   a1' = -2*nu*a2,   a2' = -(sigma-nu)*a1
      故增长率应为 mu = sqrt(2*nu*(sigma-nu))    （sigma > nu）。
  (B) 波矢转角的初始规律  tan(phi) ~ (sigma+nu)*eta*t^2 。

模型（论文的 "moving frame" 约化）：
  固定正交标架 E1,E2,E3(t) 满足
      E1' = -nu*E2,  E2' = nu*E1 - eta*E3,  E3' = eta*E2,
  背景梯度取 B(t) = nu*E1⊗E2 + eta*E3⊗E2 （在标架内分量恒定，即论文的
  "take B with just two nonzero entries in this moving frame, both constant"），
  主梯度 D(t) = B(t) + sigma*E2⊗E1，
  然后对 (1.4) 精确积分：
      k' = -D^T k,   a' = -D a + p_w k,   p_w = 2 (k·D a)/|k|^2,   a·k = 0。

注意：本脚本只核对"局部"（t 很小）的两条律，不涉及 Proposition 2.8 的
全局增益 exp(eps^{-1/2})——那需要 §2 的完整渐近分析，不在本步范围内。
"""
import numpy as np
from scipy.integrate import solve_ivp

NU = 1.0


def frame(t, nu, eta, e0):
    """解析标架（该线性系统的精确解的结构用 RK 太浪费，这里仍用 RK 保证通用性）。"""
    return None


def rhs(t, y, nu, eta, sigma, lam):
    # y = [E1(3), E2(3), E3(3), k(3), a(3)]
    E1, E2, E3 = y[0:3], y[3:6], y[6:9]
    k, a = y[9:12], y[12:15]

    # 标架方程
    dE1 = -nu * E2
    dE2 = nu * E1 - eta * E3
    dE3 = eta * E2

    # 背景与主梯度
    B = nu * np.outer(E1, E2) + eta * np.outer(E3, E2)
    D = B + sigma * np.outer(E2, E1)

    # 波方程 (1.4)
    dk = -D.T @ k
    Da = D @ a
    pw = 2.0 * (k @ Da) / (k @ k)
    da = -Da + pw * k
    return np.concatenate([dE1, dE2, dE3, dk, da])


def run(nu=NU, eta=None, sigma=100.0, lam=1.0, tmax=2e-3, rtol=1e-11, atol=1e-14):
    eps = eta / nu
    E1 = np.array([1.0, 0.0, 0.0])
    E2 = np.array([0.0, 1.0, 0.0])
    E3 = np.array([0.0, 0.0, 1.0])

    # 增长特征向量：a ∝ E2 - sqrt(2 nu/(sigma-nu)) E1  （论文：E2 - sqrt(2 nu/sigma) E1，sigma>>nu）
    c = np.sqrt(2.0 * nu / (sigma - nu))
    a0 = E2 - c * E1
    a0 = a0 / np.linalg.norm(a0)
    k0 = lam * E3
    assert abs(a0 @ k0) < 1e-12

    y0 = np.concatenate([E1, E2, E3, k0, a0])
    sol = solve_ivp(rhs, (0.0, tmax), y0, args=(nu, eta, sigma, lam),
                    rtol=rtol, atol=atol, dense_output=True, max_step=tmax / 200)

    ts = np.linspace(1e-9, tmax, 400)
    Y = sol.sol(ts)

    loga = np.array([np.log(np.linalg.norm(Y[12:15, i])) for i in range(len(ts))])
    # t=0 处的对数导数
    slope0 = (loga[1] - loga[0]) / (ts[1] - ts[0])

    # 论文的 phi 是 k 从 E3 转向 E1 的角度：tan(phi) = (k.E1)/(k.E3)
    # 必须在"动标架分量"里算，不能直接用固定坐标的第 1、3 个分量。
    tanphi = np.array([
        (Y[9:12, i] @ Y[0:3, i]) / (Y[9:12, i] @ Y[6:9, i]) for i in range(len(ts))
    ])
    # 与 (sigma+nu)*eta*t^2 比较（论文原文："tan phi grows like (sigma+nu) eta t^2"）
    pred = (sigma + nu) * eta * ts ** 2
    ratio = tanphi / pred

    # 守恒检查
    ak = np.array([Y[9:12, i] @ Y[12:15, i] / np.linalg.norm(Y[9:12, i]) for i in range(len(ts))])
    return dict(
        eps=eps,
        mu_pred=np.sqrt(2 * nu * (sigma - nu)),
        mu_meas=slope0,
        tanphi_ratio_median=float(np.median(ratio[5:])),
        tanphi_ratio_first=float(ratio[5]),
        max_abs_ak=float(np.max(np.abs(ak))),
        dk_norm=float(np.linalg.norm(Y[9:12, -1])),
    )


if __name__ == "__main__":
    print(f"{'eps':>8} {'sigma':>7} {'mu_pred':>10} {'mu_meas':>10} {'rel.err':>9} "
          f"{'tanphi/((s+n)eta t^2)':>22} {'max|a.k|':>9}")
    print("-" * 88)
    for eps in [0.2, 0.1, 0.05]:
        for sigma in [10.0, 100.0, 1000.0]:
            r = run(eta=eps * NU, sigma=sigma, tmax=1e-3)
            rel = abs(r["mu_meas"] - r["mu_pred"]) / r["mu_pred"]
            print(f"{eps:>8.3f} {sigma:>7.0f} {r['mu_pred']:>10.4f} {r['mu_meas']:>10.4f} "
                  f"{rel:>9.2e} {r['tanphi_ratio_median']:>22.4f} {r['max_abs_ak']:>9.1e}")
