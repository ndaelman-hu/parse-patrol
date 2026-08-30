"""Draft failure-mode figure for the parse-patrol paper (matched 30-task set)."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

arms = ["NONE", "BARE", "DOCS", "FULL", "COMPLEXITY"]
wp = [0, 21, 19, 21, 2]      # wrong-parser
se = [0, 11, 11, 11, 1]      # silent-empty
fs = [12, 0, 1, 2, 1]        # parser-from-scratch
gu = [14, 12, 12, 11, 11]    # gave-up (reasoning)
succ = [53, 60, 60, 63, 63]  # success %

plt.rcParams.update({"font.size": 9, "font.family": "serif",
                     "axes.spines.top": False, "axes.spines.right": False})

fig, ax = plt.subplots(figsize=(6.4, 3.0))
x = np.arange(len(arms))
c_wp, c_se, c_fs, c_gu = "#d1495b", "#edae49", "#66a3c2", "#9aa0a6"
ax.bar(x, wp, color=c_wp, label="wrong-parser (interface)")
ax.bar(x, se, bottom=wp, color=c_se, label="silent-empty (interface)")
base2 = np.array(wp) + np.array(se)
ax.bar(x, fs, bottom=base2, color=c_fs, label="from-scratch")
base3 = base2 + np.array(fs)
ax.bar(x, gu, bottom=base3, color=c_gu, label="gave-up (reasoning)")
tops = base3 + np.array(gu)
for xi, t, s in zip(x, tops, succ):
    ax.text(xi, t + 0.6, f"{s}\\%" if False else f"{s}%", ha="center", va="bottom",
            fontsize=8, fontweight="bold")
ax.set_xticks(x); ax.set_xticklabels(arms, fontsize=8)
ax.set_ylabel("runs exhibiting mode (of 30)")
ax.set_ylim(0, max(tops) + 5)
# legend outside, in reserved right-hand whitespace
ax.legend(fontsize=7.5, loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False)
fig.subplots_adjust(left=0.10, right=0.70, top=0.97, bottom=0.11)
fig.savefig("fig_failuremodes.pdf")
fig.savefig("fig_failuremodes.png", dpi=160)
print("wrote fig_failuremodes.{pdf,png}")
