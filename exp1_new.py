import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import math
from collections import deque

class DrawingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图形绘制与填充")
        
        # 创建画布和 PhotoImage
        self.canvas_width = 800
        self.canvas_height = 600
        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        self.photo = ImageTk.PhotoImage(self.image)
        
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg='white')
        self.canvas.pack(side=tk.BOTTOM)
        self.canvas_image = self.canvas.create_image((0, 0), anchor=tk.NW, image=self.photo)
        
        # 创建控制按钮
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(side=tk.TOP)
        
        tk.Button(self.control_frame, text="直线", command=lambda: self.set_mode("line")).pack(side=tk.LEFT)
        tk.Button(self.control_frame, text="椭圆", command=lambda: self.set_mode("ellipse")).pack(side=tk.LEFT)
        tk.Button(self.control_frame, text="多边形", command=lambda: self.set_mode("polygon")).pack(side=tk.LEFT)
        tk.Button(self.control_frame, text="四联通填充", command=lambda: self.set_fill_mode("flood_fill_four")).pack(side=tk.LEFT)
        tk.Button(self.control_frame, text="清除", command=self.clear_canvas).pack(side=tk.LEFT)
        
        # 初始化变量
        self.mode = "line"
        self.fill_mode = None
        self.points = []
        self.polygon_points = []
        self.drawing = False
        
        # 绑定鼠标事件
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<Motion>", self.on_motion)
        
    def set_mode(self, mode):
        self.mode = mode
        self.fill_mode = None
        self.points = []
        self.polygon_points = []
        self.drawing = False
        print(f"模式切换为: {self.mode}")
        
    def set_fill_mode(self, fill_mode):
        self.fill_mode = fill_mode
        self.mode = "fill"
        print(f"填充模式切换为: {self.fill_mode}")
        
    def clear_canvas(self):
        self.image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas.itemconfig(self.canvas_image, image=self.photo)
        self.points = []
        self.polygon_points = []
        self.drawing = False
        self.fill_mode = None
        self.mode = "line"
        print("画布已清除")
        
    def put_pixel(self, x, y, color=(0, 0, 0)):
        if 0 <= x < self.canvas_width and 0 <= y < self.canvas_height:
            self.image.putpixel((x, y), color)
        
    def update_canvas(self):
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas.itemconfig(self.canvas_image, image=self.photo)
        
    def bresenham_line(self, x1, y1, x2, y2, color=(0, 0, 0)):
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy
        
        x, y = x1, y1
        while True:
            self.put_pixel(x, y, color)
            if x == x2 and y == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        self.update_canvas()
        
    def midpoint_ellipse(self, center_x, center_y, a, b, color=(0, 0, 0)):
        x = 0
        y = b
        
        # Region 1
        d1 = (b * b) - (a * a * b) + (0.25 * a * a)
        dx = 2 * b * b * x
        dy = 2 * a * a * y
        
        while dx < dy:
            self.put_pixel(center_x + x, center_y + y, color)
            self.put_pixel(center_x - x, center_y + y, color)
            self.put_pixel(center_x + x, center_y - y, color)
            self.put_pixel(center_x - x, center_y - y, color)
            
            if d1 < 0:
                x += 1
                dx += 2 * b * b
                d1 += dx + b * b
            else:
                x += 1
                y -= 1
                dx += 2 * b * b
                dy -= 2 * a * a
                d1 += dx - dy + b * b
        
        # Region 2
        d2 = ((b * b) * ((x + 0.5) * (x + 0.5))) + \
             ((a * a) * ((y - 1) * (y - 1))) - \
             (a * a * b * b)
             
        while y >= 0:
            self.put_pixel(center_x + x, center_y + y, color)
            self.put_pixel(center_x - x, center_y + y, color)
            self.put_pixel(center_x + x, center_y - y, color)
            self.put_pixel(center_x - x, center_y - y, color)
            
            if d2 > 0:
                y -= 1
                dy -= 2 * a * a
                d2 += a * a - dy
            else:
                y -= 1
                x += 1
                dx += 2 * b * b
                dy -= 2 * a * a
                d2 += dx - dy + a * a
        self.update_canvas()
        
    def scan_line_fill(self, points, fill_color=(255, 0, 0)):
        if len(points) < 3:
            messagebox.showerror("错误", "多边形至少需要三个点")
            return
            
        # 找到多边形的边界
        min_y = min(p[1] for p in points)
        max_y = max(p[1] for p in points)
        
        # 对每一条扫描线
        for y in range(int(min_y), int(max_y) + 1):
            intersections = []
            
            # 计算扫描线与多边形边的交点
            for i in range(len(points)):
                j = (i + 1) % len(points)
                y1, y2 = points[i][1], points[j][1]
                if min(y1, y2) <= y <= max(y1, y2):
                    if y1 != y2:
                        x = points[i][0] + (points[j][0] - points[i][0]) * (y - y1) / (y2 - y1)
                        intersections.append(x)
            
            # 对交点进行排序
            intersections.sort()
            
            # 两两配对填充
            for i in range(0, len(intersections), 2):
                if i + 1 < len(intersections):
                    x_start = int(math.ceil(intersections[i]))
                    x_end = int(math.floor(intersections[i+1]))
                    for x in range(x_start, x_end + 1):
                        self.put_pixel(x, y, fill_color)
        self.update_canvas()
    
    def flood_fill_four_connected(self, x, y, fill_color=(255, 0, 0), boundary_color=(0, 0, 0)):
        # 获取目标颜色
        target_pixel = self.get_pixel_color(x, y)
        if target_pixel == fill_color or target_pixel == boundary_color:
            return
        
        # 使用队列实现迭代式的四联通漫水填充
        queue = deque()
        queue.append((x, y))
        while queue:
            current_x, current_y = queue.popleft()
            if 0 <= current_x < self.canvas_width and 0 <= current_y < self.canvas_height:
                current_color = self.get_pixel_color(current_x, current_y)
                if current_color == target_pixel and current_color != boundary_color:
                    self.put_pixel(current_x, current_y, fill_color)
                    queue.append((current_x + 1, current_y))
                    queue.append((current_x - 1, current_y))
                    queue.append((current_x, current_y + 1))
                    queue.append((current_x, current_y - 1))
        self.update_canvas()
        
    def get_pixel_color(self, x, y):
        # 获取指定像素的颜色
        return self.image.getpixel((x, y))
    
    def on_click(self, event):
        if self.mode == "line":
            self.points.append((event.x, event.y))
            if len(self.points) == 2:
                self.bresenham_line(int(self.points[0][0]), int(self.points[0][1]),
                                  int(self.points[1][0]), int(self.points[1][1]))
                self.points = []
                
        elif self.mode == "ellipse":
            self.points.append((event.x, event.y))
            if len(self.points) == 2:
                center_x = self.points[0][0]
                center_y = self.points[0][1]
                dx = abs(self.points[1][0] - center_x)
                dy = abs(self.points[1][1] - center_y)
                self.midpoint_ellipse(int(center_x), int(center_y), int(dx), int(dy))
                self.points = []
                
        elif self.mode == "polygon":
            self.polygon_points.append((event.x, event.y))
            if len(self.polygon_points) > 1:
                self.bresenham_line(int(self.polygon_points[-2][0]), int(self.polygon_points[-2][1]),
                                  int(self.polygon_points[-1][0]), int(self.polygon_points[-1][1]))
        
        elif self.mode == "fill":
            if self.fill_mode == "flood_fill_four":
                if len(self.polygon_points) > 2:
                    # 提示用户点击填充点
                    messagebox.showinfo("提示", "请点击多边形内部的一个点进行四联通填充")
                    # 绑定填充点点击事件
                    self.canvas.bind("<Button-1>", lambda e: self.perform_flood_fill(e, mode="four"))
                else:
                    messagebox.showerror("错误", "多边形至少需要三个点进行填充")
    
    def perform_flood_fill(self, event, mode="four"):
        x, y = event.x, event.y
        boundary_color = (0, 0, 0)  # 假设边界颜色为黑色
        fill_color = (255, 0, 0)    # 填充颜色为红色
        if mode == "four":
            self.flood_fill_four_connected(x, y, fill_color=fill_color, boundary_color=boundary_color)
            messagebox.showinfo("完成", "四联通填充完成")
        # 重新绑定鼠标事件
        self.canvas.bind("<Button-1>", self.on_click)
        
    def on_right_click(self, event):
        if self.mode == "polygon" and len(self.polygon_points) > 2:
            self.bresenham_line(int(self.polygon_points[-1][0]), int(self.polygon_points[-1][1]),
                              int(self.polygon_points[0][0]), int(self.polygon_points[0][1]))
            self.drawing = True
    
    def on_motion(self, event):
        pass
    
    def fill_polygon(self):
        if self.mode == "fill" and self.fill_mode == "flood_fill_four":
            if len(self.polygon_points) > 2:
                # 提示用户点击填充点
                messagebox.showinfo("提示", "请点击多边形内部的一个点进行四联通填充")
                # 绑定填充点点击事件
                self.canvas.bind("<Button-1>", lambda e: self.perform_flood_fill(e, mode="four"))
            else:
                messagebox.showerror("错误", "多边形至少需要三个点进行填充")
        else:
            messagebox.showerror("错误", "请选择一个填充模式并绘制多边形")

def main():
    root = tk.Tk()
    app = DrawingApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
