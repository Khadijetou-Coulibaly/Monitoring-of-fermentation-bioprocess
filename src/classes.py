import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
class BioprocessMonitor:
    def __init__(self, filepath, ph_lims, temperature_lims):
        """
        Utility class used to monitor bioprocesses by
        generating dashboards and summaries.

        Parameters
        ----------
        filepath : str
            Input CSV dataset path.
        ph_lims : tuple[float, float]
            Lower and upper acceptable pH limits.
        temperature_lims : tuple[float, float]
            Lower and upper acceptable temperature limits.
        """

        self.ph_lims = ph_lims
        self.temperature_lims = temperature_lims
        self.df = pd.read_csv(filepath)

    def extract_batch(self, batch_id):
        """
        Extracts data corresponding to a single batch.

        Parameters
        ----------
        batch_id : int
            Batch identifier.

        Returns
        -------
        pandas.DataFrame
            DataFrame containing only rows associated with
            the requested batch.
        """
        return self.df[self.df["batch_id"] == batch_id]



    def optimal_ph_mask(self, df_batch):
        """
        Determines whether each pH measurement falls within
        the acceptable operating range.

        Parameters
        ----------
        df_batch : pandas.DataFrame
            Batch-specific DataFrame.

        Returns
        -------
        array-like of bool
            A mask whereby True indicates that the measurement
            is within the acceptable operating range.
        """
        return (df_batch["pH"] >= self.ph_lims[0]) & (df_batch["pH"] <= self.ph_lims[1])

    def optimal_temperature_mask(self, df_batch):
        """
        Determines whether each temperature measurement falls
        within the acceptable operating range.

        Parameters
        ----------
        df_batch : pandas.DataFrame
            Batch-specific DataFrame.

        Returns
        -------
        array-like of bool
            A mask whereby True indicates that the measurement
            is within the acceptable operating range.
        """
        return (df_batch["temperature_C"] >= self.temperature_lims[0]) & (
                df_batch["temperature_C"] <= self.temperature_lims[1]
        )


    def get_n_batches(self):
        """
        Determines the number of unique batches present
        in the dataset.

        Returns
        -------
        int
            Total number of distinct batch identifiers.
        """
        return self.df['batch_id'].nunique()

    def export_dashboard(self, batch_id, filepath):
        """
        Creates and saves a dashboard figure for a single batch.

        Parameters
        ----------
        batch_id : int
            Batch identifier.
        filepath : str
            Output PNG image path.

        Dashboard Requirements
        ----------------------
        Create a 2 × 2 figure containing:

        Top-Left
            Glucose, biomass, and product concentrations versus time.
            - A different color and marker should be used for each substance.

        Top-Right
            Temperature versus time.
            - Measurements within the acceptable temperature range
              should be displayed as green circles.
            - Measurements outside the acceptable temperature range
              should be displayed as red X markers.

        Bottom-Left
            pH versus time.
            - Measurements within the acceptable pH range
              should be displayed as green circles.
            - Measurements outside the acceptable pH range
              should be displayed as red X markers.

        Bottom-Right
            Dissolved oxygen versus time.

        Additional Requirements
        -----------------------
        - Use scatter plots.
        - Add x-axis and y-axis labels.
        - Add legends where appropriate.
        - Apply consistent formatting across all subplots unless
          indicated otherwise.
        - Apply a tick spacing of 6 h on the x-axis for all subplots.
        - Save the figure to the provided filepath.
        - Close the figure after saving.
        """
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        df_batch = self.extract_batch(batch_id)
        # Concentrations
        axes[0, 0].scatter(
            df_batch["time_h"],
            df_batch["C_glucose_g_L^-1"],
            color="orange",
            marker="^",
            label="Glucose",
            )
        axes[0, 0].scatter(
            df_batch["time_h"],
            df_batch["C_biomass_g_L^-1"],
            color="green",
            marker="+",
            label="Biomass",
        )
        axes[0, 0].scatter(
            df_batch["time_h"],
            df_batch["C_product_g_L^-1"],
            color="blue",
            marker="D",
            label="Product",
        )

        axes[0, 0].set_xlabel("Time (h)")
        axes[0, 0].set_ylabel("Concentration (g/L)")
        axes[0, 0].set_title(f"Concentrations for Batch {batch_id}")
        axes[0, 0].legend()
        axes[0, 0].grid(True)

        #For the temperature
        in_range_T = df_batch[self.optimal_temperature_mask(df_batch)]
        out_range_T = df_batch[
            (df_batch["temperature_C"] < self.temperature_lims[0])|
            (df_batch["temperature_C"] > self.temperature_lims[1])
        ]
        axes[0, 1].scatter(
        in_range_T ["time_h"],
        in_range_T ["temperature_C"],
        color="green",
        marker="o",
        label="InRange",
        )
        axes[0, 1].scatter(
        out_range_T ["time_h"],
        out_range_T ["temperature_C"],
        color="red",
        marker="x",
        label="OutRange",
        )
        axes[0, 1].set_xlabel("Time (h)")
        axes[0, 1].set_ylabel("Temperature in C")
        axes[0, 1].set_title(f"Temperatures for Batch {batch_id}")
        axes[0, 1].legend()
        axes[0, 1].grid(True)

        #For the pH
        in_range_pH = df_batch[self.optimal_ph_mask(df_batch)]
        out_range_pH = df_batch[
            (df_batch["pH"] < self.ph_lims[0])
            | (df_batch["pH"] > self.ph_lims[1])
        ]
        axes[1, 0].scatter(
        in_range_pH ["time_h"],
        in_range_pH ["pH"],
        color="green",
        marker="o",
        label="InRange",
        )
        axes[1, 0].scatter(
        out_range_pH ["time_h"],
        out_range_pH ["pH"],
        color="red",
        marker="x",
        label="OutRange",
        )
        axes[1, 0].set_xlabel("Time (h)")
        axes[1, 0].set_ylabel("pH")
        axes[1, 0].set_title(f"pH for Batch {batch_id}")
        axes[1, 0].legend()
        axes[1, 0].grid(True)

        #For the oxygen
        axes[1, 1]. scatter(
        df_batch["time_h"],
        df_batch["DO_percent"],
        color="blue",
        marker="*",
        label="Oxy",
        )
        axes[1, 1].set_xlabel("Time (h)")
        axes[1, 1].set_ylabel("% of oxygen")
        axes[1, 1].set_title(f"oxygen percentages for Batch {batch_id}")
        axes[1, 1].legend()
        axes[1, 1].grid(True)


        max_time = df_batch["time_h"].max()
        for ax in axes.flat:
            ax.set_xticks(np.arange(0, max_time + 1, 6))


        plt.tight_layout()
        fig.savefig(filepath)
        plt.close(fig)

    def export_summary(self, filepath):
        """
        Generates a batch summary table and exports it to a CSV file.

        Parameters
        ----------
        filepath : str
            Output CSV table path.

        Summary Table Columns
        ---------------------
        batch_id
            Batch identifier.

        ph_optimal_percent
            Percentage of measurements in a batch within the
            acceptable pH range, rounded to 2 decimal places.

        temperature_optimal_percent
            Percentage of measurements in a batch within the
            acceptable temperature range, rounded to 2 decimal places.

        C_product_g_L^-1_final
            Final product concentration for the batch.
        """
        summary_data = []
        batch_ids = self.df["batch_id"].unique()
        for batch_id in batch_ids:
            df_batch = self.extract_batch(batch_id)

            in_range_ph = self.optimal_ph_mask(df_batch).sum()
            total_count = len(df_batch)

            ph_optimal_percent = (in_range_ph / total_count) * 100
            ph_optimal_percent_rounded = round(ph_optimal_percent, 2)

            in_range_temperature = self.optimal_temperature_mask(df_batch).sum()
            total_count = len(df_batch)

            temperature_optimal_percent = (in_range_temperature / total_count) * 100
            temperature_optimal_percent_rounded = round(temperature_optimal_percent, 2)

            final_product_C = df_batch["C_product_g_L^-1"].iloc[-1]

            summary_data.append(
            {
            "batch_id": batch_id,
            "ph_optimal_percent": ph_optimal_percent_rounded,
            "temperature_optimal_percent": temperature_optimal_percent_rounded,
            "C_product_g_L^-1_final_Concentration": final_product_C,
            }
            )
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_csv(filepath, index=False)
