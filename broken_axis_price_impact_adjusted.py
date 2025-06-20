# I used this script to greate figure 2 in my thesis

import pandas as pd
import matplotlib.pyplot as plt
df = pd.read_excel(
    "Combined relative.xlsx",
    parse_dates=["Date"],
    engine="openpyxl"
)
price_col = next(
    (col for col in df.columns if "r_price.impact_hour".lower() in col.lower()),
    None
)
if price_col is None:
    raise ValueError("No column contains 'r_price.impact_Hour'; check the Excel headers.")
df_pepe = df[df["Pool"] == "PEPE"].sort_values("Date")
df_eth  = df[df["Pool"] == "ETH"].sort_values("Date")
fig, (ax_high, ax_low) = plt.subplots(
    2, 1, sharex=True,
    gridspec_kw={"height_ratios": [4, 1], "hspace": 0},
    figsize=(12, 6)
)
for ax in (ax_high, ax_low):
    ax.plot(df_pepe["Date"], df_pepe[price_col], label="PEPE", color="blue")
    ax.plot(df_eth["Date"],  df_eth[price_col],  label="ETH",  color="red")
ax_high.set_ylim(2, df[price_col].max() * 1.02)
ax_low .set_ylim(-1, 2)
ax_low .set_yticks([-1, 0, 1, 2])
max_top = df[price_col].max()
step = max(int((max_top - 2) / 5), 1)
ax_high.set_yticks(range(2, int(max_top) + 1, step))
ax_high.ticklabel_format(axis="y", style="plain")
ax_high.spines['bottom'].set_visible(False)
ax_low .spines['top'   ].set_visible(False)
ax_high.tick_params(labelbottom=False)
ax_low .tick_params(labeltop=False)
d = .015  
for x in (-d, 1 - d):
    ax_high.plot((x, x + d), (0, -d),
                 transform=ax_high.transAxes,
                 color='k', clip_on=False)
    ax_low .plot((x, x + d), (1, 1 + d),
                 transform=ax_low.transAxes,
                 color='k', clip_on=False)
ax_low.axhline(0, color='gray', linewidth=1, alpha=0.5)
fig.legend(
    loc="lower center",
    ncol=2,
    bbox_to_anchor=(0.5, -0.02),
    frameon=False
)
ax_low .set_xlabel("")
ax_high.set_ylabel("Relative Price Impact")
fig.suptitle("Relative Price Impact by Pool", y=1.02)

plt.tight_layout()
plt.savefig("broken_axis_price_impact_adjusted.png", dpi=300, bbox_inches="tight")
plt.show()
