import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import os

def export_report(scheduler, log_tree, output_dir=None):
    """
    Export analysis report containing energy consumption, execution log, and power state transitions.
    """
    # If no output directory specified, prompt user
    if output_dir is None:
        output_dir = filedialog.askdirectory(title="Select Output Directory")
        if not output_dir:
            return

    # Create timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 1. Save Energy Consumption Graph
    energy_fig, energy_ax = plt.subplots(figsize=(10, 6))
    energy_ax.plot(scheduler.time_history, scheduler.energy_history, 'b-', label='Energy Consumption')
    energy_ax.set_title("Energy Consumption Over Time")
    energy_ax.set_xlabel("Time (s)")
    energy_ax.set_ylabel("Energy (J)")
    energy_ax.grid(True)
    energy_ax.legend()
    
    energy_plot_path = os.path.join(output_dir, f"energy_consumption_{timestamp}.png")
    energy_fig.savefig(energy_plot_path)
    plt.close(energy_fig)
    
    # 2. Save Power State Transitions Graph
    state_fig, state_ax = plt.subplots(figsize=(10, 4))
    state_map = {state: i for i, state in enumerate(scheduler.POWER_STATES)}
    y = [state_map[state] for state in scheduler.state_history]
    x = range(len(y))
    state_ax.plot(x, y, 'ro-', markersize=8)
    state_ax.set_title("CPU Power State Transitions")
    state_ax.set_yticks(list(state_map.values()))
    state_ax.set_yticklabels(list(state_map.keys()))
    state_ax.set_xlabel("Transition #")
    state_ax.grid(True)
    
    state_plot_path = os.path.join(output_dir, f"power_states_{timestamp}.png")
    state_fig.savefig(state_plot_path)
    plt.close(state_fig)
    
    # 3. Save Execution Log as CSV
    log_data = []
    for item in log_tree.get_children():
        values = log_tree.item(item)['values']
        log_data.append({
            'Time (s)': values[0],
            'Event Type': values[1],
            'Task': values[2],
            'Details': values[3]
        })
    
    log_df = pd.DataFrame(log_data)
    log_csv_path = os.path.join(output_dir, f"execution_log_{timestamp}.csv")
    log_df.to_csv(log_csv_path, index=False)
    
    # 4. Generate Summary Statistics
    completed = len(scheduler.completed_tasks)
    efficiency = completed / scheduler.energy_consumed if scheduler.energy_consumed > 0 else 0
    battery_pct = (scheduler.battery_capacity / 5000) * 100
    
    summary_stats = f"""
Energy-Aware Scheduler Analysis Report
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
=====================================

Summary Statistics:
- Total Energy Consumed: {scheduler.energy_consumed:.2f} J
- Tasks Completed: {completed}
- QoS Violations: {scheduler.qos_violations}
- Efficiency: {efficiency:.2f} tasks/J
- Battery Remaining: {battery_pct:.1f}%

Output Files:
- Energy Consumption Graph: {energy_plot_path}
- Power State Transitions Graph: {state_plot_path}
- Execution Log: {log_csv_path}
"""
    
    # 5. Save Summary Report
    report_path = os.path.join(output_dir, f"scheduler_report_{timestamp}.txt")
    with open(report_path, 'w') as f:
        f.write(summary_stats)
    
    messagebox.showinfo("Export Successful", f"Report generated successfully at:\n{output_dir}")

def modify_app_to_include_export(app):
    """
    Modify the existing EnergyAwareSchedulerApp to include export functionality.
    """
    # Find Simulation Controls frame dynamically
    sim_frame = None
    for widget in app.root.winfo_children():
        for child in widget.winfo_children():
            if isinstance(child, ttk.LabelFrame) and child.cget("text") == "Simulation Controls":
                sim_frame = child
                break
        if sim_frame:
            break
    if not sim_frame:
        raise ValueError("Could not find Simulation Controls frame")
    
    # Add Export Button to Simulation Controls
    ttk.Button(
        sim_frame,
        text="Export Report",
        command=lambda: export_report(app.scheduler, app.log_tree)
    ).grid(row=3, column=0, columnspan=2, pady=5, sticky="ew")

if __name__ == "__main__":
    # This is a modification to the existing app, so we don't create a new instance
    # Instead, you would call modify_app_to_include_export(app) after creating the main app
    pass