
import tkinter as tk
from tkinter import ttk, messagebox
import random
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
