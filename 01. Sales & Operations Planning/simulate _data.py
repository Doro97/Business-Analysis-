# simulate_data.py

import numpy as np
import pandas as pd
import os


class DemandSupplySimulator:
    def __init__(self, start_date="2022-01-01", end_date="2025-06-30", seed=42):
        np.random.seed(seed)
        self.start_date = start_date
        self.end_date = end_date
        self.data = None

    def simulate(self):
        months = pd.date_range(start=self.start_date, end=self.end_date, freq='MS')

        demand = np.round(
            500000
            + 30000 * np.sin(np.arange(len(months)) * 2 * np.pi / 12)
            + np.random.normal(0, 3000, len(months)), 0
        )

        supply = np.round(
            500000
            + 25000 * np.sin((np.arange(len(months)) * 2 * np.pi / 12) + 0.5)
            + np.random.normal(0, 5000, len(months)), 0
        )

        def status(d, s):
            if abs(d - s) <= 2000:
                return "Met"
            elif s > d:
                return "Exceeded"
            else:
                return "Not Met"

        df = pd.DataFrame({
            "Month": months,
            "Demand": demand,
            "Supply": supply
        })

        df["Status"] = [status(d, s) for d, s in zip(df["Demand"], df["Supply"])]
        df.set_index("Month", inplace=True)
        df['Availability_Gap'] = df['Demand'] - df['Supply']
        df['Service_Level_%'] = (df['Supply'] / df['Demand']) * 100

        self.data = df
        return df

    def save_to_csv(self, folder="Data/", filename="historical_demand_supply.csv"):
        os.makedirs(folder, exist_ok=True)
        path = os.path.join(folder, filename)
        self.data.to_csv(path, index_label="Month")
        return path

    def run(self):
        print("Simulating historical demand and supply data...")
        self.simulate()
        csv_path = self.save_to_csv()
        print(f"Data saved to: {csv_path}")


if __name__ == "__main__":
    print("Starting demand-supply simulation...")
    sim = DemandSupplySimulator()
    sim.run()
