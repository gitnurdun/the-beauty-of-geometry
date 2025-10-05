import tkinter as tk
from tkinter import ttk
import random
import math
import time

class Particle:
    def __init__(self, canvas, width, height, swarm_id):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.size = 3
        self.x = random.randint(0, width)
        self.y = random.randint(0, height)
        self.speed = random.uniform(0.5, 2.0)
        self.angle = random.uniform(0, 2 * math.pi)
        self.swarm_id = swarm_id
        self.color = self.get_swarm_color(swarm_id)
        self.id = canvas.create_oval(
            self.x - self.size, self.y - self.size,
            self.x + self.size, self.y + self.size,
            fill=self.color, outline=""
        )
        self.links = []
        
    def get_swarm_color(self, swarm_id):
        """为不同的粒子群分配不同的颜色"""
        colors = ["#FF6060", "#60FF60", "#6060FF", "#FF60FF", "#60FFFF", "#FFB060", "#B060FF"]
        return colors[swarm_id % len(colors)]
        
    def move(self, mouse_x, mouse_y, cursor_sensitivity, particle_speed):
        # 随机运动
        self.angle += random.uniform(-0.2, 0.2)
        
        # 向光标位置移动的趋势
        dx = mouse_x - self.x
        dy = mouse_y - self.y
        dist = max(1, math.sqrt(dx*dx + dy*dy))
        
        # 吸引力随距离增加而减小，并受灵敏度控制
        attraction = min(1.0, cursor_sensitivity * 100.0 / dist)
        self.angle = math.atan2(
            math.sin(self.angle) * (1 - attraction) + dy/dist * attraction,
            math.cos(self.angle) * (1 - attraction) + dx/dist * attraction
        )
        
        # 应用粒子速度因子
        speed_factor = particle_speed * self.speed
        
        # 更新位置
        self.x += math.cos(self.angle) * speed_factor
        self.y += math.sin(self.angle) * speed_factor
        
        # 边界处理
        if self.x < 0: self.x = self.width
        if self.x > self.width: self.x = 0
        if self.y < 0: self.y = self.height
        if self.y > self.height: self.y = 0
        
        # 更新画布上的位置
        self.canvas.coords(
            self.id,
            self.x - self.size, self.y - self.size,
            self.x + self.size, self.y + self.size
        )

