import os
import math
import matplotlib
matplotlib.use('Agg')  # خلفية غير تفاعلية للتوافق مع Kivy
import matplotlib.pyplot as plt

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle

# عوامل جدول الجودة للمخططات (A2, D3, D4)
A2_TABLE = {2: 1.880, 3: 1.023, 4: 0.729, 5: 0.577, 6: 0.483, 7: 0.419, 8: 0.373, 9: 0.337, 10: 0.308}
D3_TABLE = {2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0.076, 8: 0.136, 9: 0.184, 10: 0.223}
D4_TABLE = {2: 3.267, 3: 2.574, 4: 2.282, 5: 2.114, 6: 2.004, 7: 1.924, 8: 1.864, 9: 1.816, 10: 1.777}

class GlobalState:
    selected_chart = ""
    num_samples = 0
    sample_size = 0
    raw_data = []         # قائمة تحتوي البيانات المدخلة
    sample_indices = []   # أرقام العينات الحالية

# --- شاشة أساسية معالجة للخلفية bg.png ---
class BaseScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # تركيب الخلفية bg.png إذا كانت موجودة في المجلد
        if os.path.exists('bg.png'):
            with self.canvas.before:
                self.bg_rect = Rectangle(source='bg.png', pos=self.pos, size=self.size)
            self.bind(pos=self._update_bg, size=self._update_bg)

    def _update_bg(self, instance, value):
        if hasattr(self, 'bg_rect'):
            self.bg_rect.pos = self.pos
            self.bg_rect.size = self.size

