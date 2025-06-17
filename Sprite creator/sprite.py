import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class SpriteSheetCutter:
    def __init__(self, root, image_path):
        self.root = root
        self.original_image = Image.open(image_path)

        # Resize image to fit within screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        max_width = int(screen_width * 0.9)
        max_height = int(screen_height * 0.9)

        ratio = min(max_width / self.original_image.width, max_height / self.original_image.height, 1)
        self.display_image = self.original_image.resize(
            (int(self.original_image.width * ratio), int(self.original_image.height * ratio)),
            Image.Resampling.LANCZOS
        )
        self.ratio = ratio  # Store resize ratio for later cropping math

        self.tk_image = ImageTk.PhotoImage(self.display_image)
        self.canvas = tk.Canvas(root, width=self.display_image.width, height=self.display_image.height, cursor="cross")
        self.canvas.pack()

        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_image)

        self.start_x = None
        self.start_y = None
        self.rect = None
        self.selections = []

        self.canvas.bind("<ButtonPress-1>", self.start_selection)
        self.canvas.bind("<B1-Motion>", self.update_selection)
        self.canvas.bind("<ButtonRelease-1>", self.save_selection)

    def start_selection(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def update_selection(self, event):
        curr_x = self.canvas.canvasx(event.x)
        curr_y = self.canvas.canvasy(event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, curr_x, curr_y)

    def save_selection(self, event):
        end_x = self.canvas.canvasx(event.x)
        end_y = self.canvas.canvasy(event.y)

        # Convert selection from display size back to original size
        box = (
            int(min(self.start_x, end_x) / self.ratio),
            int(min(self.start_y, end_y) / self.ratio),
            int(max(self.start_x, end_x) / self.ratio),
            int(max(self.start_y, end_y) / self.ratio),
        )

        cropped = self.original_image.crop(box)
        filename = f"element_{len(self.selections)+1}.png"
        cropped.save(filename)
        self.selections.append(box)
        print(f"Saved {filename} at {box}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    image_path = filedialog.askopenfilename(title="Select your sprite sheet")
    if image_path:
        root.deiconify()
        root.title("Sprite Sheet Cutter (Resizable)")
        app = SpriteSheetCutter(root, image_path)
        root.mainloop()
