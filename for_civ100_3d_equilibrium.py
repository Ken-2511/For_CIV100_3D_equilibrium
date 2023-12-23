import tkinter as tk
import numpy as np
from math import *
import os
import json

root = tk.Tk()
root.title("For CIV 100 3D Equilibrium")


# 定义一个 unknown force 的框架
class UnknownForce(tk.LabelFrame):
    def __init__(self, master, f_name):
        super().__init__(master, text=f_name)
        self.activated = True
        self.name = f_name
        self.magnitude = 0
        self.tail = np.zeros(3)
        self.vector = np.zeros(3)
        self.unit_vector = np.zeros(3)
        self.moment_coefficient = np.zeros(3)
        width = 10
        ### about GUI ###
        tk.Label(self, text="Magnitude:").grid(row=0, column=0)
        self.magnitude_entry = tk.Entry(self, width=width, state="readonly")
        self.magnitude_entry.grid(row=0, column=1)
        tk.Label(self, text="Name:").grid(row=0, column=2)
        self.name_entry = tk.Entry(self, width=width)
        self.name_entry.grid(row=0, column=3)
        self.name_entry.bind("<FocusOut>", self.update_value)
        # vector
        tk.Label(self, text="Vector:").grid(row=1, column=0)
        self.vector_entry = [tk.Entry(self, width=width) for _ in range(3)]
        for i, entry in enumerate(self.vector_entry, 1):
            entry.grid(row=1, column=i, padx=5)
            entry.bind("<FocusOut>", self.update_value)
        # tail
        tk.Label(self, text="Tail (start point):").grid(row=2, column=0)
        self.tail_entry = [tk.Entry(self, width=width) for _ in range(3)]
        for i, entry in enumerate(self.tail_entry, 1):
            entry.grid(row=2, column=i, padx=5)
            entry.bind("<FocusOut>", self.update_value)
        # unit vector
        tk.Label(self, text="Unit Vector:").grid(row=3, column=0)
        self.unit_vector_entry = [tk.Entry(self, width=width, state="readonly") for _ in range(3)]
        for i, entry in enumerate(self.unit_vector_entry, 1):
            entry.grid(row=3, column=i, padx=5)
        # moment coefficient
        # tk.Label(self, text="Moment Coefficient:").grid(row=4, column=0)
        # self.moment_coefficient_entry = [tk.Entry(self, width=width, state="readonly") for _ in range(3)]
        # for i, entry in enumerate(self.moment_coefficient_entry, 1):
        #     entry.grid(row=4, column=i, padx=5)
        # update the values in the entries
        self.update_entry(True, name=True)
        self.update_value()
        self.update_entry()

    def deactivate(self):
        self.name = ""
        self.magnitude = 0
        self.tail = np.zeros(3)
        self.vector = np.zeros(3)
        self.unit_vector = np.zeros(3)
        self.moment_coefficient = np.zeros(3)
        self.update_entry(True, True, True)
        self.name_entry.config(state="readonly")
        for i in range(3):
            self.tail_entry[i].config(state="readonly")
        self.activated = False

    def activate(self):
        self.name_entry.config(state="normal")
        for i in range(3):
            self.tail_entry[i].config(state="normal")
        self.activated = True

    def import_from_dic(self, dic):
        # load history from a dictionary
        self.name = dic["name"]
        self.magnitude = np.array(dic["magnitude"], dtype=np.float64)
        self.tail = np.array(dic["tail"], dtype=np.float64)
        self.vector = np.array(dic["vector"], dtype=np.float64)
        self.unit_vector = np.array(dic["unit_vector"], dtype=np.float64)
        self.moment_coefficient = np.array(dic["moment_coefficient"], dtype=np.float64)
        if sum(np.square(self.vector)) == 0:
            self.deactivate()
        else:
            self.activate()
        self.update_entry(True, True, True)

    def export_to_dic(self):
        # form a dictionary which contains its information
        dic = {
            "name": self.name,
            "magnitude": float(self.magnitude),
            "tail": list(self.tail),
            "vector": list(self.vector),
            "unit_vector": list(self.unit_vector),
            "moment_coefficient": list(self.moment_coefficient)
        }
        return dic

    def update_entry(self, tail_and_vector=False, magnitude=False, name=False):
        for i in range(3):
            if tail_and_vector:
                self.tail_entry[i].delete(0, tk.END)
                self.tail_entry[i].insert(0, str(self.tail[i]))
                self.vector_entry[i].delete(0, tk.END)
                self.vector_entry[i].insert(0, str(self.vector[i]))
            self.unit_vector_entry[i].config(state="normal")
            self.unit_vector_entry[i].delete(0, tk.END)
            self.unit_vector_entry[i].insert(0, str(self.unit_vector[i]))
            self.unit_vector_entry[i].config(state="readonly")
            # self.moment_coefficient_entry[i].config(state="normal")
            # self.moment_coefficient_entry[i].delete(0, tk.END)
            # self.moment_coefficient_entry[i].insert(0, str(self.moment_coefficient[i]))
            # self.moment_coefficient_entry[i].config(state="readonly")
        if magnitude:
            self.magnitude_entry.config(state="normal")
            self.magnitude_entry.delete(0, tk.END)
            self.magnitude_entry.insert(0, str(self.magnitude))
            self.magnitude_entry.config(state="readonly")
        if name:
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, self.name)

    def update_value(self, *args):
        # 先检测vector是否是零向量，如果是零向量的话就deactivate，反之activate
        # 如果并没有activate，那就不要继续算了
        for i in range(3):
            self.vector[i] = eval(self.vector_entry[i].get())
        if sum(np.square(self.vector)) == 0:
            if self.activated:
                self.deactivate()
            return
        if not self.activated:
            self.activate()
        for i in range(3):
            self.tail[i] = eval(self.tail_entry[i].get())
        self.unit_vector = self.vector / np.sqrt(sum(np.square(self.vector)))
        moment_arm = self.tail - moment_frame.moment_reference_point
        # noinspection PyUnreachableCode
        self.moment_coefficient = np.cross(moment_arm, self.unit_vector)
        self.name = self.name_entry.get()
        self.update_entry()


