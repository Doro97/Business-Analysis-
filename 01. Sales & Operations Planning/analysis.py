import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Simulate historical demand and supply data (2022-2024 monthly)
np.random.seed(42)
months = pd.date_range(start="2022-01-01", end="2024-12-01", freq='MS')
data = pd.DataFrame({
    "Month": months,
    "Demand": np.round(500000 + 30000*np.sin(np.arange(len(months))*2*np.pi/12) + np.random.normal(0,15000,len(months)),0),
    "Supply": np.round(500000 + 25000*np.sin((np.arange(len(months))*2*np.pi/12) + 0.5) + np.random.normal(0,15000,len(months)),0)
})

# Add forecast for 2025 based on trend + seasonality pattern
future_months = pd.date_range(start="2025-01-01", end="2025-12-01", freq='MS')
future_demand = np.round(510000 + 30000*np.sin(np.arange(len(future_months))*2*np.pi/12) + np.random.normal(0,15000,len(future_months)),0)
future_supply = np.round(500000 + 25000*np.sin((np.arange(len(future_months))*2*np.pi/12) + 0.5) + np.random.normal(0,15000,len(future_months)),0)

forecast_df = pd.DataFrame({
    "Month": future_months,
    "Demand": future_demand,
    "Supply": future_supply
})

# Chart 1 – Historical Demand vs Supply
plt.figure(figsize=(12,6))
plt.plot(data["Month"], data["Demand"], label="Demand", color="blue", marker="o")
plt.plot(data["Month"], data["Supply"], label="Supply", color="orange", marker="o")
plt.axhline(y=data["Demand"].mean(), color="gray", linestyle="--", alpha=0.5)
plt.title("Historical Demand vs Supply (2022–2024)", fontsize=14, weight="bold")
plt.xlabel("Month")
plt.ylabel("Units")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()

# Chart 2 – Forecasted Demand & Supply Gap for 2025
plt.figure(figsize=(12,6))
bar_width = 0.35
x = np.arange(len(forecast_df))
plt.bar(x - bar_width/2, forecast_df["Demand"], bar_width, label="Forecasted Demand", color="blue")
plt.bar(x + bar_width/2, forecast_df["Supply"], bar_width, label="Expected Supply", color="orange")
gap = forecast_df["Demand"] - forecast_df["Supply"]
plt.plot(x, gap, color="red", marker="o", label="Gap (Units)")
plt.xticks(x, [m.strftime("%b") for m in forecast_df["Month"]], rotation=45)
plt.title("2025 Forecasted Demand vs Expected Supply", fontsize=14, weight="bold")
plt.xlabel("Month")
plt.ylabel("Units")
plt.legend()
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()

# Chart 3 – Annual Lost Sales Value (2022–2025)
annual_data = pd.concat([data, forecast_df])
annual_data["Year"] = annual_data["Month"].dt.year
annual_data["Gap"] = annual_data["Demand"] - annual_data["Supply"]
price_per_unit = 5  # USD assumption
lost_sales = annual_data.groupby("Year")["Gap"].apply(lambda g: sum(g[g>0])*price_per_unit)

plt.figure(figsize=(8,6))
plt.bar(lost_sales.index, lost_sales.values, color="red")
plt.title("Annual Lost Sales Value (USD)", fontsize=14, weight="bold")
plt.xlabel("Year")
plt.ylabel("Lost Sales (USD)")
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()
