import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from sklearn.metrics import mean_squared_error

folder_path = 'regular_alt_batteries' 

current_map = {
    '0.1': 9.30, '1.1': 9.30, '3.1': 12.9, '2.2': 12.9,
    '2.3': 14.3, '5.2': 14.3, '0.0': 16.0, '1.0': 16.0,
    '2.0': 19.0, '3.0': 19.0, '2.1': 19.0,
    '4.1': 14.3, '5.1': 14.3, '4.0': 17.0, '5.0': 17.0
}

group_b_test_files = ['4.1', '5.1', '4.0', '5.0'] 

def get_col_name(df, possible_names):
    for name in possible_names:
        for col in df.columns:
            if name.lower().replace(" ", "_") == col.lower().replace(" ", "_"):
                return col
    return None

def load_and_process(battery_id):
    file_id = battery_id.replace('.', '')
    file_path = os.path.join(folder_path, f'battery{file_id}.csv')
    
    if not os.path.exists(file_path):
        return None
    
    try:
        # Load and drop completely empty rows/cols
        df = pd.read_csv(file_path, low_memory=False).dropna(how='all')
        
        mission_col = get_col_name(df, ['mission type', 'mission', 'mission_type'])
        mode_col = get_col_name(df, ['mode', 'operation mode', 'op_mode'])
        time_col = get_col_name(df, ['relative time', 'time', 'relative_time'])
        volt_col = get_col_name(df, ['voltage load', 'voltage', 'voltage_load', 'v'])

        if not all([mission_col, mode_col, time_col, volt_col]):
            return None

        # Ensure numeric types and drop NaNs in critical columns
        for col in [time_col, volt_col]:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=[time_col, volt_col, mission_col, mode_col])

        # Identify discharge segments
        discharge_mask = (df[mission_col] == 0) & (df[mode_col] == -1)
        discharge = df[discharge_mask].copy()
        
        if discharge.empty:
            return None

        current = current_map[battery_id]

        # IMPROVED R0 EXTRACTION 
        first_idx = discharge.index[0]
        # Check if there is a resting row before discharge starts
        if first_idx > 0 and (first_idx - 1) in df.index:
            v_before_load = df.loc[first_idx - 1, volt_col]
            v_after_load = df.loc[first_idx, volt_col]
            r0_est = abs(v_before_load - v_after_load) / current
        else:
            r0_est = 0.05 # Realistic fallback for these packs (50 mOhms)
        
        # If r0_est calculation resulted in NaN, use fallback
        if np.isnan(r0_est): r0_est = 0.05

        # Calculate OCV
        discharge['OCV'] = discharge[volt_col] + (current * r0_est)

        # Process SOC
        discharge['time_hrs'] = (discharge[time_col] - discharge[time_col].iloc[0]) / (3600 * 1000)
        total_time = discharge['time_hrs'].max()
        if total_time <= 0: return None

        Q = current * total_time 
        discharge['SOC'] = 1 - (current * discharge['time_hrs'] / Q)
        
        # remove any NaNs generated during calculations
        final_df = discharge[['SOC', volt_col, 'OCV']].rename(columns={volt_col: 'voltage'}).dropna()
        
        return final_df, Q, r0_est
        
    except Exception as e:
        print(f"Error processing {battery_id}: {e}")
        return None

# EXECUTION 
print("Step 1: Training Master Model using Corrected OCV...")
result_01 = load_and_process('0.1')

if result_01 is not None:
    train_data, _, r0_train = result_01
    
    # Fit model to OCV
    coeffs = np.polyfit(train_data['SOC'], train_data['OCV'], 6)
    ocv_model_func = np.poly1d(coeffs)

    pd.DataFrame({'Coeff_Index': range(len(coeffs)), 'Value': coeffs}).to_csv('ocv_soc_model_coefficients.csv', index=False)
    print("Saved: ocv_soc_model_coefficients.csv")

    print("Step 2: Analyzing all batteries...")
    results = []
    plt.figure(figsize=(10, 6))

    for bid in current_map.keys():
        data = load_and_process(bid)
        if data:
            df_batt, q_est, r0_batt = data
            
            # Predict OCV then subtract IR drop to get Terminal Voltage
            pred_ocv = ocv_model_func(df_batt['SOC'])
            pred_volt = pred_ocv - (current_map[bid] * r0_batt)
            
            # NAN-SAFE RMSE CALCULATION 
            # Create a mask for finite values only
            mask = np.isfinite(df_batt['voltage']) & np.isfinite(pred_volt)
            if np.any(mask):
                rmse = np.sqrt(mean_squared_error(df_batt['voltage'][mask], pred_volt[mask]))
            else:
                rmse = np.nan

            results.append({
                'Battery': bid, 
                'Capacity_Ah': round(q_est, 3), 
                'R0_Ohms': round(r0_batt, 4), 
                'RMSE': round(rmse, 4) if not np.isnan(rmse) else "N/A"
            })
            
            if bid in group_b_test_files:
                plt.plot(df_batt['SOC'], df_batt['voltage'], alpha=0.3, label=f'Raw {bid}')
                plt.plot(df_batt['SOC'], df_batt['OCV'], '--', label=f'OCV {bid}')

    # Plot Master OCV Model
    s_ax = np.linspace(0, 1, 100)
    plt.plot(s_ax, ocv_model_func(s_ax), 'k-', label='Master OCV Model', linewidth=3)
    plt.title('Corrected OCV-SOC Analysis (IR-Drop Removed)')
    plt.xlabel('SOC'); plt.ylabel('Voltage (V)'); plt.legend(); plt.grid(True)
    plt.savefig('ocv_soc_plot.png')
    plt.show()

    summary_df = pd.DataFrame(results)
    summary_df.to_csv('evaluation_metrics.csv', index=False)
    print("\n--- PERFORMANCE SUMMARY ---")
    print(summary_df.to_string(index=False))
else:
    print("Failed to initialize. Check if 'battery01.csv' exists and has correct headers.")
