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
    """Helper to find the actual column name in the CSV regardless of case/spaces."""
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
        df = pd.read_csv(file_path, low_memory=False)
        
        mission_col = get_col_name(df, ['mission type', 'mission', 'mission_type'])
        mode_col = get_col_name(df, ['mode', 'operation mode', 'op_mode'])
        time_col = get_col_name(df, ['relative time', 'time', 'relative_time'])
        volt_col = get_col_name(df, ['voltage load', 'voltage', 'voltage_load', 'v'])

        if not all([mission_col, mode_col, time_col, volt_col]):
            return None

        discharge = df[(df[mission_col] == 0) & (df[mode_col] == -1)].copy()
        
        if discharge.empty:
            return None

        # Process SOC - Using 3600*1000 assuming time is in milliseconds to get realistic Ah
        discharge['time_hrs'] = (discharge[time_col] - discharge[time_col].iloc[0]) / (3600 * 1000)
        current = current_map[battery_id]
        total_time = discharge['time_hrs'].max()
        
        if total_time <= 0: return None

        Q = current * total_time 
        discharge['SOC'] = 1 - (current * discharge['time_hrs'] / Q)
        
        return discharge[['SOC', volt_col]].rename(columns={volt_col: 'voltage'}), Q
        
    except Exception as e:
        print(f"Error processing {battery_id}: {e}")
        return None

# EXECUTION 
print("Step 1: Training Master Model...")
result_01 = load_and_process('0.1')

if result_01 is not None:
    train_data, _ = result_01
    coeffs = np.polyfit(train_data['SOC'], train_data['voltage'], 6)
    model_func = np.poly1d(coeffs)

    coeff_df = pd.DataFrame({'Coeff_Index': range(len(coeffs)), 'Value': coeffs})
    coeff_df.to_csv('ocv_soc_model_coefficients.csv', index=False)
    print("Saved: ocv_soc_model_coefficients.csv")

    print("Step 2: Analyzing all batteries...")
    results = []
    plt.figure(figsize=(10, 6))

    for bid in current_map.keys():
        data = load_and_process(bid)
        if data:
            df_batt, q_est = data
            pred_volt = model_func(df_batt['SOC'])
            rmse = np.sqrt(mean_squared_error(df_batt['voltage'], pred_volt))
            results.append({'Battery': bid, 'Capacity_Ah': round(q_est, 3), 'RMSE': round(rmse, 4)})
            
            if bid in group_b_test_files:
                plt.plot(df_batt['SOC'], df_batt['voltage'], label=f'Pack {bid}')

    # Plot Master Model
    s_ax = np.linspace(0, 1, 100)
    plt.plot(s_ax, model_func(s_ax), 'k--', label='Master Model', linewidth=2)
    plt.title('Battery SOC vs Voltage Analysis')
    plt.xlabel('SOC'); plt.ylabel('Voltage (V)'); plt.legend(); plt.grid(True)
    plt.savefig('ocv_soc_plot.png')
    plt.show()

    # Save final summary to CSV for "Evaluation Metrics" deliverable
    summary_df = pd.DataFrame(results)
    summary_df.to_csv('evaluation_metrics.csv', index=False)
    print("Saved: evaluation_metrics.csv")

    print("\n--- PERFORMANCE SUMMARY ---")
    print(summary_df.to_string(index=False))
else:
    print("Failed to initialize. Please check your CSV headers.")