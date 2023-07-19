import tkinter as tk
import asyncio
import threading
from app import App

if __name__ == "__main__":
    root = tk.Tk()
    root.title("TABARNAK V2")
    root.geometry("600x550")  # Set the initial size of the window

    # Grid layout
    root.grid_rowconfigure(0, weight=1)
    root.grid_columnconfigure([0, 1, 2], weight=1)

    loop = asyncio.get_event_loop()
    app = App(root, loop)
    threading.Thread(target=loop.run_forever, daemon=True).start()
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()
