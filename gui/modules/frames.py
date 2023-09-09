import customtkinter


class ModulesFrame(customtkinter.CTkFrame):
    def __init__(
            self,
            master,
            **kwargs
    ):
        super().__init__(master, **kwargs)

        self.frame = customtkinter.CTkFrame(master)
        self.frame.grid(
            row=0,
            column=2,
            padx=20,
            pady=20,
            sticky="nsew")
        self.frame.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=1)

        # self.frame_label = customtkinter.CTkLabel(
        #     self.frame,
        #     text="Modules:",
        #     font=customtkinter.CTkFont(size=16, weight="bold")
        # )
        # self.frame_label.grid(
        #     row=0,
        #     column=0,
        #     padx=20,
        #     pady=0,
        #     sticky="w"
        # )

        self.tabview = customtkinter.CTkTabview(self.frame, width=350)
        self.tabview.grid(
            row=0,
            column=0,
            padx=20,
            pady=0,
            sticky="nsew",
            rowspan=7
        )



