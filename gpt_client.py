from g4f.client import Client

class GPTClient:
    def __init__(self):
        self.client = Client()

    def ask_for_deletable_files(self, folder_contents_path):
        try:
            folder_contents = folder_contents_path.read_text(encoding="utf-8")
            prompt = (
                "You are a system cleaner assistant.\n"
                "Your task is to analyze a list of files and folders and identify items that can be SAFELY deleted "
                "without harming the operating system or important applications.\n\n"
                "Rules:\n"
                "DO NOT recommend deleting system-related folders (e.g. NVIDIA, AMD, Intel, Microsoft)\n"
                "DO NOT recommend deleting files or folders from Windows or Program Files\n"
                "DO NOT recommend deleting folders related to drivers, core services, or active apps\n"
                "You MAY suggest deletion of temporary files, old logs, cache folders, or unused application data\n"
                "If unsure — skip the item (do NOT include it)\n\n"
                "Output format:\n"
                "Return ONLY the names of files or folders that are safe to delete\n"
                "One item per line\n"
                "Append [folder] at the end if it's a folder\n"
                "Do NOT use dashes, bullets, or any extra symbols\n"
                "If nothing is safe to delete, return 'null'\n\n"
                "List to analyze:\n"
                f"{folder_contents}"
            )

            print("Sending request to GPT...")
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                web_search=False
            )

            answer = response.choices[0].message.content
            print(f"GPT Response received: {len(answer)} characters")

            file_names = [
                line.strip() for line in answer.splitlines()
                if line.strip()
                and line.strip().lower() != 'null'
                and line.strip() != '```'
                and not line.strip().startswith("- ")
            ]

            return file_names, answer

        except Exception as e:
            print(f"Error getting GPT response: {e}")
            return [], f"Error: {str(e)}"