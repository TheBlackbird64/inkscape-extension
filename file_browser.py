import tkinter as tk
from tkinter import ttk, messagebox, font
from datetime import datetime
import requests

TIMEOUT = 10  # seconds, Inkscape is blocked while the window is open


def format_size(size):
    if size < 1024:
        return f"{size} o"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} Ko"
    return f"{size / (1024 * 1024):.1f} Mo"


class FileBrowser:
    """Window listing the files of the server: choose the one to pull, or delete some of them"""

    def __init__(self, url, headers, current_id=None):
        self.url = url
        self.headers = headers
        self.current_id = current_id  # id of the server file linked to the document
        self.chosen_id = None  # file to pull once the window is closed
        self.current_deleted = False  # the linked file has been deleted: the document must be unlinked

        self.root = tk.Tk()
        self.root.title("Fichiers du serveur")
        self.root.minsize(420, 260)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        self.link_label = ttk.Label(self.root)
        self.link_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))

        # list of the files
        frame = ttk.Frame(self.root)
        frame.grid(row=1, column=0, sticky="nsew", padx=10)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(frame, columns=("modified", "size"), selectmode="browse")
        self.tree.heading("#0", text="Fichier")
        self.tree.heading("modified", text="Modifié le")
        self.tree.heading("size", text="Taille")
        self.tree.column("#0", width=260)
        self.tree.column("modified", width=130, stretch=False)
        self.tree.column("size", width=80, stretch=False, anchor="e")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        bold = font.nametofont("TkDefaultFont").copy()
        bold.configure(weight="bold")
        self.tree.tag_configure("linked", font=bold)

        self.tree.bind("<<TreeviewSelect>>", lambda e: self.update_buttons())
        self.tree.bind("<Double-1>", lambda e: self.open())
        self.tree.bind("<Return>", lambda e: self.open())
        self.tree.bind("<Delete>", lambda e: self.delete())

        # buttons
        buttons = ttk.Frame(self.root)
        buttons.grid(row=2, column=0, sticky="ew", padx=10, pady=10)
        buttons.columnconfigure(2, weight=1)

        ttk.Button(buttons, text="Rafraîchir", command=self.refresh).grid(row=0, column=0)
        self.delete_button = ttk.Button(buttons, text="Supprimer", command=self.delete)
        self.delete_button.grid(row=0, column=1, padx=(5, 0))
        ttk.Button(buttons, text="Fermer", command=self.root.destroy).grid(row=0, column=3)
        self.open_button = ttk.Button(buttons, text="Ouvrir", command=self.open)
        self.open_button.grid(row=0, column=4, padx=(5, 0))

        self.status = ttk.Label(self.root, foreground="gray")
        self.status.grid(row=3, column=0, sticky="w", padx=10, pady=(0, 10))

        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def run(self):
        """Show the window until it is closed, then read chosen_id and current_deleted"""
        self.update_link_label()
        self.refresh()

        # centered, and in front of Inkscape
        width, height = 560, 400
        x = (self.root.winfo_screenwidth() - width) // 2
        y = (self.root.winfo_screenheight() - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after_idle(self.root.attributes, "-topmost", False)
        self.root.focus_force()
        self.tree.focus_set()

        self.root.mainloop()

    def is_linked(self, id):
        return self.current_id is not None and id == self.current_id and not self.current_deleted

    def update_link_label(self):
        if self.current_id is None:
            text = "Document non lié : choisissez le fichier du serveur à récupérer."
        elif self.current_deleted:
            text = f"Le fichier lié '{self.current_id}' a été supprimé : le document sera délié."
        else:
            text = f"Document lié à : {self.current_id}"
        self.link_label.configure(text=text)

    def update_buttons(self):
        state = "normal" if self.selected() is not None else "disabled"
        self.open_button.configure(state=state)
        self.delete_button.configure(state=state)

    def selected(self):
        selection = self.tree.selection()
        return selection[0] if selection else None

    def refresh(self):
        """Ask the server the list of its files"""
        self.tree.delete(*self.tree.get_children())

        try:
            res = requests.get(self.url + "list", headers=self.headers, timeout=TIMEOUT)
            res.raise_for_status()
            files = res.json()
        except requests.RequestException as e:
            self.status.configure(text=f"Impossible de récupérer la liste des fichiers : {e}")
            self.update_buttons()
            return

        for file in files:
            linked = self.is_linked(file["id"])
            self.tree.insert(
                "", "end",
                iid=file["id"],
                text=file["id"] + ("  (lié)" if linked else ""),
                values=(datetime.fromtimestamp(file["modified"]).strftime("%d/%m/%Y %H:%M"), format_size(file["size"])),
                tags=("linked",) if linked else (),
            )

        # select the linked file, or the most recent one
        children = self.tree.get_children()
        if self.is_linked(self.current_id) and self.current_id in children:
            to_select = self.current_id
        else:
            to_select = children[0] if children else None
        if to_select is not None:
            self.tree.selection_set(to_select)
            self.tree.focus(to_select)
            self.tree.see(to_select)

        self.status.configure(text=f"{len(files)} fichier(s) sur le serveur")
        self.update_buttons()

    def open(self):
        """Close the window: the selected file will be pulled in the document"""
        id = self.selected()
        if id is None:
            return
        self.chosen_id = id
        self.root.destroy()

    def delete(self):
        """Delete the selected file on the server, after confirmation"""
        id = self.selected()
        if id is None:
            return

        message = f"Supprimer définitivement '{id}' du serveur ?"
        if self.is_linked(id):
            message += "\n\nC'est le fichier lié au document ouvert : le document sera délié."
        if not messagebox.askyesno("Supprimer", message, icon="warning", parent=self.root):
            return

        try:
            res = requests.delete(self.url + "delete", params={"id": id}, headers=self.headers, timeout=TIMEOUT)
            res.raise_for_status()
        except requests.RequestException as e:
            messagebox.showerror("Erreur", f"Impossible de supprimer '{id}' : {e}", parent=self.root)
        else:
            if self.is_linked(id):
                self.current_deleted = True
                self.update_link_label()

        self.refresh()