# --- 1. الشاشة الأولى: اختيار نوع المخطط ---
class ScreenChartSelect(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        title = Label(
            text="Statistical Process Control (SPC)\nSelect Control Chart", 
            font_size='20sp', bold=True, halign='center', size_hint_y=None, height=70
        )
        layout.add_widget(title)
        
        charts = [
            ("Xbar - R Chart (Variables, Subgroup > 1)", "Xbar-R"),
            ("I - MR Chart (Individual Values, Subgroup = 1)", "I-MR"),
            ("p Chart (Fraction Defective / Attributes)", "p-Chart"),
            ("c Chart (Number of Defects / Attributes)", "c-Chart")
        ]
        
        for name, code in charts:
            btn = Button(text=name, size_hint_y=None, height=55, background_color=(0.2, 0.5, 0.8, 1))
            btn.bind(on_press=lambda inst, c=code: self.select_chart(c))
            layout.add_widget(btn)
            
        layout.add_widget(Widget())  # دفع العناصر للأعلى
        self.add_widget(layout)

    def select_chart(self, chart_code):
        GlobalState.selected_chart = chart_code
        self.manager.current = 'screen_dims'

# --- 2. الشاشة الثانية: تحديد عدد العينات وحجم العينة ---
class ScreenDimensions(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        self.lbl_title = Label(text="", font_size='18sp', bold=True, size_hint_y=None, height=40)
        self.layout.add_widget(self.lbl_title)
        
        self.txt_samples = TextInput(hint_text="Number of Samples (Rows)", input_filter='int', multiline=False, size_hint_y=None, height=50)
        self.txt_size = TextInput(hint_text="Sample Size (Columns)", input_filter='int', multiline=False, size_hint_y=None, height=50)
        
        self.layout.add_widget(self.txt_samples)
        self.layout.add_widget(self.txt_size)
        
        btn_next = Button(text="OK -> Enter Data Grid", size_hint_y=None, height=55, background_color=(0.1, 0.6, 0.2, 1))
        btn_next.bind(on_press=self.proceed_to_grid)
        self.layout.add_widget(btn_next)
        
        self.lbl_err = Label(text="", color=(1, 0, 0, 1), size_hint_y=None, height=30)
        self.layout.add_widget(self.lbl_err)
        
        self.layout.add_widget(Widget())  # دفع العناصر للأعلى
        self.add_widget(self.layout)

    def on_pre_enter(self):
        self.lbl_title.text = f"Chart Selected: {GlobalState.selected_chart}"
        if GlobalState.selected_chart in ["I-MR", "c-Chart"]:
            self.txt_size.text = "1"
            self.txt_size.disabled = True
        else:
            self.txt_size.text = ""
            self.txt_size.disabled = False

    def proceed_to_grid(self, instance):
        try:
            samples = int(self.txt_samples.text)
            size = int(self.txt_size.text)
            
            if samples <= 0 or size <= 0:
                self.lbl_err.text = "Error: Values must be greater than 0!"
                return
                
            if GlobalState.selected_chart == "Xbar-R" and (size < 2 or size > 10):
                self.lbl_err.text = "For Xbar-R chart, Sample Size must be between 2 and 10."
                return

            GlobalState.num_samples = samples
            GlobalState.sample_size = size
            self.lbl_err.text = ""
            self.manager.get_screen('screen_grid').build_grid()
            self.manager.current = 'screen_grid'
        except ValueError:
            self.lbl_err.text = "Please enter valid integers!"

# --- 3. الشاشة الثالثة: جدول إدخال البيانات ---
class ScreenDataGrid(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.add_widget(self.main_layout)

    def build_grid(self):
        self.main_layout.clear_widgets()
        
        title = Label(text=f"Enter Data ({GlobalState.num_samples} Samples x {GlobalState.sample_size} Size)", 
                      font_size='16sp', bold=True, size_hint_y=None, height=40)
        self.main_layout.add_widget(title)
        
        scroll = ScrollView()
        grid = GridLayout(cols=GlobalState.sample_size + 1, spacing=5, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        
        grid.add_widget(Label(text="Sample #", bold=True, size_hint_y=None, height=40))
        for j in range(1, GlobalState.sample_size + 1):
            grid.add_widget(Label(text=f"Obs {j}", bold=True, size_hint_y=None, height=40))
            
        self.inputs_matrix = []
        for i in range(1, GlobalState.num_samples + 1):
            grid.add_widget(Label(text=f"S-{i}", size_hint_y=None, height=40))
            row_inputs = []
            for j in range(GlobalState.sample_size):
                txt = TextInput(multiline=False, input_filter='float', size_hint_y=None, height=40)
                grid.add_widget(txt)
                row_inputs.append(txt)
            self.inputs_matrix.append(row_inputs)
            
        scroll.add_widget(grid)
        self.main_layout.add_widget(scroll)
        
        btn_calc = Button(text="Calculate & Plot Chart 🚀", size_hint_y=None, height=50, background_color=(0.1, 0.6, 0.2, 1))
        btn_calc.bind(on_press=self.process_data)
        self.main_layout.add_widget(btn_calc)
        
        self.lbl_err = Label(text="", color=(1, 0, 0, 1), size_hint_y=None, height=30)
        self.main_layout.add_widget(self.lbl_err)

    def process_data(self, instance):
        try:
            data = []
            for row in self.inputs_matrix:
                row_vals = [float(cell.text) for cell in row]
                data.append(row_vals)
                
            GlobalState.raw_data = data
            GlobalState.sample_indices = list(range(1, len(data) + 1))
            self.lbl_err.text = ""
            
            self.manager.get_screen('screen_result').calculate_and_display()
            self.manager.current = 'screen_result'
        except ValueError:
            self.lbl_err.text = "Error: Please fill ALL cells with numeric values!"

# --- 4. الشاشة الرابعة: عرض المخطط البياني والتحليل ---
class ScreenResult(BaseScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.img_chart = Image(size_hint_y=0.55)
        self.layout.add_widget(self.img_chart)
        
        scroll_res = ScrollView(size_hint_y=0.3)
        self.lbl_analysis = Label(text="", font_size='14sp', halign='left', size_hint_y=None)
        self.lbl_analysis.bind(texture_size=self.lbl_analysis.setter('size'))
        scroll_res.add_widget(self.lbl_analysis)
        self.layout.add_widget(scroll_res)
        
        btn_box = BoxLayout(size_hint_y=0.15, spacing=10)
        self.btn_remove_ooc = Button(text="Remove Out-Of-Control Samples", background_color=(0.8, 0.2, 0.2, 1))
        self.btn_remove_ooc.bind(on_press=self.remove_ooc_samples)
        
        btn_restart = Button(text="Start New Chart", background_color=(0.3, 0.3, 0.3, 1))
        btn_restart.bind(on_press=self.restart_app)
        
        btn_box.add_widget(self.btn_remove_ooc)
        btn_box.add_widget(btn_restart)
        self.layout.add_widget(btn_box)
        
        self.add_widget(self.layout)
        self.ooc_list = []

    def calculate_and_display(self):
        chart_type = GlobalState.selected_chart
        data = GlobalState.raw_data
        indices = GlobalState.sample_indices
        n = GlobalState.sample_size
        
        values = []
        ucl, lcl, cl = 0, 0, 0
        
        if chart_type == "Xbar-R":
            values = [sum(row) / len(row) for row in data]
            ranges = [max(row) - min(row) for row in data]
            cl = sum(values) / len(values)
            r_bar = sum(ranges) / len(ranges)
            a2 = A2_TABLE.get(n, 0.577)
            ucl = cl + (a2 * r_bar)
            lcl = cl - (a2 * r_bar)
            
        elif chart_type == "I-MR":
            values = [row[0] for row in data]
            cl = sum(values) / len(values)
            mr = [abs(values[i] - values[i-1]) for i in range(1, len(values))]
            mr_bar = sum(mr) / len(mr) if mr else 0
            ucl = cl + (2.66 * mr_bar)
            lcl = cl - (2.66 * mr_bar)
            
        elif chart_type == "p-Chart":
            defects = [row[0] for row in data]
            p_i = [d / n for d in defects]
            values = p_i
            p_bar = sum(defects) / (len(data) * n)
            cl = p_bar
            sd = math.sqrt((p_bar * (1 - p_bar)) / n)
            ucl = p_bar + (3 * sd)
            lcl = max(0, p_bar - (3 * sd))
            
        elif chart_type == "c-Chart":
            values = [row[0] for row in data]
            cl = sum(values) / len(values)
            ucl = cl + (3 * math.sqrt(cl))
            lcl = max(0, cl - (3 * math.sqrt(cl)))

        self.ooc_list = []
        for idx, val in zip(indices, values):
            if val > ucl or val < lcl:
                self.ooc_list.append((idx, val))

        fig, ax = plt.subplots(figsize=(7, 4))
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')
        
        ax.plot(indices, values, color='blue', marker='o', linestyle='-', label='Sample Values')
        
        if self.ooc_list:
            ooc_x = [pt[0] for pt in self.ooc_list]
            ooc_y = [pt[1] for pt in self.ooc_list]
            ax.plot(ooc_x, ooc_y, 'ro', markersize=9, label='Out of Control')

        ax.axhline(cl, color='green', linestyle='--', label=f'CL = {cl:.2f}')
        ax.axhline(ucl, color='red', linestyle='--', label=f'UCL = {ucl:.2f}')
        ax.axhline(lcl, color='red', linestyle='--', label=f'LCL = {lcl:.2f}')

        ax.set_title(f"Control Chart: {chart_type}", color='black', fontsize=12, fontweight='bold')
        ax.set_xlabel("Sample Number", color='black')
        ax.set_ylabel("Value", color='black')
        ax.grid(True, linestyle=':', alpha=0.6)
        ax.legend(loc='upper right', fontsize=8)
        plt.tight_layout()

        chart_path = "qc_chart.png"
        plt.savefig(chart_path, dpi=100, facecolor=fig.get_facecolor())
        plt.close(fig)
        
        self.img_chart.source = chart_path
        self.img_chart.reload()

        report = [
            f"=== QUALITY CONTROL ANALYSIS ({chart_type}) ===",
            f"Total Samples Analyzed: {len(data)}",
            f"Center Line (CL): {cl:.4f}",
            f"Upper Control Limit (UCL): {ucl:.4f}",
            f"Lower Control Limit (LCL): {lcl:.4f}",
            "-" * 45
        ]

        if self.ooc_list:
            ooc_str = ", ".join([f"S-{pt[0]}" for pt in self.ooc_list])
            report.append(f"STATUS: Process is OUT OF CONTROL! ⚠️")
            report.append(f"Out-of-control sample(s): {ooc_str}")
            report.append("Action: Click 'Remove Out-Of-Control Samples' to recalculate limits.")
            self.btn_remove_ooc.disabled = False
        else:
            report.append("STATUS: Process is IN STATISTICAL CONTROL. ✅")
            report.append("All sample points are within control limits.")
            self.btn_remove_ooc.disabled = True

        self.lbl_analysis.text = "\n".join(report)

    def remove_ooc_samples(self, instance):
        if not self.ooc_list:
            return
            
        ooc_indices_set = set(pt[0] for pt in self.ooc_list)
        
        new_data = []
        new_indices = []
        for idx, row in zip(GlobalState.sample_indices, GlobalState.raw_data):
            if idx not in ooc_indices_set:
                new_data.append(row)
                new_indices.append(idx)
                
        GlobalState.raw_data = new_data
        GlobalState.sample_indices = new_indices
        self.calculate_and_display()

    def restart_app(self, instance):
        self.manager.current = 'screen_chart_select'

# --- إدارة الشاشات وتدفق التطبيق ---
class QualityControlApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ScreenChartSelect(name='screen_chart_select'))
        sm.add_widget(ScreenDimensions(name='screen_dims'))
        sm.add_widget(ScreenDataGrid(name='screen_grid'))
        sm.add_widget(ScreenResult(name='screen_result'))
        return sm

if __name__ == '__main__':
    QualityControlApp().run()
            
