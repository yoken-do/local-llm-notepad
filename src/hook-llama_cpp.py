from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('llama_cpp', subdir='lib')

# To compile, run the following: 
# pyinstaller --onefile --noconsole --additional-hooks-dir=. main.py
