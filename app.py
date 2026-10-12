import os
import sys
import json
import customtkinter as ctk
from tkinter import filedialog, messagebox

from cnf_converter import CNFConverter


# ============================================================
# RESOURCE PATH
# Works both normally and inside PyInstaller .exe
# ============================================================

def resource_path(filename):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)

    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        filename
    )


# ============================================================
# APPEARANCE
# ============================================================

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# ============================================================
# COLORS
# ============================================================

BG_COLOR = "#070B14"
CARD_COLOR = "#0F172A"
INNER_COLOR = "#111827"
BORDER_COLOR = "#263449"

BLUE = "#3B82F6"
BLUE_HOVER = "#2563EB"
CYAN = "#22D3EE"

TEXT = "#F8FAFC"
SECONDARY = "#94A3B8"

GREEN = "#22C55E"
YELLOW = "#F59E0B"
RED = "#EF4444"


# ============================================================
# MAIN APPLICATION
# ============================================================

class CNFConverterApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # Window
        self.title(
            "CNF Lab - CFG to Chomsky Normal Form"
        )

        self.geometry("1400x850")
        self.minsize(1100, 700)

        self.configure(
            fg_color=BG_COLOR
        )

        # Application icon
        try:
            self.iconbitmap(
                resource_path("icon.ico")
            )
        except Exception:
            pass

        # Data
        self.current_result = None
        self.step_widgets = []

        # Build UI
        self.create_header()
        self.create_main_area()
        self.create_output_area()


    # ========================================================
    # HEADER
    # ========================================================

    def create_header(self):

        header = ctk.CTkFrame(
            self,
            fg_color=CARD_COLOR,
            corner_radius=18,
            border_width=1,
            border_color=BORDER_COLOR
        )

        header.pack(
            fill="x",
            padx=20,
            pady=(20, 10)
        )

        # Logo
        logo = ctk.CTkLabel(
            header,
            text="◈",
            font=ctk.CTkFont(
                size=34,
                weight="bold"
            ),
            text_color=CYAN
        )

        logo.pack(
            side="left",
            padx=(22, 8),
            pady=15
        )

        # Title area
        title_frame = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )

        title_frame.pack(
            side="left",
            pady=10
        )

        title = ctk.CTkLabel(
            title_frame,
            text="CNF LAB",
            font=ctk.CTkFont(
                size=25,
                weight="bold"
            ),
            text_color=TEXT
        )

        title.pack(
            anchor="w"
        )

        subtitle = ctk.CTkLabel(
            title_frame,
            text="Context-Free Grammar  →  Chomsky Normal Form",
            font=ctk.CTkFont(
                size=12
            ),
            text_color=SECONDARY
        )

        subtitle.pack(
            anchor="w"
        )

        # Status
        status = ctk.CTkLabel(
            header,
            text="●  READY",
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            text_color=GREEN
        )

        status.pack(
            side="right",
            padx=25
        )


    # ========================================================
    # MAIN AREA
    # ========================================================

    def create_main_area(self):

        main = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        main.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=10
        )

        main.grid_columnconfigure(
            0,
            weight=4
        )

        main.grid_columnconfigure(
            1,
            weight=6
        )

        main.grid_rowconfigure(
            0,
            weight=1
        )

        self.create_input_panel(main)
        self.create_pipeline_panel(main)


    # ========================================================
    # INPUT PANEL
    # ========================================================

    def create_input_panel(self, parent):

        card = ctk.CTkFrame(
            parent,
            fg_color=CARD_COLOR,
            corner_radius=18,
            border_width=1,
            border_color=BORDER_COLOR
        )

        card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 8)
        )

        heading = ctk.CTkLabel(
            card,
            text="INPUT GRAMMAR",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            ),
            text_color=TEXT
        )

        heading.pack(
            anchor="w",
            padx=20,
            pady=(20, 3)
        )

        description = ctk.CTkLabel(
            card,
            text="Define your Context-Free Grammar",
            font=ctk.CTkFont(
                size=12
            ),
            text_color=SECONDARY
        )

        description.pack(
            anchor="w",
            padx=20,
            pady=(0, 15)
        )

        # Preset label
        preset_label = ctk.CTkLabel(
            card,
            text="Sample Grammar",
            font=ctk.CTkFont(
                size=12
            ),
            text_color=SECONDARY
        )

        preset_label.pack(
            anchor="w",
            padx=20
        )

        # Preset dropdown
        self.preset = ctk.CTkComboBox(
            card,
            values=[
                "Simple CFG",
                "Nullable Production",
                "Unit Production",
                "Long Production"
            ],
            height=38,
            corner_radius=10,
            border_color=BORDER_COLOR,
            button_color=BLUE,
            button_hover_color=BLUE_HOVER,
            command=self.load_preset
        )

        self.preset.pack(
            fill="x",
            padx=20,
            pady=(5, 12)
        )

        self.preset.set(
            "Simple CFG"
        )

        # Grammar editor
        self.grammar_box = ctk.CTkTextbox(
            card,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR,
            fg_color=BG_COLOR,
            text_color=TEXT,
            font=ctk.CTkFont(
                family="Consolas",
                size=14
            )
        )

        self.grammar_box.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=5
        )

        self.grammar_box.insert(
            "1.0",
            "S -> AB\n"
            "A -> aA | ε\n"
            "B -> bB | b"
        )

        # Help text
        info = ctk.CTkLabel(
            card,
            text=(
                "Use one production per line\n"
                "Example: S -> AB | a"
            ),
            font=ctk.CTkFont(
                size=11
            ),
            text_color=SECONDARY,
            justify="left"
        )

        info.pack(
            anchor="w",
            padx=20,
            pady=8
        )

        # Convert button
        convert = ctk.CTkButton(
            card,
            text="⚡  CONVERT TO CNF",
            height=48,
            corner_radius=12,
            fg_color=BLUE,
            hover_color=BLUE_HOVER,
            font=ctk.CTkFont(
                size=15,
                weight="bold"
            ),
            command=self.convert_grammar
        )

        convert.pack(
            fill="x",
            padx=20,
            pady=(5, 20)
        )


    # ========================================================
    # PIPELINE PANEL
    # ========================================================

    def create_pipeline_panel(self, parent):

        card = ctk.CTkFrame(
            parent,
            fg_color=CARD_COLOR,
            corner_radius=18,
            border_width=1,
            border_color=BORDER_COLOR
        )

        card.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(8, 0)
        )

        title = ctk.CTkLabel(
            card,
            text="CONVERSION PIPELINE",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            ),
            text_color=TEXT
        )

        title.pack(
            anchor="w",
            padx=20,
            pady=(20, 3)
        )

        subtitle = ctk.CTkLabel(
            card,
            text="Step-by-step CFG transformation",
            font=ctk.CTkFont(
                size=12
            ),
            text_color=SECONDARY
        )

        subtitle.pack(
            anchor="w",
            padx=20,
            pady=(0, 15)
        )

        # Scrollable pipeline
        self.pipeline = ctk.CTkScrollableFrame(
            card,
            fg_color="transparent"
        )

        self.pipeline.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5
        )

        # Initial message
        self.pipeline_empty_label = ctk.CTkLabel(
            self.pipeline,
            text=(
                "Your conversion steps will appear here.\n\n"
                "Enter a grammar and click\n"
                "\"CONVERT TO CNF\"."
            ),
            font=ctk.CTkFont(
                size=13
            ),
            text_color=SECONDARY,
            justify="center"
        )

        self.pipeline_empty_label.pack(
            pady=80
        )


    # ========================================================
    # STEP CARD
    # ========================================================

    def create_step_card(
        self,
        number,
        title,
        description,
        grammar
    ):

        frame = ctk.CTkFrame(
            self.pipeline,
            fg_color=INNER_COLOR,
            corner_radius=14,
            border_width=1,
            border_color=BORDER_COLOR
        )

        frame.pack(
            fill="x",
            padx=5,
            pady=6
        )

        # Top row
        top = ctk.CTkFrame(
            frame,
            fg_color="transparent"
        )

        top.pack(
            fill="x",
            padx=12,
            pady=(12, 4)
        )

        # Number
        number_label = ctk.CTkLabel(
            top,
            text=f"{number:02}",
            width=42,
            height=38,
            corner_radius=10,
            fg_color="#172554",
            text_color=CYAN,
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            )
        )

        number_label.pack(
            side="left"
        )

        # Title
        title_label = ctk.CTkLabel(
            top,
            text=title,
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            ),
            text_color=TEXT
        )

        title_label.pack(
            side="left",
            padx=12
        )

        # Completed status
        status = ctk.CTkLabel(
            top,
            text="✓",
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            ),
            text_color=GREEN
        )

        status.pack(
            side="right"
        )

        # Description
        description_label = ctk.CTkLabel(
            frame,
            text=description,
            font=ctk.CTkFont(
                size=11
            ),
            text_color=SECONDARY,
            justify="left",
            anchor="w"
        )

        description_label.pack(
            fill="x",
            padx=66,
            pady=(0, 8)
        )

        # Grammar output
        grammar_box = ctk.CTkTextbox(
            frame,
            height=100,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_COLOR,
            fg_color=BG_COLOR,
            text_color=TEXT,
            font=ctk.CTkFont(
                family="Consolas",
                size=11
            )
        )

        grammar_box.pack(
            fill="x",
            padx=12,
            pady=(0, 12)
        )

        grammar_box.insert(
            "1.0",
            grammar
        )

        grammar_box.configure(
            state="disabled"
        )

        self.step_widgets.append(
            frame
        )


    # ========================================================
    # OUTPUT PANEL
    # ========================================================

    def create_output_area(self):

        output = ctk.CTkFrame(
            self,
            fg_color=CARD_COLOR,
            corner_radius=18,
            border_width=1,
            border_color=BORDER_COLOR
        )

        output.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

        # Top row
        top = ctk.CTkFrame(
            output,
            fg_color="transparent"
        )

        top.pack(
            fill="x"
        )

        title = ctk.CTkLabel(
            top,
            text="FINAL CNF OUTPUT",
            font=ctk.CTkFont(
                size=17,
                weight="bold"
            ),
            text_color=TEXT
        )

        title.pack(
            side="left",
            padx=20,
            pady=15
        )

        self.output_status = ctk.CTkLabel(
            top,
            text="WAITING",
            font=ctk.CTkFont(
                size=11,
                weight="bold"
            ),
            text_color=SECONDARY
        )

        self.output_status.pack(
            side="left"
        )

        # Copy button
        copy_button = ctk.CTkButton(
            top,
            text="⧉ Copy",
            width=90,
            height=34,
            corner_radius=9,
            fg_color=INNER_COLOR,
            hover_color="#1E293B",
            command=self.copy_output
        )

        copy_button.pack(
            side="right",
            padx=(5, 10)
        )

        # TXT button
        txt_button = ctk.CTkButton(
            top,
            text="TXT",
            width=65,
            height=34,
            corner_radius=9,
            fg_color=INNER_COLOR,
            hover_color="#1E293B",
            command=self.export_txt
        )

        txt_button.pack(
            side="right",
            padx=5
        )

        # JSON button
        json_button = ctk.CTkButton(
            top,
            text="JSON",
            width=65,
            height=34,
            corner_radius=9,
            fg_color=INNER_COLOR,
            hover_color="#1E293B",
            command=self.export_json
        )

        json_button.pack(
            side="right",
            padx=5
        )

        # Output box
        self.output_box = ctk.CTkTextbox(
            output,
            height=145,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_COLOR,
            fg_color=BG_COLOR,
            text_color=TEXT,
            font=ctk.CTkFont(
                family="Consolas",
                size=12
            )
        )

        self.output_box.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

        self.output_box.insert(
            "1.0",
            "Waiting for conversion..."
        )

        self.output_box.configure(
            state="disabled"
        )


    # ========================================================
    # PRESET GRAMMARS
    # ========================================================

    def load_preset(self, choice):

        presets = {

            "Simple CFG":
                "S -> AB\n"
                "A -> a\n"
                "B -> b",

            "Nullable Production":
                "S -> AB\n"
                "A -> a | ε\n"
                "B -> b",

            "Unit Production":
                "S -> A\n"
                "A -> B\n"
                "B -> b",

            "Long Production":
                "S -> ABCD\n"
                "A -> a\n"
                "B -> b\n"
                "C -> c\n"
                "D -> d"
        }

        self.grammar_box.delete(
            "1.0",
            "end"
        )

        self.grammar_box.insert(
            "1.0",
            presets[choice]
        )


    # ========================================================
    # CONVERT GRAMMAR
    # ========================================================

    def convert_grammar(self):

        grammar = self.grammar_box.get(
            "1.0",
            "end"
        ).strip()

        if not grammar:

            messagebox.showwarning(
                "Empty Grammar",
                "Please enter a Context-Free Grammar."
            )

            return

        try:

            # Create converter
            converter = CNFConverter(
                grammar
            )

            # Convert grammar
            result = converter.convert()

            # Save result
            self.current_result = result

            # Display pipeline
            self.display_steps(
                result["steps"]
            )

            # Display final CNF
            self.display_output(
                result["final"]
            )

            # Update status
            self.output_status.configure(
                text="✓ CONVERTED",
                text_color=GREEN
            )

        except Exception as error:

            messagebox.showerror(
                "Conversion Error",
                str(error)
            )

            self.output_status.configure(
                text="ERROR",
                text_color=RED
            )


    # ========================================================
    # DISPLAY CONVERSION STEPS
    # ========================================================

    def display_steps(self, steps):

        # Remove old widgets
        for widget in self.pipeline.winfo_children():
            widget.destroy()

        self.step_widgets = []

        # Add new steps
        for step in steps:

            self.create_step_card(
                step["number"],
                step["title"],
                step["description"],
                step["grammar"]
            )


    # ========================================================
    # DISPLAY FINAL OUTPUT
    # ========================================================

    def display_output(self, final_text):

        self.output_box.configure(
            state="normal"
        )

        self.output_box.delete(
            "1.0",
            "end"
        )

        self.output_box.insert(
            "1.0",
            final_text
        )

        self.output_box.configure(
            state="disabled"
        )


    # ========================================================
    # COPY FINAL OUTPUT
    # ========================================================

    def copy_output(self):

        if not self.current_result:

            messagebox.showinfo(
                "Nothing to Copy",
                "Please convert a grammar first."
            )

            return

        text = self.current_result["final"]

        self.clipboard_clear()

        self.clipboard_append(
            text
        )

        self.update()

        messagebox.showinfo(
            "Copied",
            "Final CNF grammar copied to clipboard."
        )


    # ========================================================
    # EXPORT TXT
    # ========================================================

    def export_txt(self):

        if not self.current_result:

            messagebox.showinfo(
                "No Result",
                "Please convert a grammar first."
            )

            return

        file_path = filedialog.asksaveasfilename(
            title="Export CNF as TXT",
            defaultextension=".txt",
            filetypes=[
                (
                    "Text File",
                    "*.txt"
                )
            ]
        )

        if not file_path:
            return

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                self.current_result["final"]
            )

        messagebox.showinfo(
            "Export Successful",
            "CNF grammar exported successfully."
        )


    # ========================================================
    # EXPORT JSON
    # ========================================================

    def export_json(self):

        if not self.current_result:

            messagebox.showinfo(
                "No Result",
                "Please convert a grammar first."
            )

            return

        file_path = filedialog.asksaveasfilename(
            title="Export CNF as JSON",
            defaultextension=".json",
            filetypes=[
                (
                    "JSON File",
                    "*.json"
                )
            ]
        )

        if not file_path:
            return

        data = {
            "final_cnf": self.current_result["final"],
            "steps": self.current_result["steps"]
        }

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False
            )

        messagebox.showinfo(
            "Export Successful",
            "CNF conversion exported as JSON."
        )


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    app = CNFConverterApp()

    app.mainloop()