# SmartFileCleaner

SmartFileCleaner is a graphical application for analyzing and safely deleting files and folders using AI. The program helps determine which files can be deleted without harming the system and which should be kept, based on the contents of selected folders and AI analysis.

---

## Features

* Select multiple folders for analysis
* Automatic collection of folder contents
* Intelligent analysis powered by GPT-4 through [gpt4free](https://github.com/xtekky/gpt4free) API client
* Categorization of files into recommended for deletion and for keeping
* View detailed information about each file/folder
* Bulk selection and deletion of files with confirmation
* Intuitive and responsive GUI built with Tkinter
* Runs in a separate thread for smooth interface performance

---

## Usage

Run the application with the command:

```bash
python main.py
```

### Main steps:

1. Add one or more folders for analysis.
2. Click the **Analyze Folders** button to start the analysis.
3. After analysis, a list of files recommended for deletion and for keeping will be displayed.
4. Review file details, select the files you want, and delete them.

---

## Project Structure

* `main.py` — application entry point
* `file_manager.py` — file and folder management logic
* `gpt_client.py` — interaction with the GPT API via gpt4free
* `gui/` — interface modules (main window, status bar, file lists, etc.)
* `temp_data/` — configuration files and saved data

---

## Requirements

* Python 3.10+
* `g4f[all]` (GPT4Free client library)

Install dependencies with:

```bash
pip install -U g4f[all]
```

---

## About GPT4Free

This project uses the [gpt4free](https://github.com/xtekky/gpt4free) library written by @xtekky to interact with various free GPT providers in a unified way.

**Important legal notice from GPT4Free:**

By using GPT4Free, you agree to its [GNU General Public License v3](https://www.gnu.org/licenses/gpl-3.0.html). The author is not responsible for usage or forks, and you should comply with the license terms.

GPT4Free serves as a Proof of Concept (PoC) demonstrating multi-provider requests with load balancing and timeout controls.

For more details, updates, and support, please visit the [official GPT4Free repository](https://github.com/xtekky/gpt4free).