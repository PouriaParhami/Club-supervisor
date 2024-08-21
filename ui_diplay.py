from tkinter import *
from PIL import Image
Image.CUBIC = Image.BICUBIC
import ttkbootstrap as ttk
import cv2
import re
import win32com.client
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import threading
import face_recognition_yolo_insepresv1_db as face_rec
import face_detection_yolo_inceptionRes as face_detect
import sqlit_setup 
import pandas as pd
from datetime import datetime

class HomePage:
    def __init__(self):
        
        sqlit_setup.setup_database()
        
        # Create the main window
        self.root = ttk.Window(themename="superhero")
        self.root.state('zoomed') # Make the window full screen
        self.root.title("Gym Entry")

        # Create the frames
        self.frame_left = ttk.Frame(self.root, width=200, height=400,)  # primary"
        self.frame_right = ttk.Frame(self.root, width=200, height=400,) # bootstyle="secondary"
        self.frame_bottom = ttk.Frame(self.root, height=200,) # bootstyle="success"

        # Position the frames in the grid
        self.frame_left.grid(row=0, column=0, sticky="nsew")
        self.frame_right.grid(row=0, column=1, sticky="nsew")
        self.frame_bottom.grid(row=1, column=0, columnspan=2, sticky="nsew")

        # Configure row and column weights to ensure proper resizing
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        
    def get_webcam_names(self):
        """Get the names of all connected webcams."""
        wmi = win32com.client.GetObject("winmgmts:")
        webcams = []
        for item in wmi.InstancesOf("Win32_PnPEntity"):
            if item.Caption and re.search(r'camera|video', item.Caption, re.I):
                webcams.append(item.Caption)
        return webcams 
    
    def get_webcam_index(self):
        """List all available webcams."""
        index = 0
        arr = []
        while True:
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # Use CAP_DSHOW for Windows to avoid "assertion failed" errors
            if not cap.read()[0]:
                break
            else:
                arr.append(index)
                cap.release()
            index += 1
        return arr
    
    def webcam_name_index(self):
        name_list = self.get_webcam_names()
        name_list.reverse()
        index_list = self.get_webcam_index()
        
        name_index = zip(index_list, name_list)
        return name_index
    
    def _scaler_acc(self, e):
        self.acc = self.accuracy_meter.get()
        self.acc_label.config(text=f"Accuracy: {self.acc:.1}%")
        self.acc=float(f"{self.acc:.1}")
    
    def start_stop_recognition(self):
        camera_index = int(self.my_combo.get().split(" ")[0])
        if self.start_stop.get() == 1:
            acc = self.accuracy_meter.get()
            acc = float(f"{acc:.1}")
            self.accuracy_meter.config(state=DISABLED)
            self.my_combo.config(state=DISABLED)
            
            self.progress_bar_start.grid()  # Show the progress bar
            self.progress_bar_start.start()  # Start the progress bar
            recognition_thread = threading.Thread(target=face_rec.start_recognition, 
                                                args=(camera_index,
                                                    self.start_stop.get(), 
                                                    self.save_pic_value.get(),
                                                    acc, 
                                                    self._append_bottom_tree,
                                                    self.progress_bar_start))  # Pass the progress bar instance here
            recognition_thread.daemon = True
            recognition_thread.start()
        else:
            face_rec.stop_recognition()
            self.accuracy_meter.config(state=NORMAL)
            self.my_combo.config(state=NORMAL)
            self.progress_bar_start.stop()
            self.progress_bar_start.grid_remove() 

    def _display_start_recognition(self):
        left_frame_label = ttk.Label(self.frame_left, text="Start Recongniton and Set the Accuracy.")
        left_frame_label.grid(column=0, row=0, padx=10, pady=20)
    
        self.start_stop = IntVar()
        strt_recognition = ttk.Checkbutton(self.frame_left, bootstyle="success, round-toggle",
                            text="Start/Stop Recognition", 
                            variable=self.start_stop, 
                            onvalue=1,
                            offvalue=0,
                            command=self.start_stop_recognition)

        strt_recognition.grid(column=0, row=1, pady=40, padx=10)
        
    def _display_save_image_button(self):
        self.save_pic_value = IntVar(value=1)
        save_pic = ttk.Checkbutton(self.frame_left, bootstyle="success, round-toggle",
                                text="Save Members Picture", 
                                variable=self.save_pic_value, 
                                onvalue=1,
                                offvalue=0,
                                )
        
        save_pic.grid(column=1, row=1, pady=40, padx=10)
    
    def _display_chose_camera(self):
        web_cam_list = list(self.webcam_name_index())
        self.my_combo = ttk.Combobox(self.frame_left, 
                        bootstyle="success", 
                        values=web_cam_list)
        self.my_combo.grid(column=2, row=1, pady=40, padx=10)

        # Set Combo Default
        self.my_combo.current(0)
        self.my_combo.bind("<<ComboboxSelected>>", self._click_bind)
    
    def _click_bind(self, e):
        camera_index_name = self.my_combo.get()
        camera_index = camera_index_name.split(" ")[0]
        return int(camera_index)
    
    def _display_accuracy_setting(self):
        scale_frame = ttk.Frame(self.frame_left, width=200, height=400,)
        scale_frame.grid(column=0, row=2, columnspan=2)
        
        hight_acc_label = ttk.Label(scale_frame, text="High")
        hight_acc_label.grid(column=1, row=0, pady=10, padx=5)
        
        self.acc_label = ttk.Label(scale_frame, text="")
        self.acc_label.grid(column=2, row=1, pady=3, padx=5)
        
        self.accuracy_meter = ttk.Scale(scale_frame, 
                        bootstyle="success",
                        length=200,
                        orient="horizontal",
                        command=self._scaler_acc,
                        )
        
        self.accuracy_meter.set(0.3)
        self.accuracy_meter.grid(column=2, row=0, pady=10,)
        
        low_acc_label = ttk.Label(scale_frame, text="Low")
        low_acc_label.grid(column=3, row=0, pady=10, padx=5)
    
    def _display_left_fram_progress_bar(self):
        self.progress_bar_start = ttk.Progressbar(self.frame_left, 
                                   bootstyle="success-striped", 
                                   mode='indeterminate',
                                   )
        self.progress_bar_start.grid(column=0, row=3, padx=5 ,pady=10, columnspan=2, sticky="ew")
        self.progress_bar_start.grid_remove()
    
    def _append_bottom_tree(self):
        # Clear the Treeview
        for item in self.my_tree.get_children():
            self.my_tree.delete(item)

        # Set the Treeview headings
        self.my_tree.heading("e_first_name", text="English First Name")
        self.my_tree.heading("e_last_name", text="English Last Name")
        self.my_tree.heading("f_first_name", text="Farsi First Name")
        self.my_tree.heading("f_last_name", text="Farsi Last Name")
        self.my_tree.heading("date", text="Date")
        self.my_tree.heading("time", text="Time")
        self.my_tree.heading("jalali_date", text="Jalali Date")

        # Define the column widths
        self.my_tree.column("e_first_name", anchor=CENTER, width=150)
        self.my_tree.column("e_last_name", anchor=CENTER, width=150)
        self.my_tree.column("f_first_name", anchor=CENTER, width=150)
        self.my_tree.column("f_last_name", anchor=CENTER, width=150)
        self.my_tree.column("date", anchor=CENTER, width=100)
        self.my_tree.column("time", anchor=CENTER, width=100)
        self.my_tree.column("jalali_date", anchor=CENTER, width=150)

        # Fetch the data
        detailed_records = sqlit_setup.get_detailed_entrance_records()

        # Insert the data into the Treeview
        for record in detailed_records:
            self.my_tree.insert('', END, values=record)
    
    def _bottom_view_tree(self):
        bot_scroll = ttk.Scrollbar(self.frame_bottom,
                               orient="vertical",
                               bootstyle="primary round")
        bot_scroll.pack(side="right", fill="y")
        
        columns = ("e_first_name", "e_last_name", "f_first_name", "f_last_name", "date", "time", "jalali_date")
        self.my_tree = ttk.Treeview(self.frame_bottom, 
                            bootstyle="success",
                            columns=columns,
                            show="headings",
                            yscrollcommand= bot_scroll
                            )
        self.my_tree.pack(fill=BOTH, expand=1)
    
    def _add_user(self):
        self.add_new_user_label.config(text="Please wait ...")
        self.add_new_user_button.config(state=DISABLED)
        self.progress_bar_right_frame.grid()
        self.progress_bar_right_frame.start()

        def add_user_thread():
            result = face_detect.main()
            self.add_new_user_label.config(text="Done, Now you can start the app" if result else "Failed to add new user")
            self.add_new_user_button.config(state=NORMAL)
            self.progress_bar_right_frame.stop()
            self.progress_bar_right_frame.grid_remove()

        threading.Thread(target=add_user_thread).start()
        
    # --------------------------------------------------------------------- Right Frame
    
    def _export_all_data(self):    
    
        self.progress_bar_right_frame.grid()
        self.progress_bar_right_frame.start()
        
        def do_export_all_result():
            today_list = sqlit_setup.export_all_data()
            data = []

            # Convert set of tuples to list of dictionaries
            print(today_list)
            for record in today_list:
                data.append({
                    'en memeber name': record[0] + " " + record[1],
                    'fr memebr name': record[2] + " " + record[3],
                    'Date': record[4],
                    'Time': record[5],
                    'Jalali': record[6]
                })

            # Create a DataFrame
            df = pd.DataFrame(data)

            # Save to Excel file
            excel_filename = f"total_data.xlsx"
            df.to_excel(excel_filename, index=False)
            self.progress_bar_right_frame.stop()
            self.progress_bar_right_frame.grid_remove()
            
        threading.Thread(target=do_export_all_result).start()
    
    def _add_member_to_db(self):
        e_first_name = self.e_first_name_entry.get()
        e_last_name = self.e_last_name_entry.get()
        f_first_name = self.f_first_name_entry.get()
        f_last_name = self.f_last_name_entry.get()

        if e_first_name and e_last_name and f_first_name and f_last_name:
            sqlit_setup.add_member(e_first_name, e_last_name, f_first_name, f_last_name)

            # Clear the entry fields after adding
            self.e_first_name_entry.delete(0, ttk.END)
            self.e_last_name_entry.delete(0, ttk.END)
            self.f_first_name_entry.delete(0, ttk.END)
            self.f_last_name_entry.delete(0, ttk.END)
    
    def _export_result(self):
        self.progress_bar_right_frame.grid()
        self.progress_bar_right_frame.start()
        
        def do_export_result():
            today_list = sqlit_setup.exoprt_all()
            data = []

            # Convert set of tuples to list of dictionaries
            for record in today_list:
                data.append({
                    'en memeber name': record[0] + " " + record[1],
                    'fr memebr name': record[2] + " " + record[3],
                    'Date': record[4],
                    'Time': record[5],
                    'Jalali': record[6]
                })

            # Create a DataFrame
            df = pd.DataFrame(data)

            # Save to Excel file
            today_date = datetime.now().strftime("%Y-%m-%d")
            excel_filename = f"entrance_records_{today_date}.xlsx"
            df.to_excel(excel_filename, index=False)
            self.progress_bar_right_frame.stop()
            self.progress_bar_right_frame.grid_remove()
            
        threading.Thread(target=do_export_result).start()
    
    def _load_members_data(self, tree):
        """Load members data into the Treeview."""
        records = sqlit_setup.select_all_memebrs()

        for row in tree.get_children():
            tree.delete(row)

        for record in records:
            tree.insert('', 'end', values=record)
            
    def _edit_member(self, tree, e_first_name_entry, e_last_name_entry, f_first_name, f_last_name):
        """Edit a member's details."""
        selected_item = tree.selection()
        if not selected_item:
            Messagebox.show_info("Select a member", "Please select a member to edit.")
            return

        member_id = tree.item(selected_item, 'values')[0]
        new_e_first_name = e_first_name_entry.get()
        new_e_last_name = e_last_name_entry.get()
        new_f_first_name = f_first_name.get()
        new_f_last_name = f_last_name.get()

        if not new_e_first_name:
            new_e_first_name = tree.item(selected_item, 'values')[1]
        
        if not new_e_last_name:
            new_e_last_name = tree.item(selected_item, 'values')[2]
        
        if not new_f_first_name:
            new_f_first_name = tree.item(selected_item, 'values')[3]
            
        if not new_f_last_name:
            new_f_last_name = tree.item(selected_item, 'values')[4]
        

        sqlit_setup.edit_memebrs(new_e_first_name, new_e_last_name, new_f_first_name, new_f_last_name, member_id)

        self._load_members_data(tree)
        Messagebox.show_info("Success", "Member updated successfully.") 
    
    def _dispalye_right_notebook(self):
        self.add_user_notebook = ttk.Notebook(self.frame_right, bootstyle="success")
        self.add_user_notebook.grid(column=0, row=1, pady=10)
        
        self.tab_add_user = ttk.Frame(self.add_user_notebook, )
        self.tab_edit_user = ttk.Frame(self.add_user_notebook)
        
    def _display_add_user_bootn_right_frame(self):
        self.add_new_user_button = ttk.Button(self.tab_add_user,
                             text="Add New User",
                             bootstyle="primary",
                             command=self._add_user)
    
        self.add_new_user_button.grid(column=0, row=5, padx=5, pady=5)
        
    def _display_export_button_right_frame(self):
        self.export_button = ttk.Button(self.tab_add_user,
                             text="Export Result",
                             bootstyle="primary",
                             command=self._export_result)
    
        self.export_button.grid(column=1, row=5, padx=5, pady=10)
    
    def _diplay_add_new_user_label_right_frame(self):
        self.add_new_user_label = ttk.Label(self.tab_add_user, text="")
        self.add_new_user_label.grid(column=0, row=6, padx=5, pady=5, columnspan=3, sticky="we")
    
    def _diplay_progress_bar_right_frame(self):
        self.progress_bar_right_frame = ttk.Progressbar(self.tab_add_user, 
                                   bootstyle="success-striped", 
                                   mode='indeterminate',
                                   )
        self.progress_bar_right_frame.grid(column=0, row=7, padx=7, pady=10, columnspan=2, sticky="ew")
        self.progress_bar_right_frame.grid_remove()
        
    def _display_add_user_ui_right_frame(self):
        e_first_name_label = ttk.Label(self.tab_add_user, text="English First Name:")
        e_first_name_label.grid(column=0, row=0, padx=10, pady=5, sticky="w")

        self.e_first_name_entry = ttk.Entry(self.tab_add_user, width=20)
        self.e_first_name_entry.grid(column=1, row=0, padx=10, pady=5, sticky="ew")

        e_last_name_label = ttk.Label(self.tab_add_user, text="English Last Name:")
        e_last_name_label.grid(column=0, row=1, padx=10, pady=5, sticky="w")

        self.e_last_name_entry = ttk.Entry(self.tab_add_user, width=20)
        self.e_last_name_entry.grid(column=1, row=1, padx=10, pady=5, sticky="ew")

        f_first_name_label = ttk.Label(self.tab_add_user, text="Farsi First Name:")
        f_first_name_label.grid(column=3, row=0, padx=10, pady=5, sticky="w")

        self.f_first_name_entry = ttk.Entry(self.tab_add_user, width=20)
        self.f_first_name_entry.grid(column=4, row=0, padx=10, pady=5, sticky="ew")

        f_last_name_label = ttk.Label(self.tab_add_user, text="Farsi Last Name:")
        f_last_name_label.grid(column=3, row=1, padx=10, pady=5, sticky="w")

        self.f_last_name_entry = ttk.Entry(self.tab_add_user, width=20)
        self.f_last_name_entry.grid(column=4, row=1, padx=10, pady=5, sticky="ew")
               
    def _display_add_button_right_frame(self):
        self.add_button = ttk.Button(self.tab_add_user, text="Add Member", command=self._add_member_to_db, bootstyle="primary")
        self.add_button.grid(column=0, row=4, columnspan=2, padx=10, pady=10, sticky="ew")
    
    def _diplay_export_all_right_frame(self):
        self.export_button_all = ttk.Button(self.tab_add_user,
                             text="Export All Data",
                             bootstyle="primary",
                             command=self._export_all_data)
    
        self.export_button_all.grid(column=2, row=5, padx=5, pady=5)
    
    def _display_create_memeber_rf(self):
        
        righ_frame_scroll = ttk.Scrollbar(self.tab_edit_user,
                               orient="vertical",
                               bootstyle="primary round")
        righ_frame_scroll.grid(row=5, column=4, sticky='ns')
    
        columns = ('members_id', 'e_first_name', 'e_last_name', 'f_first_name', 'f_last_name')
        self.right_edit_tree = ttk.Treeview(self.tab_edit_user, columns=columns, show='headings', yscrollcommand=righ_frame_scroll)

        self.right_edit_tree.heading('members_id', text='ID')
        self.right_edit_tree.heading('e_first_name', text='English First Name')
        self.right_edit_tree.heading('e_last_name', text='English Last Name')
        self.right_edit_tree.heading('f_first_name', text='Farsi First Name')
        self.right_edit_tree.heading('f_last_name', text='Farsi Last Name')
        
        self.right_edit_tree.grid(row=5, column=0, columnspan=4, padx=2, pady=10, sticky='nsew')
        
        # self.tab_edit_user.grid_rowconfigure(5, weight=1)
        # self.tab_edit_user.grid_columnconfigure(0, weight=1)
        # self.tab_edit_user.grid_columnconfigure(4, weight=0)
        self._load_members_data(self.right_edit_tree)
        
    def _display_edit_button_lables_rf(self):
        ttk.Label(self.tab_edit_user, text="Edit First Name:").grid(row=6, column=0, padx=5, pady=5, sticky='e')
        self.e_first_name_entry = ttk.Entry(self.tab_edit_user)
        self.e_first_name_entry.grid(row=6, column=1, padx=2, pady=5, sticky='w')

        ttk.Label(self.tab_edit_user, text="Edit Last Name:").grid(row=6, column=2, padx=5, pady=5, sticky='e')
        self.e_last_name_entry = ttk.Entry(self.tab_edit_user)
        self.e_last_name_entry.grid(row=6, column=3, padx=10, pady=5, sticky='w')
        
        ttk.Label(self.tab_edit_user, text="Edit farsi First Name:").grid(row=7, column=0, padx=5, pady=5, sticky='e')
        self.f_first_name_entry = ttk.Entry(self.tab_edit_user)
        self.f_first_name_entry.grid(row=7, column=1, padx=2, pady=5, sticky='w')
        
        ttk.Label(self.tab_edit_user, text="Edit farsi Last Name:").grid(row=7, column=2, padx=5, pady=5, sticky='e')
        self.f_last_name_entry = ttk.Entry(self.tab_edit_user)
        self.f_last_name_entry.grid(row=7, column=3, padx=2, pady=5, sticky='w')

    def _display_edit_user_bottons_rf(self):
        edit_button = ttk.Button(self.tab_edit_user, text="Edit Member", command=lambda: self._edit_member(self.right_edit_tree, self.e_first_name_entry, self.e_last_name_entry, self.f_first_name_entry, self.f_last_name_entry))
        edit_button.grid(row=8, column=0, columnspan=2, pady=10, padx=10, sticky='ew')

        refresh_button = ttk.Button(self.tab_edit_user, text="Refresh List", command=lambda: self._load_members_data(self.right_edit_tree))
        refresh_button.grid(row=8, column=2, columnspan=2, pady=10, padx=10, sticky='ew')
    
    
    # ---------------------------------------------------------- Main Frames         
    def right_frame(self):
        self._dispalye_right_notebook()
        self._display_add_user_bootn_right_frame()
        self._display_export_button_right_frame()
        self._diplay_add_new_user_label_right_frame()
        self._diplay_progress_bar_right_frame()
        self._display_add_user_ui_right_frame()
        self._display_add_button_right_frame()
        self._diplay_export_all_right_frame()
        self._display_create_memeber_rf()
        self._display_edit_button_lables_rf()
        self._display_edit_user_bottons_rf()
        
        
        self.add_user_notebook.add(self.tab_add_user, text="Add User")
        self.add_user_notebook.add(self.tab_edit_user, text="Edit User")

    def left_frame(self):
        self._display_start_recognition()
        self._display_save_image_button()
        self._display_chose_camera()
        self._display_accuracy_setting()
        self._display_left_fram_progress_bar()
    
    def bottom_frame(self):
        self._bottom_view_tree()
        self._append_bottom_tree()

# if __name__ == "__main__":
#     home_page = HomePage()
    
#     home_page.left_frame()
#     home_page.right_frame()
#     home_page.bottom_frame()
    
    
#     home_page.root.mainloop()