class KnownForce(tk.LabelFrame):
    def __init__(self, master, f_name):
        super().__init__(master, text=f_name)
        self.activated = True
        self.name = f_name
        self.magnitude = 0
        self.tail = np.zeros(3)
        self.vector = np.zeros(3)
        self.unit_vector = np.zeros(3)
        self.moment_coefficient = np.zeros(3)
        width = 10
        ### about GUI ###
        tk.Label(self, text="Magnitude:").grid(row=0, column=0)
        self.magnitude_entry = tk.Entry(self, width=width)
        self.magnitude_entry.grid(row=0, column=1)
        self.magnitude_entry.bind("<FocusOut>", self.update_value)
        tk.Label(self, text="Name:").grid(row=0, column=2)
        self.name_entry = tk.Entry(self, width=width)
        self.name_entry.grid(row=0, column=3)
        self.name_entry.bind("<FocusOut>", self.update_value)
        # vector
        tk.Label(self, text="Vector:").grid(row=1, column=0)
        self.vector_entry = [tk.Entry(self, width=width) for _ in range(3)]
        for i, entry in enumerate(self.vector_entry, 1):
            entry.grid(row=1, column=i, padx=5)
            entry.bind("<FocusOut>", self.update_value)
        # tail
        tk.Label(self, text="Tail (start point):").grid(row=2, column=0)
        self.tail_entry = [tk.Entry(self, width=width) for _ in range(3)]
        for i, entry in enumerate(self.tail_entry, 1):
            entry.grid(row=2, column=i, padx=5)
            entry.bind("<FocusOut>", self.update_value)
        # unit vector
        tk.Label(self, text="Unit Vector:").grid(row=3, column=0)
        self.unit_vector_entry = [tk.Entry(self, width=width, state="readonly") for _ in range(3)]
        for i, entry in enumerate(self.unit_vector_entry, 1):
            entry.grid(row=3, column=i, padx=5)
        # moment coefficient
        # tk.Label(self, text="Moment Coefficient:").grid(row=4, column=0)
        # self.moment_coefficient_entry = [tk.Entry(self, width=width, state="readonly") for _ in range(3)]
        # for i, entry in enumerate(self.moment_coefficient_entry, 1):
        #     entry.grid(row=4, column=i, padx=5)
        # update the values in the entries
        self.update_entry(True, True)
        self.update_value()
        self.update_entry()

    def deactivate(self):
        self.name = ""
        self.magnitude = 0
        self.tail = np.zeros(3)
        self.vector = np.zeros(3)
        self.unit_vector = np.zeros(3)
        self.moment_coefficient = np.zeros(3)
        self.update_entry(True, True)
        self.name_entry.config(state="readonly")
        for i in range(3):
            self.tail_entry[i].config(state="readonly")
        self.activated = False

    def activate(self):
        self.name_entry.config(state="normal")
        for i in range(3):
            self.tail_entry[i].config(state="normal")
        self.activated = True

    def import_from_dic(self, dic):
        # load history from a dictionary
        self.name = dic["name"]
        self.magnitude = np.array(dic["magnitude"], dtype=np.float64)
        self.tail = np.array(dic["tail"], dtype=np.float64)
        self.vector = np.array(dic["vector"], dtype=np.float64)
        self.unit_vector = np.array(dic["unit_vector"], dtype=np.float64)
        self.moment_coefficient = np.array(dic["moment_coefficient"], dtype=np.float64)
        if sum(np.square(self.vector)) == 0:
            self.deactivate()
        else:
            self.activate()
        self.update_entry(True, True)

    def export_to_dic(self):
        # form a dictionary which contains its information
        dic = {
            "name": self.name,
            "magnitude": float(self.magnitude),
            "tail": list(self.tail),
            "vector": list(self.vector),
            "unit_vector": list(self.unit_vector),
            "moment_coefficient": list(self.moment_coefficient)
        }
        return dic

    def update_entry(self, tail_and_vector=False, name=False):
        for i in range(3):
            if tail_and_vector:
                self.tail_entry[i].delete(0, tk.END)
                self.tail_entry[i].insert(0, str(self.tail[i]))
                self.vector_entry[i].delete(0, tk.END)
                self.vector_entry[i].insert(0, str(self.vector[i]))
            self.unit_vector_entry[i].config(state="normal")
            self.unit_vector_entry[i].delete(0, tk.END)
            self.unit_vector_entry[i].insert(0, str(self.unit_vector[i]))
            self.unit_vector_entry[i].config(state="readonly")
            # self.moment_coefficient_entry[i].config(state="normal")
            # self.moment_coefficient_entry[i].delete(0, tk.END)
            # self.moment_coefficient_entry[i].insert(0, str(self.moment_coefficient[i]))
            # self.moment_coefficient_entry[i].config(state="readonly")
        if tail_and_vector:
            self.magnitude_entry.delete(0, tk.END)
            self.magnitude_entry.insert(0, str(self.magnitude))
        if name:
            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, self.name)

    def update_value(self, *args):
        # 先检测vector是否是零向量，如果是零向量的话就deactivate，反之activate
        # 如果并没有activate，那就不要继续算了
        for i in range(3):
            self.vector[i] = eval(self.vector_entry[i].get())
        if sum(np.square(self.vector)) == 0:
            if self.activated:
                self.deactivate()
            return
        if not self.activated:
            self.activate()
        for i in range(3):
            self.tail[i] = eval(self.tail_entry[i].get())
        self.magnitude = eval(self.magnitude_entry.get())
        self.unit_vector = self.vector / np.sqrt(sum(np.square(self.vector)))
        moment_arm = self.tail - moment_frame.moment_reference_point
        # noinspection PyUnreachableCode
        self.moment_coefficient = np.cross(moment_arm, self.unit_vector)
        self.name = self.name_entry.get()
        self.update_entry()


