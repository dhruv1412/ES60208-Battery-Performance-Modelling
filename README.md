# ES60208-Battery-Performance-Modelling

This repository contains an automated workflow for estimating Li-ion cell parameters and State of Charge (SOC) using the NASA Battery Data Set.
Project Overview
The goal of this project is to develop a robust SOC estimator and identify time-varying Equivalent Circuit Model (ECM) parameters.
Target Accuracy: SOC error <= 5% across typical operating profiles.

Phase 1 (OCV-SOC Modeling)
We have completed the derivation of the OCV-SOC curve from raw charge/discharge tests.

Key Features
 * Automated Data Processing: Cleans and processes raw NASA battery CSV files based on mission and operation modes.
 * OCV-SOC Mapping: Utilizes a 6th-degree polynomial fit to characterize the Open-Circuit Voltage relative to the State of Charge.
 * Performance Metrics: Generates RMSE and Capacity (Ah) predictions for multiple battery packs.
 
Results
 * Master Model Coefficients: Saved in ocv_soc_model_coefficients.csv.
 * Evaluation Summary: Detailed RMSE metrics for packs like 4.1, 5.1, 4.0, and 5.0 are stored in evaluation_metrics.csv.
 * Visualization: ocv_soc_plot.png compares individual pack performance against the Master Model.
 
Installation & Usage
 * Place your battery data in a folder named regular_alt_batteries.
 * Ensure you have pandas, numpy, matplotlib, and scikit-learn installed.
 * Run the main script:
   python battery_analysis.py
