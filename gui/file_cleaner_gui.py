import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading

from gpt_client import GPTClient
from file_manager import FileManager

from pathlib import Path

class FileCleanerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("File Cleaner - GPT Analysis")
        self.root.geometry("1100x800")
        
        self.file_manager = FileManager()
        self.gpt_client = GPTClient()
        self.deletable_file_vars = {}  # {file_name: BooleanVar}
        self.keep_file_vars = {}  # {file_name: BooleanVar}
        
        self.create_widgets()
        self.load_saved_folders()
        
    def create_widgets(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Секция выбора папок
        folders_frame = ttk.LabelFrame(main_frame, text="Folder Selection", padding="5")
        folders_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Кнопки управления папками
        folder_buttons_frame = ttk.Frame(folders_frame)
        folder_buttons_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(folder_buttons_frame, text="Add Folder", command=self.add_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_buttons_frame, text="Remove Selected", command=self.remove_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_buttons_frame, text="Clear All", command=self.clear_folders).pack(side=tk.LEFT, padx=5)
        
        # Список выбранных папок
        self.folders_listbox = tk.Listbox(folders_frame, height=4)
        self.folders_listbox.grid(row=1, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Скроллбар для списка папок
        folders_scrollbar = ttk.Scrollbar(folders_frame, orient="vertical", command=self.folders_listbox.yview)
        folders_scrollbar.grid(row=1, column=2, sticky=(tk.N, tk.S))
        self.folders_listbox.config(yscrollcommand=folders_scrollbar.set)
        
        # Кнопка анализа
        analyze_btn = ttk.Button(main_frame, text="Analyze Folders", command=self.analyze_folders)
        analyze_btn.grid(row=1, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        # Прогресс бар
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=2, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        # Статус
        self.status_label = ttk.Label(main_frame, text="Ready - Please select folders to analyze")
        self.status_label.grid(row=3, column=0, columnspan=2, pady=5)
        
        # Контейнер для двух блоков файлов
        files_container = ttk.Frame(main_frame)
        files_container.grid(row=4, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # БЛОК 1: Файлы для удаления
        deletable_frame = ttk.LabelFrame(files_container, text="Files to Delete (Recommended)", padding="5")
        deletable_frame.grid(row=0, column=0, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Кнопки управления для файлов к удалению
        deletable_buttons_frame = ttk.Frame(deletable_frame)
        deletable_buttons_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(deletable_buttons_frame, text="Select All", command=self.select_all_deletable).pack(side=tk.LEFT, padx=5)
        ttk.Button(deletable_buttons_frame, text="Deselect All", command=self.deselect_all_deletable).pack(side=tk.LEFT, padx=5)
        ttk.Button(deletable_buttons_frame, text="Delete Selected", command=self.delete_selected).pack(side=tk.RIGHT, padx=5)
        
        # Скроллируемый фрейм для файлов к удалению
        deletable_canvas = tk.Canvas(deletable_frame, height=250)
        deletable_scrollbar = ttk.Scrollbar(deletable_frame, orient="vertical", command=deletable_canvas.yview)
        self.deletable_scrollable_frame = ttk.Frame(deletable_canvas)
        
        self.deletable_scrollable_frame.bind(
            "<Configure>",
            lambda e: deletable_canvas.configure(scrollregion=deletable_canvas.bbox("all"))
        )
        
        deletable_canvas.create_window((0, 0), window=self.deletable_scrollable_frame, anchor="nw")
        deletable_canvas.configure(yscrollcommand=deletable_scrollbar.set)
        
        deletable_canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        deletable_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # БЛОК 2: Файлы для сохранения
        keep_frame = ttk.LabelFrame(files_container, text="Files to Keep (Not Recommended for Deletion)", padding="5")
        keep_frame.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Кнопки управления для файлов к сохранению
        keep_buttons_frame = ttk.Frame(keep_frame)
        keep_buttons_frame.grid(row=0, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        ttk.Button(keep_buttons_frame, text="Select All", command=self.select_all_keep).pack(side=tk.LEFT, padx=5)
        ttk.Button(keep_buttons_frame, text="Deselect All", command=self.deselect_all_keep).pack(side=tk.LEFT, padx=5)
        ttk.Button(keep_buttons_frame, text="Delete Selected", command=self.delete_selected_keep).pack(side=tk.RIGHT, padx=5)
        
        # Скроллируемый фрейм для файлов к сохранению
        keep_canvas = tk.Canvas(keep_frame, height=250)
        keep_scrollbar = ttk.Scrollbar(keep_frame, orient="vertical", command=keep_canvas.yview)
        self.keep_scrollable_frame = ttk.Frame(keep_canvas)
        
        self.keep_scrollable_frame.bind(
            "<Configure>",
            lambda e: keep_canvas.configure(scrollregion=keep_canvas.bbox("all"))
        )
        
        keep_canvas.create_window((0, 0), window=self.keep_scrollable_frame, anchor="nw")
        keep_canvas.configure(yscrollcommand=keep_scrollbar.set)
        
        keep_canvas.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        keep_scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        
        # Область для показа деталей файла
        details_frame = ttk.LabelFrame(main_frame, text="File Details", padding="5")
        details_frame.grid(row=5, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.details_text = scrolledtext.ScrolledText(details_frame, height=8, width=70)
        self.details_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Настройка растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(4, weight=1)
        main_frame.rowconfigure(5, weight=1)
        folders_frame.columnconfigure(0, weight=1)
        
        # Настройка для контейнера файлов
        files_container.columnconfigure(0, weight=1)
        files_container.columnconfigure(1, weight=1)
        files_container.rowconfigure(0, weight=1)
        
        # Настройка для блоков файлов
        deletable_frame.columnconfigure(0, weight=1)
        deletable_frame.rowconfigure(1, weight=1)
        keep_frame.columnconfigure(0, weight=1)
        keep_frame.rowconfigure(1, weight=1)
        
        details_frame.columnconfigure(0, weight=1)
        details_frame.rowconfigure(0, weight=1)
    
    def load_saved_folders(self):
        """
        Загружает сохраненные папки из конфигурации
        """
        if self.file_manager.load_config():
            self.update_folders_listbox()
            self.status_label.config(text=f"Loaded {len(self.file_manager.folder_paths)} folders from config")
    
    def update_folders_listbox(self):
        """
        Обновляет список папок в GUI
        """
        self.folders_listbox.delete(0, tk.END)
        for folder_path in self.file_manager.folder_paths:
            self.folders_listbox.insert(tk.END, str(folder_path))
    
    def add_folder(self):
        """
        Добавляет новую папку через диалог выбора
        """
        folder_path = filedialog.askdirectory(title="Select folder to analyze")
        if folder_path:
            # Проверяем, что папка еще не добавлена
            if folder_path not in [str(path) for path in self.file_manager.folder_paths]:
                self.file_manager.folder_paths.append(Path(folder_path))
                self.file_manager.save_config()
                self.update_folders_listbox()
                self.status_label.config(text=f"Added folder: {folder_path}")
            else:
                messagebox.showinfo("Info", "This folder is already in the list")
    
    def remove_folder(self):
        """
        Удаляет выбранную папку из списка
        """
        selection = self.folders_listbox.curselection()
        if selection:
            index = selection[0]
            removed_folder = self.file_manager.folder_paths.pop(index)
            self.file_manager.save_config()
            self.update_folders_listbox()
            self.status_label.config(text=f"Removed folder: {removed_folder}")
        else:
            messagebox.showwarning("Warning", "Please select a folder to remove")
    
    def clear_folders(self):
        """
        Очищает весь список папок
        """
        if self.file_manager.folder_paths:
            result = messagebox.askyesno("Confirm", "Are you sure you want to clear all folders?")
            if result:
                self.file_manager.folder_paths.clear()
                self.file_manager.save_config()
                self.update_folders_listbox()
                self.status_label.config(text="All folders cleared")
        else:
            messagebox.showinfo("Info", "No folders to clear")
    
    def analyze_folders(self):
        """
        Анализирует папки в отдельном потоке
        """
        if not self.file_manager.folder_paths:
            messagebox.showwarning("Warning", "Please select at least one folder to analyze")
            return
        
        thread = threading.Thread(target=self._analyze_folders_thread)
        thread.daemon = True
        thread.start()
        
    def _analyze_folders_thread(self):
        """
        Основная логика анализа в отдельном потоке
        """
        try:
            self.root.after(0, lambda: self.progress.start())
            self.root.after(0, lambda: self.status_label.config(text="Gathering folder contents..."))
            
            # Собираем содержимое папок
            folder_contents_path = self.file_manager.gather_folder_contents()
            
            self.root.after(0, lambda: self.status_label.config(text="Asking GPT for analysis..."))
            
            # Получаем анализ от GPT
            deletable_files, gpt_response = self.gpt_client.ask_for_deletable_files(folder_contents_path)
            
            # Получаем файлы для сохранения
            keep_files = self.file_manager.get_not_deletable_files(deletable_files)
            
            # Сохраняем ответ
            self.file_manager.save_deletable_files_list(gpt_response)
            
            # Обновляем GUI
            self.root.after(0, lambda: self.update_file_lists(deletable_files, keep_files))
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.status_label.config(
                text=f"Analysis complete. Found {len(deletable_files)} files to delete, {len(keep_files)} files to keep."
            ))
            
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.progress.stop())
            self.root.after(0, lambda: self.status_label.config(text=f"Error: {error_msg}"))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Analysis failed: {error_msg}"))
    
    def update_file_lists(self, deletable_files, keep_files):
        """
        Обновляет списки файлов в GUI
        """
        # Очищаем старые списки
        for widget in self.deletable_scrollable_frame.winfo_children():
            widget.destroy()
        for widget in self.keep_scrollable_frame.winfo_children():
            widget.destroy()
        
        self.deletable_file_vars = {}
        self.keep_file_vars = {}
        
        # Создаем чекбоксы для файлов к удалению
        for i, file_name in enumerate(deletable_files):
            if file_name.strip():  # Пропускаем пустые строки
                var = tk.BooleanVar()
                self.deletable_file_vars[file_name] = var
                
                frame = ttk.Frame(self.deletable_scrollable_frame)
                frame.grid(row=i, column=0, sticky=(tk.W, tk.E), padx=5, pady=2)
                
                # Определяем цвет для папок
                display_text = file_name
                if file_name.endswith('[folder]'):
                    display_text = file_name.replace('[folder]', ' [FOLDER]')
                
                checkbox = ttk.Checkbutton(frame, text=display_text, variable=var)
                checkbox.grid(row=0, column=0, sticky=tk.W)
                
                # Кнопка для показа деталей
                details_btn = ttk.Button(frame, text="Info", width=6,
                                       command=lambda fn=file_name: self.show_file_details(fn))
                details_btn.grid(row=0, column=1, sticky=tk.E, padx=5)
                
                frame.columnconfigure(0, weight=1)
        
        # Создаем чекбоксы для файлов к сохранению
        for i, file_name in enumerate(keep_files):
            if file_name.strip():  # Пропускаем пустые строки
                var = tk.BooleanVar()
                self.keep_file_vars[file_name] = var
                
                frame = ttk.Frame(self.keep_scrollable_frame)
                frame.grid(row=i, column=0, sticky=(tk.W, tk.E), padx=5, pady=2)
                
                # Определяем цвет для папок
                display_text = file_name
                if file_name.endswith('[folder]'):
                    display_text = file_name.replace('[folder]', ' [FOLDER]')
                
                checkbox = ttk.Checkbutton(frame, text=display_text, variable=var)
                checkbox.grid(row=0, column=0, sticky=tk.W)
                
                # Кнопка для показа деталей
                details_btn = ttk.Button(frame, text="Info", width=6,
                                       command=lambda fn=file_name: self.show_file_details(fn))
                details_btn.grid(row=0, column=1, sticky=tk.E, padx=5)
                
                frame.columnconfigure(0, weight=1)
    
    def show_file_details(self, file_name):
        """
        Показывает детали файла или папки
        """
        details = self.file_manager.get_file_info(file_name)
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(1.0, f"Item: {file_name}\n\n{details}")
    
    def select_all_deletable(self):
        """
        Выбирает все чекбоксы в блоке файлов для удаления
        """
        for var in self.deletable_file_vars.values():
            var.set(True)
    
    def deselect_all_deletable(self):
        """
        Снимает выделение со всех чекбоксов в блоке файлов для удаления
        """
        for var in self.deletable_file_vars.values():
            var.set(False)
    
    def select_all_keep(self):
        """
        Выбирает все чекбоксы в блоке файлов для сохранения
        """
        for var in self.keep_file_vars.values():
            var.set(True)
    
    def deselect_all_keep(self):
        """
        Снимает выделение со всех чекбоксов в блоке файлов для сохранения
        """
        for var in self.keep_file_vars.values():
            var.set(False)
    
    def delete_selected(self):
        """
        Удаляет выбранные файлы из блока "рекомендуемые для удаления"
        """
        selected_files = [file_name for file_name, var in self.deletable_file_vars.items() if var.get()]
        self._delete_files(selected_files, "deletable")
    
    def delete_selected_keep(self):
        """
        Удаляет выбранные файлы из блока "рекомендуемые для сохранения"
        """
        selected_files = [file_name for file_name, var in self.keep_file_vars.items() if var.get()]
        
        # Дополнительное предупреждение для файлов из блока "сохранения"
        result = messagebox.askyesno("Additional Warning", 
                                   f"You are about to delete {len(selected_files)} files from the 'Keep' list.\n"
                                   f"These files were NOT recommended for deletion by GPT.\n\n"
                                   f"Are you absolutely sure you want to proceed?")
        
        if result:
            self._delete_files(selected_files, "keep")
    
    def _delete_files(self, selected_files, source_type):
        """
        Общая логика удаления файлов
        """
        if not selected_files:
            messagebox.showwarning("Warning", "No files/folders selected for deletion.")
            return
        
        # Подтверждение
        result = messagebox.askyesno("Confirm Deletion", 
                                   f"Are you sure you want to delete {len(selected_files)} files/folders?")
        
        if result:
            try:
                deleted_count, errors = self.file_manager.delete_files(selected_files)
                
                message = f"Successfully deleted {deleted_count} files/folders."
                if errors:
                    message += f"\n\nErrors:\n" + "\n".join(errors[:10])  # Показываем первые 10 ошибок
                
                messagebox.showinfo("Deletion Complete", message)
                
                # Обновляем статус
                self.status_label.config(text=f"Deleted {deleted_count} files/folders")
                
                # Убираем удаленные файлы из соответствующего списка
                if source_type == "deletable":
                    for file_name in selected_files:
                        if file_name in self.deletable_file_vars:
                            del self.deletable_file_vars[file_name]
                else:  # keep
                    for file_name in selected_files:
                        if file_name in self.keep_file_vars:
                            del self.keep_file_vars[file_name]
                
                # Обновляем список (перезапускаем анализ)
                self.analyze_folders()
                
            except Exception as e:
                messagebox.showerror("Error", f"Deletion failed: {str(e)}")

def main():
    root = tk.Tk()
    app = FileCleanerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()