class ParticleAnimation:
    def __init__(self, root, width=800, height=600):
        self.root = root
        self.width = width
        self.height = height
        self.mouse_x = width // 2
        self.mouse_y = height // 2
        self.start_time = time.time()
        
        # 默认参数
        self.cursor_sensitivity = 0.8  # 默认值提高
        self.particle_density = 50
        self.swarm_density = 3
        self.link_distance = 150
        self.particle_speed = 1.0  # 粒子速度因子
        
        # 创建画布
        self.canvas = tk.Canvas(root, width=width, height=height, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 创建控制面板（在画布上）
        self.control_frame = tk.Frame(self.canvas, bg="#202020", bd=0, highlightthickness=0)
        self.control_frame.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
        
        # 创建滑块
        self.create_sliders()
        
        # 创建粒子群
        self.swarms = []
        self.create_swarms()
        
        # 绑定鼠标移动事件
        self.canvas.bind("<Motion>", self.on_mouse_move)
        
        # 开始动画
        self.animate()
        
    def create_sliders(self):
        """创建美化后的控制滑块"""
        # 标题
        title_label = tk.Label(
            self.control_frame, 
            text="粒子群控制面板", 
            fg="white", 
            bg="#202020",
            font=("Arial", 10, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # 光标敏感度滑块
        sensitivity_label = tk.Label(
            self.control_frame, 
            text="光标敏感度:", 
            fg="white", 
            bg="#202020"
        )
        sensitivity_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.sensitivity_slider = ttk.Scale(
            self.control_frame, 
            from_=0.1, 
            to=2.0,  # 范围扩大到2.0
            value=self.cursor_sensitivity,
            length=150,
            command=lambda v: setattr(self, 'cursor_sensitivity', float(v))
        )
        self.sensitivity_slider.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 粒子密度滑块
        particle_label = tk.Label(
            self.control_frame, 
            text="粒子密度:", 
            fg="white", 
            bg="#202020"
        )
        particle_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.particle_slider = ttk.Scale(
            self.control_frame, 
            from_=20, 
            to=200, 
            value=self.particle_density,
            length=150,
            command=lambda v: self.update_particle_count(int(float(v)))
        )
        self.particle_slider.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 形状密度滑块
        swarm_label = tk.Label(
            self.control_frame, 
            text="形状密度:", 
            fg="white", 
            bg="#202020"
        )
        swarm_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.swarm_slider = ttk.Scale(
            self.control_frame, 
            from_=1, 
            to=10, 
            value=self.swarm_density,
            length=150,
            command=lambda v: self.update_swarm_count(int(float(v)))
        )
        self.swarm_slider.grid(row=3, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 连线距离滑块
        link_label = tk.Label(
            self.control_frame, 
            text="连线距离:", 
            fg="white", 
            bg="#202020"
        )
        link_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.link_slider = ttk.Scale(
            self.control_frame, 
            from_=50, 
            to=300, 
            value=self.link_distance,
            length=150,
            command=lambda v: setattr(self, 'link_distance', float(v))
        )
        self.link_slider.grid(row=4, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 粒子速度滑块
        speed_label = tk.Label(
            self.control_frame, 
            text="粒子速度:", 
            fg="white", 
            bg="#202020"
        )
        speed_label.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        self.speed_slider = ttk.Scale(
            self.control_frame, 
            from_=0.2, 
            to=3.0, 
            value=self.particle_speed,
            length=150,
            command=lambda v: setattr(self, 'particle_speed', float(v))
        )
        self.speed_slider.grid(row=5, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # 配置列权重，使滑块可以拉伸
        self.control_frame.columnconfigure(1, weight=1)
        
        # 美化滑块样式
        style = ttk.Style()
        style.configure("TScale", background="#303030", troughcolor="#404040")
        
    def create_swarms(self):
        """创建多个粒子群"""
        self.swarms = []
        particles_per_swarm = max(1, self.particle_density // self.swarm_density)
        
        for i in range(self.swarm_density):
            swarm = []
            for _ in range(particles_per_swarm):
                particle = Particle(self.canvas, self.width, self.height, i)
                swarm.append(particle)
            self.swarms.append(swarm)
    
    def update_particle_count(self, new_density):
        """更新粒子密度"""
        self.particle_density = new_density
        self.reset_swarms()
    
    def update_swarm_count(self, new_density):
        """更新形状密度"""
        self.swarm_density = new_density
        self.reset_swarms()
    
    def reset_swarms(self):
        """重置所有粒子群"""
        # 清除所有粒子和连线
        for swarm in self.swarms:
            for particle in swarm:
                self.canvas.delete(particle.id)
                for link in particle.links:
                    self.canvas.delete(link)
        
        # 创建新的粒子群
        self.create_swarms()
    
    def on_mouse_move(self, event):
        self.mouse_x = event.x
        self.mouse_y = event.y
        
    def animate(self):
        # 清除所有连线
        for swarm in self.swarms:
            for particle in swarm:
                for link in particle.links:
                    self.canvas.delete(link)
                particle.links = []
        
        # 移动粒子并创建新连线
        for swarm in self.swarms:
            for i, particle in enumerate(swarm):
                particle.move(self.mouse_x, self.mouse_y, self.cursor_sensitivity, self.particle_speed)
                
                # 创建粒子间的连线（只在同一群内）
                for other in swarm[i+1:]:
                    dx = particle.x - other.x
                    dy = particle.y - other.y
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    # 只连接近距离的粒子
                    if distance < self.link_distance:
                        # 计算随时间变化的透明度
                        time_elapsed = time.time() - self.start_time
                        opacity = 0.3 + 0.2 * math.sin(time_elapsed + distance/50)
                        
                        # 创建带透明度的连线
                        color = self.get_color_with_opacity(particle.color, opacity)
                        link = self.canvas.create_line(
                            particle.x, particle.y, other.x, other.y,
                            fill=color, width=1
                        )
                        particle.links.append(link)
                        other.links.append(link)
        
        # 继续动画循环
        self.root.after(30, self.animate)
    
    def get_color_with_opacity(self, base_color, opacity):
        """将十六进制颜色转换为带透明度的格式"""
        r = int(base_color[1:3], 16)
        g = int(base_color[3:5], 16)
        b = int(base_color[5:7], 16)
        return f"#{int(r*opacity):02x}{int(g*opacity):02x}{int(b*opacity):02x}"

if __name__ == "__main__":
    root = tk.Tk()
    root.title("增强型粒子群聚动画")
    app = ParticleAnimation(root)
    root.mainloop()
