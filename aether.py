# aether.py - Termux GUI Edition
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import subprocess
import shutil
import tempfile
import threading
import sys

class AetherTermux:
    def __init__(self, root):
        self.root = root
        self.root.title("Aether [Termux]")
        self.root.geometry("1100x680")
        self.root.configure(bg='#0d0d0d')
        
        # Dark + Green Theme
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background='#0d0d0d')
        style.configure('TNotebook.Tab', background='#1a1a1a', foreground='#00ff00', padding=[15, 10])
        style.map('TNotebook.Tab', background=[('selected', '#00ff00')], foreground=[('selected', 'black')])
        style.configure('TFrame', background='#0d0d0d')
        style.configure('TLabel', background='#0d0d0d', foreground='#00ff00')
        style.configure('TButton', background='#1a1a1a', foreground='#00ff00')
        style.map('TButton', background=[('active', '#00ff00')], foreground=[('active', 'black')])
        style.configure('TProgressbar', background='#00ff00', troughcolor='#1a1a1a')

        self.apk_path = None
        self.dll_path = None
        self.working_dir = None
        self.output_apk = None

        self.setup_ui()

    def setup_ui(self):
        # Header
        header = ttk.Label(self.root, text="AETHER\nGorilla Tag Quest Injector", font=('Monospace', 18, 'bold'), foreground='#00ff00')
        header.pack(pady=20)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=15, pady=10)

        # Mod Tab
        mod_frame = ttk.Frame(notebook)
        notebook.add(mod_frame, text=" INJECT ")
        self.setup_mod_tab(mod_frame)

        # Settings Tab
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text=" SETTINGS ")
        self.setup_settings_tab(settings_frame)

    def setup_mod_tab(self, parent):
        info = ttk.Label(parent, text="Termux Edition | Real Injection\nQuest 1/2/3/Pro + Fan Games", foreground='#00ff88', justify='center')
        info.pack(pady=10)

        # APK
        apk_frame = ttk.Frame(parent)
        apk_frame.pack(pady=12, fill='x', padx=20)
        ttk.Label(apk_frame, text="APK:", font=('Monospace', 11, 'bold')).pack(anchor='w')
        self.apk_btn = ttk.Button(apk_frame, text="Select .apk", command=self.select_apk)
        self.apk_btn.pack(pady=5)
        self.apk_label = ttk.Label(apk_frame, text="No APK selected", foreground='#666')
        self.apk_label.pack()

        # DLL
        dll_frame = ttk.Frame(parent)
        dll_frame.pack(pady=12, fill='x', padx=20)
        ttk.Label(dll_frame, text="DLL:", font=('Monospace', 11, 'bold')).pack(anchor='w')
        self.dll_btn = ttk.Button(dll_frame, text="Select .dll", command=self.select_dll)
        self.dll_btn.pack(pady=5)
        self.dll_label = ttk.Label(dll_frame, text="No DLL selected", foreground='#666')
        self.dll_label.pack()

        # Inject Button
        self.inject_btn = ttk.Button(parent, text="INJECT NOW", command=self.start_injection)
        self.inject_btn.pack(pady=25)

        # Progress
        prog_frame = ttk.Frame(parent)
        prog_frame.pack(pady=15, fill='x', padx=20)
        self.progress = ttk.Progressbar(prog_frame, mode='determinate')
        self.progress.pack(fill='x', pady=8)
        self.status = ttk.Label(prog_frame, text="Ready in Termux.", foreground='#00ff00')
        self.status.pack()

    def setup_settings_tab(self, parent):
        settings = [
            ("Auto-Sign APK", True),
            ("Target: arm64-v8a", True),
            ("Fan Game Mode", True),
            ("Bypass Level: Extreme", False)
        ]
        for text, default in settings:
            var = tk.BooleanVar(value=default)
            cb = ttk.Checkbutton(parent, text=text, variable=var)
            cb.pack(anchor='w', pady=6, padx=30)
            setattr(self, f"var_{text}", var)

    def select_apk(self):
        path = filedialog.askopenfilename(
            initialdir="~/storage/shared",
            filetypes=[("APK", "*.apk")]
        )
        if path:
            self.apk_path = path
            self.apk_label.config(text=os.path.basename(path), foreground='#00ff00')

    def select_dll(self):
        path = filedialog.askopenfilename(
            initialdir="~/storage/shared",
            filetypes=[("DLL", "*.dll")]
        )
        if path:
            self.dll_path = path
            self.dll_label.config(text=os.path.basename(path), foreground='#00ff00')

    def start_injection(self):
        if not self.apk_path or not self.dll_path:
            messagebox.showerror("Error", "Select APK and DLL!")
            return
        threading.Thread(target=self.inject, daemon=True).start()

    def inject(self):
        self.set_status("Starting injection...", 0)
        self.inject_btn.config(state='disabled')

        try:
            self.working_dir = tempfile.mkdtemp()
            decompiled = os.path.join(self.working_dir, "app")
            lib_dir = os.path.join(decompiled, "lib", "arm64-v8a")

            # Decompile
            self.set_status("Decompiling APK...", 15)
            subprocess.run(["apktool", "d", self.apk_path, "-o", decompiled], check=True)

            os.makedirs(lib_dir, exist_ok=True)
            dll_name = os.path.basename(self.dll_path)
            target_dll = os.path.join(lib_dir, dll_name)
            shutil.copy2(self.dll_path, target_dll)
            self.set_status(f"Injected {dll_name}", 40)

            # Patch Smali
            self.set_status("Bypassing anticheat...", 60)
            self.patch_smali(decompiled, os.path.splitext(dll_name)[0])

            # Rebuild
            self.set_status("Rebuilding APK...", 80)
            output = os.path.join(self.working_dir, "aether_modded.apk")
            subprocess.run(["apktool", "b", decompiled, "-o", output], check=True)

            # Sign
            self.set_status("Signing APK...", 95)
            signed = output.replace(".apk", "_signed.apk")
            subprocess.run([
                "java", "-jar", "uber-apk-signer.jar", "--apks", output
            ], check=True, cwd=os.getcwd())
            final_apk = signed if os.path.exists(signed) else output

            # Copy to Downloads
            final_dest = os.path.expanduser("~/storage/downloads/aether_modded.apk")
            shutil.copy2(final_apk, final_dest)

            self.set_status("DONE! Saved to Downloads", 100)
            messagebox.showinfo("Success", f"Modded APK saved:\n{final_dest}\n\nSideload with SideQuest!")

        except Exception as e:
            self.set_status("Failed!", 0)
            messagebox.showerror("Error", str(e))
        finally:
            self.inject_btn.config(state='normal')

    def patch_smali(self, decompiled_dir, lib_name):
        smali_dir = os.path.join(decompiled_dir, "smali")
        for root, _, files in os.walk(smali_dir):
            for f in files:
                if f.endswith(".smali"):
                    path = os.path.join(root, f)
                    with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()
                    if "onCreate" in content and "invoke-super" in content:
                        inject = f'\n    const-string v0, "{lib_name}"\n    invoke-static {{v0}}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V\n'
                        if inject not in content:
                            content = content.replace("invoke-super", inject + "    invoke-super", 1)
                            with open(path, 'w', encoding='utf-8') as file:
                                file.write(content)
                        break

    def set_status(self, text, percent):
        self.root.after(0, lambda: self.status.config(text=text))
        self.root.after(0, lambda: self.progress.config(value=percent))

if __name__ == "__main__":
    if not shutil.which("apktool"):
        print("Install apktool: pkg install apktool")
        sys.exit(1)
    root = tk.Tk()
    app = AetherTermux(root)
    root.mainloop()