import tkinter as tk
import asyncio
import threading
from app import App

if __name__ == "__main__":
    root = tk.Tk()
    loop = asyncio.get_event_loop()
    app = App(root, loop)
    threading.Thread(target=loop.run_forever, daemon=True).start()
    root.protocol("WM_DELETE_WINDOW", app.close)
    root.mainloop()