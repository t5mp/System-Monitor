from tkinter import *
from tkinter import ttk
import psutil
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation

# Setup window
root = Tk()
root.geometry("1200x800")
root.title("System Monitor")
root.configure(bg="#f0f0f0")  

# Create pages
main_page = Frame(root, bg="#f0f0f0")
dashboard_page = Frame(root, bg="#f0f0f0")
proc_page = Frame(root, bg="#f0f0f0")

for page in (main_page, dashboard_page, proc_page):
    page.grid(row=0, column=0, sticky='nsew')

def show_main(): main_page.tkraise()
def show_dashboard(): dashboard_page.tkraise()
def show_proc(): proc_page.tkraise()

def mod_button(master, text, command):
    return Button(
        master, text=text, font=("Segoe UI", 12), fg="#333", bg="#e0e0e0",
        activebackground="#c0c0c0", activeforeground="#000", relief=FLAT,
        highlightthickness=0, bd=0, padx=10, pady=5, command=command
    )

# Main page
Label(main_page, text="System Monitor", font=("Segoe UI", 22, "bold"), fg="#222", bg="#f0f0f0").pack(pady=30)

for text, cmd in [("Dashboard", show_dashboard), ("Processes", show_proc), ("Quit", root.destroy)]:
    mod_button(main_page, text, cmd).pack(pady=10)

# Chart builder
def build_chart(frame, row, column, label_text, data_deque, fetch_func, color='blue', max_val=100, unit='%'):
    fig, ax = plt.subplots(figsize=(4, 2.5), facecolor='#f0f0f0')
    fig.subplots_adjust(left=0.1, right=0.98, top=0.85, bottom=0.2)
    ax.set_facecolor('#f0f0f0')

    line, = ax.plot(range(60), data_deque, color=color, linewidth=2)
    ax.set_ylim(0, max_val)
    ax.set_xticks([])
    ax.set_yticks([0, max_val//2, max_val])
    ax.set_yticklabels([f"0{unit}", f"{max_val//2}{unit}", f"{max_val}{unit}"], color="#333", fontname="Segoe UI", fontsize=8)
    ax.set_title(label_text, color="#333", fontname="Segoe UI", fontsize=12, pad=10)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.grid(False)

    percent_label = Label(frame, text=f"0{unit}", font=("Segoe UI", 14), fg=color, bg="#f0f0f0")
    percent_label.grid(row=row*2, column=column, pady=(10, 0))

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().grid(row=row*2+1, column=column, padx=10, pady=(0, 20))
    canvas.get_tk_widget().configure(bg='#f0f0f0', highlightthickness=0)

    def update_graph(frame):
        val = fetch_func()
        data_deque.append(val)
        line.set_ydata(data_deque)
        percent_label.config(text=f"{val:.1f}{unit}")
        return line,

    return animation.FuncAnimation(fig, update_graph, interval=1000, blit=True)

# Dashboard layout
dashboard_page.columnconfigure([0, 1, 2], weight=1)

cpu_data = deque([0]*60, maxlen=60)
ani_cpu = build_chart(dashboard_page, 0, 0, "CPU Usage", cpu_data, lambda: psutil.cpu_percent(interval=None), 'royalblue')

mem_data = deque([0]*60, maxlen=60)
ani_mem = build_chart(dashboard_page, 0, 1, "Memory Usage", mem_data, lambda: psutil.virtual_memory().percent, 'mediumseagreen')

disk_data = deque([0]*60, maxlen=60)
ani_disk = build_chart(dashboard_page, 0, 2, "Disk Usage", disk_data, lambda: psutil.disk_usage('/').percent, 'darkorange')

# Network graph
net_sent = deque([0]*60, maxlen=60)
net_recv = deque([0]*60, maxlen=60)
last_net = psutil.net_io_counters()

fig_net, ax_net = plt.subplots(figsize=(8, 2.5), facecolor='#f0f0f0')
fig_net.subplots_adjust(left=0.1, right=0.98, top=0.85, bottom=0.2)
ax_net.set_facecolor('#f0f0f0')

line_sent, = ax_net.plot(range(60), net_sent, color='tomato', linewidth=2, label="Upload")
line_recv, = ax_net.plot(range(60), net_recv, color='limegreen', linewidth=2, label="Download")
ax_net.set_ylim(0, 100)
ax_net.set_xticks([])
ax_net.set_yticks([0, 50, 100])
ax_net.set_yticklabels(["0KB/s", "50KB/s", "100KB/s"], color="#333", fontname="Segoe UI", fontsize=8)
ax_net.set_title("Network I/O", color="#333", fontname="Segoe UI", fontsize=12, pad=10)
for spine in ax_net.spines.values():
    spine.set_visible(False)
ax_net.grid(False)
ax_net.legend(loc="upper right", fontsize=8, facecolor="#f0f0f0", edgecolor="#f0f0f0", labelcolor="#333")

canvas_net = FigureCanvasTkAgg(fig_net, master=dashboard_page)
canvas_net.get_tk_widget().grid(row=2, column=0, columnspan=3, pady=10)
canvas_net.get_tk_widget().configure(bg='#f0f0f0', highlightthickness=0)

def update_net_graph(frame):
    global last_net
    net = psutil.net_io_counters()
    up = (net.bytes_sent - last_net.bytes_sent) / 1024
    down = (net.bytes_recv - last_net.bytes_recv) / 1024
    last_net = net
    net_sent.append(up)
    net_recv.append(down)
    max_val = max(max(net_sent), max(net_recv), 100)
    ax_net.set_ylim(0, max_val + 20)
    ax_net.set_yticks([0, max_val/2, max_val])
    ax_net.set_yticklabels([f"{int(0)}KB/s", f"{int(max_val/2)}KB/s", f"{int(max_val)}KB/s"],
                           color="#333", fontname="Segoe UI", fontsize=8)
    line_sent.set_ydata(net_sent)
    line_recv.set_ydata(net_recv)
    return line_sent, line_recv

ani_net = animation.FuncAnimation(fig_net, update_net_graph, interval=1000, blit=True)

# Process monitor page
Label(proc_page, text="Process Monitor", font=("Segoe UI", 16, "bold"), fg="#333", bg="#f0f0f0").pack(pady=10)

cols = ("PID", "Name", "CPU %", "Memory %")
tree = ttk.Treeview(proc_page, columns=cols, show="headings", height=20)
for c in cols:
    tree.heading(c, text=c)
    tree.column(c, anchor=CENTER, width=150)
tree.pack(fill=BOTH, expand=True, padx=20, pady=10)
tree.tag_configure('suspicious', foreground='red')

# Possivble Viruses
SUSPICIOUS = {"hacktool", "malware", "ransomware", "keylogger", "virus", "badprocess", "exploit", "coinminer"}

def update_process_list():
    for iid in tree.get_children():
        tree.delete(iid)
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            nm = (p.info['name'] or "").lower()
            vals = (
                p.info['pid'],
                p.info['name'],
                f"{p.info['cpu_percent']:.1f}",
                f"{p.info['memory_percent']:.1f}"
            )
            if any(term in nm for term in SUSPICIOUS):
                tree.insert("", "end", values=vals, tags=('suspicious',))
            else:
                tree.insert("", "end", values=vals)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    proc_page.after(3000, update_process_list)

update_process_list()


mod_button(dashboard_page, "Back", show_main).grid(row=6, column=1, pady=10)
mod_button(proc_page, "Back", show_main).pack(pady=10)


show_main()
root.mainloop()