class MomentFrame(tk.LabelFrame):
    def __init__(self, master):
        self.moment_reference_point = np.zeros(3)
        super().__init__(master, text="Moment Reference Point")
        tk.Label(self, text="Calculate Moment at Point:").grid(row=0, column=0)
        self.moment_entry = [tk.Entry(self, width=5) for _ in range(3)]
        for i, entry in enumerate(self.moment_entry, 1):
            entry.bind("<FocusOut>", self.update_value)
            entry.insert(0, self.moment_reference_point[i-1])
            entry.grid(row=0, column=i, padx=5, pady=0)
        self.grid(row=0, column=0, padx=10, pady=0, ipadx=5, ipady=5, sticky=tk.W)

    def update_value(self, *args):
        for i in range(3):
            self.moment_reference_point[i] = eval(self.moment_entry[i].get())
        for f in unknown_forces:
            f.update_value()
            f.update_entry()
        for f in known_forces:
            f.update_value()
            f.update_entry()

    def import_from_list(self, li):
        for i in range(3):
            self.moment_reference_point[i] = li[i]
            self.moment_entry[i].delete(0, tk.END)
            self.moment_entry[i].insert(0, str(self.moment_reference_point[i]))

    def export_to_list(self):
        li = list(self.moment_reference_point)
        return li


