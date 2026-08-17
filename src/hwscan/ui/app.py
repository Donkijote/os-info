from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from hwscan.application.export_service import ExportService
from hwscan.application.scan_service import ScanService
from hwscan.ui.view_model import ScanViewModel


class HWScanApp:
    """Development UI. The Linux appliance integration remains a later validation milestone."""

    def __init__(self, root: tk.Tk, fixture_dir: Path) -> None:
        self.root = root
        self.fixture_dir = fixture_dir
        self.view_model = ScanViewModel(ScanService(), ExportService())
        root.title("HWScan USB")
        root.geometry("1024x768")
        root.configure(background="#F3F5F7")
        self.status = tk.StringVar(value="Ready")
        self.summary = tk.StringVar(value="No scan has been run.")
        self._build()

    def _build(self) -> None:
        frame = ttk.Frame(self.root, padding=32)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="HWScan USB", font=("Helvetica", 26, "bold")).pack(anchor="w")
        ttk.Label(frame, textvariable=self.status, font=("Helvetica", 15)).pack(
            anchor="w", pady=(8, 24)
        )
        ttk.Label(frame, textvariable=self.summary, justify="left", wraplength=850).pack(
            anchor="w", pady=(0, 24)
        )
        actions = ttk.Frame(frame)
        actions.pack(anchor="w")
        ttk.Button(actions, text="Scan fixture", command=self._scan).pack(side="left", padx=(0, 12))
        ttk.Button(actions, text="Export report", command=self._export).pack(side="left")

    def _scan(self) -> None:
        self.status.set("Scanning…")
        self.root.update_idletasks()
        try:
            report = self.view_model.scan_fixtures(self.fixture_dir)
        except Exception as error:
            self.status.set("Scan failed")
            messagebox.showerror("HWScan", str(error))
            return
        system = report.system
        cpu = report.cpus[0] if report.cpus else {}
        self.summary.set(
            f"{system.get('manufacturer')} {system.get('product_name')}\n"
            f"Serial: {system.get('serial_number')}\n"
            f"CPU: {cpu.get('model_name')}\n"
            f"Memory: {report.memory.get('installed_bytes')} bytes\n"
            f"Storage devices: {len(report.storage)}"
        )
        self.status.set(self.view_model.state.value.replace("_", " ").title())

    def _export(self) -> None:
        if self.view_model.report is None:
            messagebox.showwarning("HWScan", "Run a scan first.")
            return
        selected = filedialog.askdirectory(title="Choose report destination")
        if not selected:
            return
        result = self.view_model.export(Path(selected))
        self.status.set("Exported")
        messagebox.showinfo("HWScan", f"Saved:\n{result.json_path.name}\n{result.excel_path.name}")


def run(fixture_dir: Path) -> None:
    root = tk.Tk()
    HWScanApp(root, fixture_dir)
    root.mainloop()
