# SmartFileCleaner

SmartFileCleaner is a graphical application for analyzing and safely deleting files and folders using AI. The program helps determine which files can be deleted without harming the system and which should be kept, based on the contents of selected folders and AI analysis.

---

## Features

- Select multiple folders for analysis
- Automatic collection of folder contents
- Intelligent analysis powered by GPT-4
- Categorization of files into recommended for deletion and for keeping
- View detailed information about each file/folder
- Bulk selection and deletion of files with confirmation
- Intuitive and responsive GUI built with Tkinter
- Runs in a separate thread for smooth interface performance

---

## Usage

Run the application with the command:

```bash
python main.py
````

### Main steps:

1. Add one or more folders for analysis.
2. Click the **Analyze Folders** button to start the analysis.
3. After analysis, a list of files recommended for deletion and for keeping will be displayed.
4. Review file details, select the files you want, and delete them.

---

## Project Structure

* `main.py` — application entry point
* `file_manager.py` — file and folder management logic
* `gpt_client.py` — interaction with the GPT API
* `gui/` — interface modules (main window, status bar, file lists, etc.)
* `config/` — configuration files and saved data