class CalculateFrame(tk.LabelFrame):
    def __init__(self, master):
        super().__init__(master, text="Calculate Result Here")
        tk.Button(self, text="calculate & update the result!", command=self.calculate_result).grid(row=0, column=0, padx=5, pady=0)
        self.grid(row=0, column=1, padx=10, pady=0, ipadx=5, ipady=5, sticky=tk.W)

    def calculate_result(self, *args):
        # update all values
        moment_frame.update_value()

        ### calculate the sum of known force ###
        force = np.zeros(3)
        for f in known_forces:
            force[:] += f.magnitude * f.unit_vector
        # calculate the sum of known moment
        moment = np.zeros(3)
        for f in known_forces:
            moment[:] += f.moment_coefficient * f.magnitude
        # form the "b" vector
        b = np.concatenate((force, moment), 0).reshape(-1, 1)
        b[:] *= -1

        ### form the coefficient matrix ###
        # firstly see how many activated unknowns
        activated_unknowns = []
        for i, f in enumerate(unknown_forces):
            if f.activated:
                activated_unknowns.append(i)
        num_unknowns = sum([int(f.activated) for f in unknown_forces])

        A = np.zeros((6, num_unknowns))
        for i, j in enumerate(activated_unknowns):
            f = unknown_forces[j]
            A[:3, i] = f.unit_vector
            A[3:, i] = f.moment_coefficient

        ### eliminate the zero rows ###
        for i in range(5, -1, -1):
            if sum(np.square(A[i])) + sum(np.square(b[i])) == 0:
                A = np.concatenate((A[:i], A[i+1:]), 0)
                b = np.concatenate((b[:i], b[i+1:]), 0)

        ### solve the matrix! ###
        print("solve this matrix:")
        np.set_printoptions(precision=4, linewidth=100)
        print(np.concatenate((A, b), 1))
        # check if solvable
        assert not A.shape[-2] < A.shape[-1], "未知量大于等式数量，方程可能有很多解"
        assert not A.shape[-2] > A.shape[-1], "未知量小于等式数量，方程可能无解"
        # solve
        answer = np.linalg.solve(A, b)
        print("answer:")
        print(answer)
        answer = answer.reshape(-1)
        default_color = unknown_forces[0].magnitude_entry.cget("bg")
        for i in activated_unknowns:
            f = unknown_forces[i]
            f.magnitude = answer[i]
            f.update_entry(False, True)
            # highlight the result
            f.magnitude_entry.config(state="normal", bg="#FFFF00")
        self.after(1000, self.change_all_mag_entry_bg, default_color)

    def change_all_mag_entry_bg(self, color):
        for f in unknown_forces:
            f.magnitude_entry.config(state="readonly", bg=color)


