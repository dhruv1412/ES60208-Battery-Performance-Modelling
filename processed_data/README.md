# Processed Battery Dataset (Downsampled)

## Overview
This folder contains a lightweight version of the "Accelerated Life Testing Dataset for Lithium-Ion Batteries" (NASA/PML-UCF). The original dataset was downsampled to facilitate fast deployment and testing of SOC estimation algorithms while keeping the repository size below 25MB.

## Data Processing Details
- **Downsampling Factor:** 1/100 (Every 100th row kept).
- **Tool used:** `downsample_script.py` (included in root).
- **Purpose:** To reduce file size for Git compatibility while preserving the overall voltage and current profiles for OCV-SOC and ECM parameter identification.

## Column Definitions
Each file contains the following logged data:
- `relative time`: Continuous time from start of life [s].
- `mode`: -1 = Discharge, 0 = Rest, 1 = Charge.
- `voltage charger`: Voltage during rest/charge [V].
- `voltage load`: Voltage under discharge load [V].
- `current load`: Measured discharge current [A].
- `temperature battery`: Cell electrode surface temperature [C].
- `mission type`: 0 = Reference discharge (Constant Current), 1 = Regular mission.

## Battery Pack Mapping (Current Levels)
Use the following current levels for model identification in this project:

### Constant Current Packs:
- **9.30A:** `battery_pack_0.1.csv`, `battery_pack_1.1.csv`
- **12.9A:** `battery_pack_3.1.csv`, `battery_pack_2.2.csv`
- **14.3A:** `battery_pack_2.3.csv`, `battery_pack_5.2.csv`
- **16.0A:** `battery_pack_0.0.csv`, `battery_pack_1.0.csv`
- **19.0A:** `battery_pack_2.0.csv`, `battery_pack_3.0.csv`, `battery_pack_2.1.csv`

### Variable Current Packs (Random Loading):
- **14.3A (avg):** `battery_pack_4.1.csv`, `battery_pack_5.1.csv`
- **17.0A (avg):** `battery_pack_4.0.csv`, `battery_pack_5.0.csv`

## Citation
Fricke, K., Nascimento, R. G., Corbetta, M., Kulkarni, C. S., & Viana, F. A. C. (2023). An accelerated Life Testing Dataset for Lithium-Ion Batteries with Constant and Variable Loading Conditions. NASA.
