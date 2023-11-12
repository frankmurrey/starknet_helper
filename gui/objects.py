import tkinter
import random
from typing import Optional, Callable, Union

import customtkinter

from utils import gui as gui_utils
from gui import constants


class FloatSpinbox(customtkinter.CTkFrame):
    def __init__(
            self,
            *args,
            start_index: int = 1,
            max_value: Union[int] = 100,
            width: int = 100,
            height: int = 32,
            step_size: Union[int, float] = 1,
            command: Callable = None,
            **kwargs
    ):
        super().__init__(*args, width=width, height=height, **kwargs)

        self.step_size = int(step_size)
        self.max_value = int(max_value)
        self.command = command

        self.configure(fg_color=("gray78", "gray21"))

        self.grid_columnconfigure((0, 2), weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.subtract_button = customtkinter.CTkButton(self, text="-", width=height-6, height=height-6,
                                                       command=self.subtract_button_callback)
        self.subtract_button.grid(row=0, column=0, padx=(3, 0), pady=3)

        self.entry = customtkinter.CTkEntry(self, width=width-(2*height), height=height-6, border_width=0, fg_color="gray16")
        self.entry.grid(row=0, column=1, columnspan=1, padx=3, pady=3, sticky="ew")

        self.add_button = customtkinter.CTkButton(self, text="+", width=height-6, height=height-6,
                                                  command=self.add_button_callback)
        self.add_button.grid(row=0, column=2, padx=(0, 3), pady=3)

        self.entry.insert(0, start_index)

    def add_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            value = int(self.entry.get()) + self.step_size
            if value > self.max_value:
                value = self.max_value
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return

    def subtract_button_callback(self):
        if self.command is not None:
            self.command()
        try:
            value = int(self.entry.get()) - self.step_size
            if value < 1:
                value = 1
            self.entry.delete(0, "end")
            self.entry.insert(0, value)
        except ValueError:
            return

    def get(self) -> Union[float, None]:
        try:
            return float(self.entry.get())
        except ValueError:
            return None

    def set(self, value: float):
        self.entry.delete(0, "end")
        self.entry.insert(0, str(int(value)))


class CTkEntryWithLabel(customtkinter.CTkFrame):
    """
    Entry with a label
    """

    def __init__(
            self,
            master,
            label_text: str,

            textvariable: Optional[Union[tkinter.StringVar, tkinter.Variable]] = None,

            on_text_changed: Optional[Callable] = None,
            on_focus_in: Optional[Callable] = None,
            on_focus_out: Optional[Callable] = None,

            width: int = 140,
            height: int = 28,

            state: str = tkinter.NORMAL,

            hide_on_focus_out: bool = False,
            **kwargs
    ):
        super().__init__(master, fg_color="transparent")

        self.on_text_changed = on_text_changed if on_text_changed is not None else lambda: None
        self.on_focus_in = on_focus_in if on_focus_in is not None else lambda: None
        self.on_focus_out = on_focus_out if on_focus_out is not None else lambda: None

        self.label = customtkinter.CTkLabel(
            self,
            text=label_text,
        )
        self.label.grid(row=0, column=0, padx=0, pady=0, sticky="w")

        self.entry = customtkinter.CTkEntry(
            self,
            state=state,
            textvariable=textvariable,
            width=width,
            height=height,

            **kwargs
        )

        if state == tkinter.DISABLED:
            self.entry.configure(fg_color="gray25", border_color="gray25")

        self.entry.grid(row=1, column=0, padx=0, pady=0, sticky="w")
        self.entry.bind("<KeyRelease>", self.text_changed)

        self.text = textvariable.get().strip() if isinstance(textvariable, tkinter.StringVar) else ""
        self.is_shortened = False
        if hide_on_focus_out:
            shortened_string = gui_utils.shorten_long_string(self.text)
            self.entry.configure(textvariable=tkinter.StringVar(value=shortened_string))
            self.is_shortened = True

            self.entry.bind("<FocusIn>", self.focus_in)
            self.entry.bind("<FocusOut>", self.focus_out)

    def get(self):
        return self.entry.get().strip()

    def bind(self, sequence, command, add=True):
        self.entry.bind(sequence, command, add)

    def show_full_text(self):
        self.entry.configure(textvariable=tkinter.StringVar(value=self.text))
        self.is_shortened = False

    def hide_full_text(self):
        text = gui_utils.shorten_long_string(self.text)
        self.entry.configure(textvariable=tkinter.StringVar(value=text))
        self.is_shortened = True

    def text_changed(self, event):
        self.text = self.entry.get().strip()

        self.on_text_changed()

    def focus_in(self, event):
        self.on_focus_in()

        self.show_full_text()

    def focus_out(self, event):
        self.on_focus_out()

        self.hide_full_text()

    def set_text_changed_callback(self, callback: Callable):
        self.entry.bind("<KeyRelease>", lambda event: callback())

    def set_click_callback(self, callback: Callable):
        self.entry.bind("<Button-1>", lambda event: callback())

    def set_focus_in_callback(self, callback: Callable):
        self.on_focus_in = callback

    def set_focus_out_callback(self, callback: Callable):
        self.on_focus_out = callback


class CTkCustomTextBox(customtkinter.CTkTextbox):
    def __init__(
            self,
            master,
            grid: dict,
            text: str,
            height: int = 100,
            font: tuple = ("Consolas", 14),
    ):
        super().__init__(master=master, font=font, fg_color='gray14')
        self.configure(height=height)
        self.grid(**grid)
        self.insert("1.0", text)


class ComboWithRandomCheckBox:
    def __init__(
            self,
            master,
            grid: dict,
            options: list,
            text: str = "Random",
            combo_command: Optional[Callable] = lambda _: None,
    ):
        self.options = options

        self.combobox = customtkinter.CTkComboBox(
            master=master,
            values=options,
            width=130,
            command=combo_command
        )
        self.combobox.grid(**grid)

        self.random_checkbox = customtkinter.CTkCheckBox(
            master=master,
            text=text,
            checkbox_width=18,
            checkbox_height=18,
            onvalue=True,
            offvalue=False,
            command=self.random_checkbox_event,
        )
        self.random_checkbox.grid(row=grid["row"] + 1, column=grid["column"], padx=20, pady=5, sticky="w")

    def random_checkbox_event(self):
        if self.random_checkbox.get():
            self.combobox.configure(
                state="disabled",
                fg_color='#3f3f3f',
            )
        else:
            self.combobox.configure(
                state="normal",
                fg_color='#343638',
            )

    def get_value(self):
        if self.random_checkbox.get():
            return random.choice(self.options)
        return self.combobox.get()

    def get_checkbox_value(self):
        return self.random_checkbox.get()

    def set_values(self, combo_value: str):

        if combo_value.lower() == 'random':
            self.combobox.configure(
                state="disabled",
                fg_color='#3f3f3f',
            )
            self.random_checkbox.select()
        else:
            self.combobox.configure(
                state="normal",
                fg_color='#343638',
            )
            self.combobox.set(combo_value)
            self.random_checkbox.deselect()