if __name__ == '__main__':
    # for the top-left frame
    moment_frame = MomentFrame(root)

    # for the top-right frame
    CalculateFrame(root)

    # for the known forces and unknown forces
    unknown_forces = []
    known_forces = []
    for i in range(6):
        force = UnknownForce(root, f"Unknown{i+1}")
        force.grid(row=i+1, column=0, ipadx=5, ipady=5, padx=10, pady=0)
        unknown_forces.append(force)
        force = KnownForce(root, f"Known{i+1}")
        force.grid(row=i+1, column=1, ipadx=5, ipady=5, padx=10, pady=0)
        known_forces.append(force)

    # try to load from history
    if os.path.exists("archive.json"):
        with open("archive.json", "r") as file:
            mrp, ukf_dicts, kf_dicts = json.load(file)
        moment_frame.import_from_list(mrp)
        for dic, f in zip(ukf_dicts, unknown_forces):
            f.import_from_dic(dic)
            f.update_entry()
        for dic, f in zip(kf_dicts, known_forces):
            f.import_from_dic(dic)
            f.update_entry()

    print("""
**力和力矩计算程序使用说明**

这个程序是一个用于计算力和力矩的工具。它允许您输入已知力和未知力的信息，然后计算未知力的结果。

**操作步骤：**

1. **设置力矩参考点：** 首先，您需要设置力矩的参考点。在窗口左上角的 "Calculate Moment at Point" 部分，输入力矩参考点的 x、y、z 坐标。

2. **输入已知力：** 在窗口右上角的 "Known Forces" 部分，您可以输入已知力的信息。对于每个已知力，输入以下信息：
   - **Magnitude（大小）：** 输入力的大小。
   - **Name（名称）：** 输入力的名称。
   - **Vector（矢量）：** 输入力的三个分量（x、y、z 方向）。
   - **Tail（起始点）：** 输入力的起始点的三个分量。

3. **输入未知力：** 在窗口左下角的 "Unknown Forces" 部分，您可以输入未知力的信息。对于每个未知力，输入以下信息：
   - **Name（名称）：** 输入力的名称。
   - **Vector（矢量）：** 输入力的三个分量（x、y、z 方向）。
   - **Tail（起始点）：** 输入力的起始点的三个分量。

4. **计算未知力：** 在窗口右下角的 "Calculate Result Here" 部分，点击 "calculate & update the result!" 按钮来计算未知力的结果。

5. **查看结果：** 计算完成后，程序将显示未知力的大小和结果，标记为黄色背景。您可以查看这些结果。

**自动保存和加载数据：**

- 这个程序具有自动保存和加载功能，无需用户手动操作。程序会在您关闭程序时自动保存当前的状态，并在下次运行时加载以前的状态。

**注意事项：**

- 请确保输入的数据是合法的，以避免错误。

- 这个功能确保了您可以轻松管理和恢复您的工作，无需手动保存文件。

- 如果需要帮助或有任何疑问，请随时联系程序管理员。

感谢您使用力和力矩计算程序！

""")

    root.mainloop()

    # save the history
    mrp = moment_frame.export_to_list()
    ukf_dicts = [f.export_to_dic() for f in unknown_forces]
    kf_dicts = [f.export_to_dic() for f in known_forces]
    with open("archive.json", "w") as file:
        json.dump([mrp, ukf_dicts, kf_dicts], file)
