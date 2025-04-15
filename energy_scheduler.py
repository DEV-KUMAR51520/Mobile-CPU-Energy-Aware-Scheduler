
import tkinter as tk
from tkinter import ttk, messagebox
import random
from export_report import modify_app_to_include_export
import threading
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque

class Task:
    def __init__(self, name, priority, burst_time, deadline=None):
        self.name = name
        self.priority = priority  # 1 (highest) to 5 (lowest)
        self.burst_time = burst_time
        self.remaining_time = burst_time
        self.arrival_time = time.time()
        self.deadline = deadline
        self.completed = False
        self.age = 0
        
    def execute(self, time_quantum, current_frequency):
        execution_speed = current_frequency / 1000  # Normalized speed factor
        actual_execution = min(time_quantum * execution_speed, self.remaining_time)
        self.remaining_time -= actual_execution
        self.age += actual_execution
        
        if self.remaining_time <= 0:
            self.completed = True
            
        return actual_execution
class CPUScheduler:
    POWER_STATES = {
        'performance': {'freq': 2000, 'power': 1.8},  # GHz and Watts
        'balanced': {'freq': 1500, 'power': 1.2},
        'powersave': {'freq': 1000, 'power': 0.8},
        'deep-save': {'freq': 500, 'power': 0.3}
    }
    
    def __init__(self):
        self.ready_queue = []
        self.completed_tasks = []
        self.current_task = None
        self.time = 0
        self.energy_consumed = 0
        self.energy_history = []
        self.time_history = []
        self.current_state = 'balanced'
        self.battery_capacity = 5000  # mAh
        self.voltage = 3.7  # Volts
        self.qos_violations = 0
        self.state_history = []
        
    def add_task(self, task):
        self.ready_queue.append(task)
        self.ready_queue.sort(key=lambda x: (x.priority, x.age))
        
    def calculate_energy(self, execution_time):
        power = self.POWER_STATES[self.current_state]['power']
        return power * (execution_time / 1000)
        
    def adjust_power_state(self):
        if not self.ready_queue:
            self.current_state = 'deep-save'
            return
            
        # Check for deadline-critical tasks
        urgent = any(t.deadline and (t.deadline - self.time) < 50 for t in self.ready_queue)
        
        # Check for QoS violations
        violating = any(t.age > self.get_max_age(t.priority) for t in self.ready_queue)
        
        if urgent or violating:
            self.current_state = 'performance'
        elif all(t.priority >= 4 for t in self.ready_queue):
            self.current_state = 'powersave'
        else:
            self.current_state = 'balanced'
            
    def get_max_age(self, priority):
        # Max allowed waiting time per priority (ms)
        return {
            1: 100, 2: 200, 3: 500, 4: 1000, 5: 2000
        }.get(priority, 2000)
            
    def schedule(self, time_quantum=100, log_callback=None):
        # Update task aging and check QoS
        for task in self.ready_queue:
            if task.age > self.get_max_age(task.priority):
                self.qos_violations += 1
                task.priority = max(1, task.priority - 1)
                if log_callback:
                    log_callback(
                        event_type="QoS Violation",
                        task_name=task.name,
                        details=f"Priority boosted to {task.priority}"
                    )
        
        self.adjust_power_state()
        
        if not self.ready_queue and not self.current_task:
            # Idle state
            idle_energy = self.calculate_energy(time_quantum)
            self.energy_consumed += idle_energy
            self.time += time_quantum / 1000
            self.energy_history.append(self.energy_consumed)
            self.time_history.append(self.time)
            self.state_history.append(self.current_state)
            if log_callback:
                log_callback(
                    event_type="Idle",
                    details=f"Deep save mode: {idle_energy:.4f}J"
                )
            return
            
        if self.current_task is None or self.current_task.completed:
            if self.current_task and self.current_task.completed:
                self.completed_tasks.append(self.current_task)
                if log_callback:
                    log_callback(
                        event_type="Task Completed",
                        task_name=self.current_task.name,
                        details=f"Total time: {self.time - self.current_task.arrival_time:.2f}s"
                    )
            if self.ready_queue:
                self.current_task = self.ready_queue.pop(0)
                if log_callback:
                    log_callback(
                        event_type="Task Started",
                        task_name=self.current_task.name,
                        details=f"Priority: {self.current_task.priority}, State: {self.current_state}"
                    )
            else:
                self.current_task = None
                
        if self.current_task:
            execution_time = self.current_task.execute(
                time_quantum, 
                self.POWER_STATES[self.current_state]['freq']
            )
            energy = self.calculate_energy(execution_time)
            self.energy_consumed += energy
            self.time += execution_time / 1000
            self.state_history.append(self.current_state)
            
            if log_callback:
                log_callback(
                    event_type="Execution",
                    task_name=self.current_task.name,
                    details=(
                        f"Freq: {self.POWER_STATES[self.current_state]['freq']}MHz, "
                        f"Energy: {energy:.4f}J, "
                        f"Remaining: {self.current_task.remaining_time}ms"
                    )
                )
            
            if not self.current_task.completed:
                self.ready_queue.append(self.current_task)
                self.current_task = None
                
        self.energy_history.append(self.energy_consumed)
        self.time_history.append(self.time)

class EnergyAwareSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mobile CPU Energy-Aware Scheduler")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.window_alive = True
        
        # Configure main window
        self.root.geometry("1400x900")
        self.root.minsize(1200, 800)
        
        # Initialize components
        self.scheduler = CPUScheduler()
        self.simulation_running = False
        self.simulation_speed = 1.0
        self.setup_ui()
        
        
        # Start periodic updates
        self.update_visualization()
        
    def on_close(self):
        """Handle window close event safely"""
        self.window_alive = False
        self.stop_simulation()
        self.root.destroy()
        
    def setup_ui(self):
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Left panel - Controls
        control_panel = ttk.Frame(self.root, padding="10")
        control_panel.grid(row=0, column=0, sticky="nsew")
        
        # Task creation controls
        task_frame = ttk.LabelFrame(control_panel, text="Task Creation", padding="10")
        task_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(task_frame, text="Task Name:").grid(row=0, column=0, sticky="w")
        self.task_name_entry = ttk.Entry(task_frame)
        self.task_name_entry.grid(row=0, column=1, sticky="ew", padx=5)
        self.task_name_entry.insert(0, "Task1")
        
        ttk.Label(task_frame, text="Priority (1-5):").grid(row=1, column=0, sticky="w")
        self.priority_combobox = ttk.Combobox(task_frame, values=[1, 2, 3, 4, 5])
        self.priority_combobox.grid(row=1, column=1, sticky="ew", padx=5)
        self.priority_combobox.current(2)
        
        ttk.Label(task_frame, text="Burst Time (ms):").grid(row=2, column=0, sticky="w")
        self.burst_time_entry = ttk.Entry(task_frame)
        self.burst_time_entry.grid(row=2, column=1, sticky="ew", padx=5)
        self.burst_time_entry.insert(0, "1000")
        
        ttk.Label(task_frame, text="Deadline (ms, optional):").grid(row=3, column=0, sticky="w")
        self.deadline_entry = ttk.Entry(task_frame)
        self.deadline_entry.grid(row=3, column=1, sticky="ew", padx=5)
        
        ttk.Button(task_frame, text="Add Task", command=self.add_task).grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")
        ttk.Button(task_frame, text="Add Random Tasks", command=self.add_random_tasks).grid(row=5, column=0, columnspan=2, pady=5, sticky="ew")
        
        # Simulation controls
        sim_frame = ttk.LabelFrame(control_panel, text="Simulation Controls", padding="10")
        sim_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(sim_frame, text="Start Simulation", command=self.start_simulation).grid(row=0, column=0, columnspan=2, pady=5, sticky="ew")
        ttk.Button(sim_frame, text="Stop Simulation", command=self.stop_simulation).grid(row=1, column=0, columnspan=2, pady=5, sticky="ew")
        ttk.Button(sim_frame, text="Reset Simulation", command=self.reset_simulation).grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")
        
        ttk.Label(sim_frame, text="Simulation Speed:").grid(row=3, column=0, sticky="w")
        self.speed_scale = ttk.Scale(sim_frame, from_=0.1, to=5, value=1, command=self.set_simulation_speed)
        self.speed_scale.grid(row=3, column=1, sticky="ew", padx=5)
        
        # Stats panel
        stats_frame = ttk.LabelFrame(control_panel, text="Statistics", padding="10")
        stats_frame.pack(fill=tk.X, pady=5)
        
        self.stats_vars = {
            'energy': tk.StringVar(value="Total Energy: 0.00 J"),
            'tasks': tk.StringVar(value="Tasks Completed: 0"),
            'violations': tk.StringVar(value="QoS Violations: 0"),
            'efficiency': tk.StringVar(value="Efficiency: 0.00 tasks/J"),
            'battery': tk.StringVar(value="Battery: 100.0%")
        }
        
        for i, (text, var) in enumerate(self.stats_vars.items()):
            ttk.Label(stats_frame, textvariable=var).grid(row=i, column=0, sticky="w", pady=2)
        
        # Right panel - Visualizations
        viz_panel = ttk.Frame(self.root, padding="10")
        viz_panel.grid(row=0, column=1, sticky="nsew")
        
        # Configure grid for visualization area
        viz_panel.grid_rowconfigure(0, weight=1)  # For task queue
        viz_panel.grid_rowconfigure(1, weight=2)  # For energy graph
        viz_panel.grid_rowconfigure(2, weight=2)  # For state graph
        viz_panel.grid_rowconfigure(3, weight=3)  # For log table
        viz_panel.grid_columnconfigure(0, weight=1)
        
        # Task queue display
        queue_frame = ttk.LabelFrame(viz_panel, text="Task Queue", padding="10")
        queue_frame.grid(row=0, column=0, sticky="nsew")
        
        self.queue_text = tk.Text(queue_frame, height=5, wrap=tk.NONE)
        self.queue_text.pack(fill=tk.BOTH, expand=True)
        self.queue_text.config(state=tk.DISABLED)
        
        # Energy graph
        energy_frame = ttk.LabelFrame(viz_panel, text="Energy Consumption", padding="10")
        energy_frame.grid(row=1, column=0, sticky="nsew")
        
        self.energy_fig, self.energy_ax = plt.subplots(figsize=(8, 3))
        self.energy_ax.set_title("Energy Consumption Over Time")
        self.energy_ax.set_xlabel("Time (s)")
        self.energy_ax.set_ylabel("Energy (J)")
        self.energy_line, = self.energy_ax.plot([], [], 'b-')
        self.energy_canvas = FigureCanvasTkAgg(self.energy_fig, energy_frame)
        self.energy_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Power state graph
        state_frame = ttk.LabelFrame(viz_panel, text="Power State Transitions", padding="10")
        state_frame.grid(row=2, column=0, sticky="nsew")
        
        self.state_fig, self.state_ax = plt.subplots(figsize=(8, 2))
        self.state_ax.set_title("CPU Power States")
        self.state_ax.set_yticks([0, 1, 2, 3])
        self.state_ax.set_yticklabels(list(CPUScheduler.POWER_STATES.keys()))
        self.state_line, = self.state_ax.plot([], [], 'ro', markersize=8)
        self.state_canvas = FigureCanvasTkAgg(self.state_fig, state_frame)
        self.state_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Execution log
        log_frame = ttk.LabelFrame(viz_panel, text="Execution Log", padding="10")
        log_frame.grid(row=3, column=0, sticky="nsew")
        
        # Create treeview with scrollbars
        self.log_tree = ttk.Treeview(log_frame, columns=('Time', 'Event', 'Task', 'Details'), show='headings')
        vsb = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_tree.yview)
        hsb = ttk.Scrollbar(log_frame, orient="horizontal", command=self.log_tree.xview)
        self.log_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Configure columns
        self.log_tree.heading('Time', text='Time (s)')
        self.log_tree.heading('Event', text='Event Type')
        self.log_tree.heading('Task', text='Task')
        self.log_tree.heading('Details', text='Details')
        
        self.log_tree.column('Time', width=80, anchor='center')
        self.log_tree.column('Event', width=120, anchor='center')
        self.log_tree.column('Task', width=120, anchor='center')
        self.log_tree.column('Details', width=300, anchor='w')
        
        # Layout
        self.log_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # Configure grid weights
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        
    def add_task(self):
        try:
            name = self.task_name_entry.get()
            priority = int(self.priority_combobox.get())
            burst_time = int(self.burst_time_entry.get())
            deadline = self.deadline_entry.get()
            deadline = int(deadline) if deadline else None
            
            if priority < 1 or priority > 5:
                messagebox.showerror("Error", "Priority must be between 1 and 5")
                return
                
            if burst_time <= 0:
                messagebox.showerror("Error", "Burst time must be positive")
                return
                
            task = Task(name, priority, burst_time, deadline)
            self.scheduler.add_task(task)
            self.update_queue_display()
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
            
    def add_random_tasks(self):
        names = ["Email", "Browser", "Game", "Music", "Video", "Chat", "Update", "Backup"]
        for i in range(5):
            name = f"{random.choice(names)}{i+1}"
            priority = random.randint(1, 5)
            burst_time = random.randint(200, 3000)
            deadline = random.choice([None, random.randint(500, 2000)])
            task = Task(name, priority, burst_time, deadline)
            self.scheduler.add_task(task)
        self.update_queue_display()
        
    def start_simulation(self):
        if not self.simulation_running:
            self.simulation_running = True
            self.simulation_thread = threading.Thread(
                target=self.run_simulation, 
                daemon=True
            )
            self.simulation_thread.start()
            
    def stop_simulation(self):
        self.simulation_running = False
        
    def reset_simulation(self):
        self.stop_simulation()
        self.scheduler = CPUScheduler()
        self.update_queue_display()
        self.clear_log()
        self.update_visualization()
        
    def set_simulation_speed(self, value):
        self.simulation_speed = float(value)
        
    def run_simulation(self):
        while self.simulation_running and (self.scheduler.ready_queue or self.scheduler.current_task):
            self.scheduler.schedule(log_callback=self.add_log_entry)
            self.update_status()
            time.sleep(0.1 / self.simulation_speed)
        
        self.simulation_running = False
        self.update_status()
        
    def update_status(self):
        # Update statistics
        completed = len(self.scheduler.completed_tasks)
        efficiency = completed / self.scheduler.energy_consumed if self.scheduler.energy_consumed > 0 else 0
        battery_pct = (self.scheduler.battery_capacity / 5000) * 100
        
        self.stats_vars['energy'].set(f"Total Energy: {self.scheduler.energy_consumed:.2f} J")
        self.stats_vars['tasks'].set(f"Tasks Completed: {completed}")
        self.stats_vars['violations'].set(f"QoS Violations: {self.scheduler.qos_violations}")
        self.stats_vars['efficiency'].set(f"Efficiency: {efficiency:.2f} tasks/J")
        self.stats_vars['battery'].set(f"Battery: {battery_pct:.1f}%")
        
        # Update current task display
        if self.scheduler.current_task:
            task_info = (
                f"{self.scheduler.current_task.name} "
                f"(P:{self.scheduler.current_task.priority}, "
                f"R:{self.scheduler.current_task.remaining_time}ms)"
            )
        else:
            task_info = "None"
            
        self.update_queue_display()
        
    def update_queue_display(self):
        self.queue_text.config(state=tk.NORMAL)
        self.queue_text.delete(1.0, tk.END)
        
        for i, task in enumerate(self.scheduler.ready_queue):
            deadline_info = f", D:{task.deadline}ms" if task.deadline else ""
            self.queue_text.insert(
                tk.END, 
                f"{i+1}. {task.name} - P:{task.priority}, R:{task.remaining_time}ms{deadline_info}\n"
            )
            
        if self.scheduler.current_task:
            self.queue_text.insert(tk.END, "\n[Current] " + self.scheduler.current_task.name)
            
        self.queue_text.config(state=tk.DISABLED)
        
    def add_log_entry(self, event_type, task_name=None, details=None):
        timestamp = f"{self.scheduler.time:.2f}"
        task_name = task_name or ""
        
        # Color coding
        tags = ()
        if "violation" in event_type.lower():
            tags = ('violation',)
        elif event_type == "Execution":
            tags = ('execution',)
        elif "start" in event_type.lower():
            tags = ('start',)
        elif "complete" in event_type.lower():
            tags = ('complete',)
            
        self.log_tree.insert(
            '', 
            'end', 
            values=(timestamp, event_type, task_name, details),
            tags=tags
        )
        self.log_tree.see(self.log_tree.get_children()[-1])
        
    def clear_log(self):
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)
            
    def update_visualization(self):
        # Update energy graph
        if self.scheduler.time_history:
            self.energy_line.set_data(self.scheduler.time_history, self.scheduler.energy_history)
            self.energy_ax.relim()
            self.energy_ax.autoscale_view()
            
            if self.scheduler.time_history[-1] > 20:
                self.energy_ax.set_xlim(self.scheduler.time_history[-1] - 20, self.scheduler.time_history[-1] + 1)
            else:
                self.energy_ax.set_xlim(0, 20)
                
            self.energy_canvas.draw()
        
        # Update state graph
        if self.scheduler.state_history:
            state_map = {state: i for i, state in enumerate(CPUScheduler.POWER_STATES)}
            y = [state_map[state] for state in self.scheduler.state_history]
            x = range(len(y))
            
            self.state_line.set_data(x, y)
            self.state_ax.relim()
            self.state_ax.autoscale_view()
            self.state_ax.set_xlim(0, len(y)+1)
            self.state_canvas.draw()
        
        if self.window_alive:
            self.root.after(200, self.update_visualization)

if __name__ == "__main__":
    root = tk.Tk()
    app = EnergyAwareSchedulerApp(root)
    
    # Configure tag colors for the log tree
    app.log_tree.tag_configure('violation', background='#ffdddd')
    app.log_tree.tag_configure('execution', background='#ddffdd')
    app.log_tree.tag_configure('start', background='#ddddff')
    app.log_tree.tag_configure('complete', background='#dfffd8')
    modify_app_to_include_export(app)
    root.mainloop()