# Mobile-CPU-Energy-Aware-Scheduler

Energy-Efficient CPU Scheduling Algorithm
This project implements an energy-efficient CPU scheduling algorithm designed for mobile and embedded systems, where power efficiency is critical. The algorithm minimizes energy consumption while maintaining performance through dynamic power state management and priority-based task scheduling. The system includes a graphical user interface (GUI) for task configuration, simulation control, and real-time monitoring, along with visualization and reporting features to analyze energy usage and task execution.
Features

Energy-Aware Scheduling: Prioritizes tasks based on priority (1–5) and age, with dynamic priority boosting for Quality of Service (QoS) violations.
Power State Management: Switches between power states (performance: 1.8W, balanced: 1.2W, powersave: 0.8W, deep-save: 0.3W) to optimize energy use.
GUI: Built with Tkinter, offering:
Task input panel for name, priority, burst time, and deadline.
Simulation controls (start, stop, reset, speed adjustment).
Real-time stats (energy, tasks completed, battery percentage).
Task queue display.


Visualization: Real-time graphs for energy consumption and power state transitions, plus an execution log table.
Reporting: Exports reports including energy graphs (PNG), power state graphs (PNG), execution logs (CSV), and a summary (text).

Prerequisites

Python: Version 3.11 or higher.
Libraries:
tkinter: Included with Python for GUI.
matplotlib: For plotting graphs.
pandas: For CSV export.


Operating System: Windows, macOS, or Linux (tested on Windows).

Installation

Clone the Repository (if using GitHub):
git clone <your-repo-url>
cd EnergyEfficientCPUScheduler


Set Up a Virtual Environment (recommended):
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux


Install Dependencies:
pip install matplotlib pandas


Verify Files:Ensure the following files are in the project directory:

energy_scheduler.py: Main application (scheduler, GUI, visualization).
export_report.py: Report generation logic.



Usage

Run the Application:
python energy_scheduler.py


Interact with the GUI:

Task Creation:
Enter task details (name, priority 1–5, burst time in ms, optional deadline in ms).
Click "Add Task" or "Add Random Tasks" to populate the queue.


Simulation:
Click "Start Simulation" to begin processing tasks.
Adjust speed with the slider (0.1–5x).
Use "Stop Simulation" or "Reset Simulation" as needed.


Monitoring:
View real-time stats (energy, tasks, battery).
Observe the task queue, energy graph, power state graph, and execution log.


Export Reports:
Click "Export Report" to save:
Energy consumption graph (energy_consumption_YYYYMMDD_HHMMSS.png).
Power state transitions graph (power_states_YYYYMMDD_HHMMSS.png).
Execution log (execution_log_YYYYMMDD_HHMMSS.csv).
Summary report (scheduler_report_YYYYMMDD_HHMMSS.txt).






Example Workflow:

Add tasks (e.g., "Email", priority 3, burst time 1000ms).
Start simulation and let it run for 20 seconds.
Click "Export Report", select an output folder, and verify the generated files.



Project Structure

energy_scheduler.py: Contains the Task, CPUScheduler, and EnergyAwareSchedulerApp classes, handling scheduling, GUI, and visualization.
export_report.py: Implements the export_report function to generate and save reports.

Notes

Current Issue: The "Export Report" button may fail due to a widget path error (KeyError: '!labelframe2'). To fix, ensure export_report.py uses the dynamic search for the "Simulation Controls" frame (see code comments).
Dependencies: Tkinter is included with Python, but matplotlib and pandas must be installed separately.
Simulation: The scheduler simulates a single-core CPU with a 100ms time quantum.

Troubleshooting

Error: KeyError: '!labelframe2':
Update export_report.py to use dynamic frame search:sim_frame = None
for widget in app.root.winfo_children():
    for child in widget.winfo_children():
        if isinstance(child, ttk.LabelFrame) and child.cget("text") == "Simulation Controls":
            sim_frame = child
            break
    if sim_frame:
        break


Re-run the application.


Missing Libraries:
Install missing dependencies:pip install matplotlib pandas




GUI Lag:
Reduce simulation speed or increase the GUI update interval (modify root.after(200, ...) to 500 in update_visualization).



Future Enhancements

Fix the export button issue to ensure reliable report generation.
Add support for multi-core scheduling.
Integrate with real hardware for practical testing.
Enhance the GUI with task editing or graph zooming features.
Optimize performance for large task sets.

License
This project is licensed under the MIT License. See the LICENSE file for details (if applicable).
Contact
For questions or contributions, please contact [Your Name/Email] or open an issue on GitHub.
