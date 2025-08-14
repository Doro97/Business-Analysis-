# forecast_from_data.py

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error, r2_score
import warnings

warnings.filterwarnings("ignore")


class DemandSupplyForecast:
    def __init__(self, csv_path="Data/historical_demand_supply.csv"):
        self.data = pd.read_csv(csv_path, parse_dates=["Month"], index_col="Month")
        self.forecast_df = None
        self.metrics = {}
        self.order = (1, 1, 1)
        self.seasonal = (1, 1, 1, 12)

    def calc_metrics(self, actual, pred):
        return (
            mean_absolute_percentage_error(actual, pred) * 100,
            np.sqrt(mean_squared_error(actual, pred)),
            r2_score(actual, pred)
        )

    def train_and_evaluate(self, train_end="2024-12-01"):
        train = self.data[:train_end]
        test = self.data['2025-01-01':]

        # Fit SARIMA
        d_fit = SARIMAX(train['Demand'], order=self.order, seasonal_order=self.seasonal,
                        enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
        s_fit = SARIMAX(train['Supply'], order=self.order, seasonal_order=self.seasonal,
                        enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)

        d_pred_test = d_fit.forecast(steps=len(test))
        s_pred_test = s_fit.forecast(steps=len(test))

        # Store metrics
        self.metrics['demand_mape'], self.metrics['demand_rmse'], self.metrics['demand_r2'] = \
            self.calc_metrics(test['Demand'], d_pred_test)
        self.metrics['supply_mape'], self.metrics['supply_rmse'], self.metrics['supply_r2'] = \
            self.calc_metrics(test['Supply'], s_pred_test)

        return self.metrics

    def forecast_future(self, forecast_steps=18):
        train_full = self.data[:'2025-06-01']

        d_fit_full = SARIMAX(train_full['Demand'], order=self.order, seasonal_order=self.seasonal,
                             enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
        s_fit_full = SARIMAX(train_full['Supply'], order=self.order, seasonal_order=self.seasonal,
                             enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)

        future_months = pd.date_range(start="2025-07-01", periods=forecast_steps, freq="MS")
        d_forecast = d_fit_full.forecast(steps=forecast_steps)
        s_forecast = s_fit_full.forecast(steps=forecast_steps)

        forecast_df = pd.DataFrame({
            "Demand_Forecast": np.round(d_forecast, 0).astype(int),
            "Supply_Forecast": np.round(s_forecast, 0).astype(int),
        }, index=future_months)

        forecast_df["Availability_Gap"] = forecast_df["Demand_Forecast"] - forecast_df["Supply_Forecast"]
        forecast_df["Service_Level_%"] = (forecast_df["Supply_Forecast"] / forecast_df["Demand_Forecast"]) * 100

        self.forecast_df = forecast_df
        return forecast_df

    def plot_and_save(self, folder="Data"):
        os.makedirs(folder, exist_ok=True)

        # Historical chart
        plt.figure(figsize=(14, 6))
        plt.plot(self.data.index, self.data['Demand'], label='Historical Demand', color='blue', marker='o')
        plt.plot(self.data.index, self.data['Supply'], label='Historical Supply', color='pink', marker='o')
        plt.axvline(pd.to_datetime("2025-06-30"), color='gray', linestyle=':', label='Forecast Start')
        plt.title('Historical Demand vs Supply')
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.savefig(os.path.join(folder, "historical_demand_supply.png"))
        plt.close()

        # Forecast chart
        plt.figure(figsize=(14, 6))
        plt.plot(self.forecast_df.index, self.forecast_df['Demand_Forecast'], label='Forecast Demand', linestyle='--', color='blue', marker='x')
        plt.plot(self.forecast_df.index, self.forecast_df['Supply_Forecast'], label='Forecast Supply', linestyle='--', color='pink', marker='x')
        plt.fill_between(self.forecast_df.index,
                         self.forecast_df['Demand_Forecast'], self.forecast_df['Supply_Forecast'],
                         where=(self.forecast_df['Supply_Forecast'] < self.forecast_df['Demand_Forecast']),
                         color='red', alpha=0.3, label='Shortfall')
        plt.fill_between(self.forecast_df.index,
                         self.forecast_df['Demand_Forecast'], self.forecast_df['Supply_Forecast'],
                         where=(self.forecast_df['Supply_Forecast'] > self.forecast_df['Demand_Forecast']),
                         color='green', alpha=0.3, label='Surplus')
        plt.axvline(pd.to_datetime("2025-06-30"), color='gray', linestyle=':', label='Forecast Start')
        plt.title('18-Month Forecast Demand vs Supply')
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.savefig(os.path.join(folder, "forecast_demand_supply.png"))
        plt.close()

        # Service level chart
        plt.figure(figsize=(14, 5))
        plt.plot(self.data.index, self.data['Service_Level_%'], label='Historical Service Level', color='green', marker='o')
        plt.plot(self.forecast_df.index, self.forecast_df['Service_Level_%'], label='Forecast Service Level', linestyle='--', color='darkgreen', marker='x')
        plt.axhline(y=100, color='gray', linestyle='--', alpha=0.6)
        plt.title('Service Level %')
        plt.legend()
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.savefig(os.path.join(folder, "service_level.png"))
        plt.close()

    def save_forecast(self, folder="Data", filename="forecast.csv"):
        path = os.path.join(folder, filename)
        self.forecast_df.to_csv(path, index_label="Month")
        return path

    def run(self):
        print("Training and evaluating forecast model...")
        metrics = self.train_and_evaluate()
        print("\n=== Model Accuracy Metrics ===")
        for k, v in metrics.items():
            print(f"{k}: {round(v, 2) if 'mape' in k or 'r2' in k else int(round(v))}")

        print("Forecasting future...")
        self.forecast_future()

        print("Saving plots...")
        self.plot_and_save()

        csv_path = self.save_forecast()
        print(f"Forecast saved to: {csv_path}")


if __name__ == "__main__":
    model = DemandSupplyForecast()
    model.run()
