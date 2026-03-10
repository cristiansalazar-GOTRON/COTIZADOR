import customtkinter as ctk
from tkinter import messagebox
import json
import os


APP_TITLE = "Cotizador de Equipos de Importacion"

RATES_FILE = r"c:\PROGRAMAS CRISTIAN\COTIZADOR AUTOMATICO\tasas_guardadas.json"

DEFAULTS = {
    "threshold": "2000",
    "low_margin": "30",
    "high_margin": "50",
    "tariff": "10",
    "vat": "19",
}


def to_float(raw_value: str, field_name: str) -> float:
    """Convert text input to float accepting comma or dot."""
    text = raw_value.strip().replace(",", ".")
    if not text:
        raise ValueError(f"El campo '{field_name}' no puede estar vacio.")
    try:
        return float(text)
    except ValueError as exc:
        raise ValueError(f"Valor invalido en '{field_name}'.") from exc


def calculate_values(data: dict) -> dict:
    """Apply the requested business rules and return all result values."""
    total_cost = data["product_cost"] + data["freight_cost"]

    if data["currency"] == "USD":
        cost_cop = total_cost * data["usd_rate"]
    else:
        cost_cop = total_cost * data["eur_rate"]

    margin = data["low_margin"] if total_cost < data["threshold"] else data["high_margin"]

    profit = cost_cop * margin
    base_price = cost_cop + profit
    tariff = cost_cop * data["tariff_percent"]
    subtotal = base_price + tariff
    vat = subtotal * data["vat_percent"]
    final_price = subtotal + vat

    return {
        "total_cost": total_cost,
        "cost_cop": cost_cop,
        "margin": margin,
        "profit": profit,
        "base_price": base_price,
        "tariff": tariff,
        "subtotal": subtotal,
        "vat": vat,
        "final_price": final_price,
    }


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("920x720")
        self.resizable(False, False)
        # bring window to front in case it is hidden
        self.lift()
        self.after(100, lambda: self.focus_force())

        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        self.currency_var = ctk.StringVar(value="USD")
        self.origin_var = ctk.StringVar(value="China")
        self.entries = {}
        self.result_labels = {}

        # load saved rates
        self.saved_rates = self._load_rates()

        self._build_ui()
        self._reset_results()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        # use a scrollable frame to contain all sections
        container = ctk.CTkScrollableFrame(self, width=900, height=700)
        container.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        container.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(container, text=APP_TITLE, font=ctk.CTkFont(size=28, weight="bold"))
        title.grid(row=0, column=0, padx=20, pady=(18, 10), sticky="w")

        # store a reference so that sub-builders know where to place their widgets
        self._current_parent = container
        self._build_purchase_section()
        self._build_config_section()
        self._build_results_section()
        self._build_action_buttons()
        # remove temporary parent
        del self._current_parent

        # set saved rates in entries
        if self.saved_rates.get("usd_rate"):
            self.entries["usd_rate"].insert(0, self.saved_rates["usd_rate"])
        if self.saved_rates.get("eur_rate"):
            self.entries["eur_rate"].insert(0, self.saved_rates["eur_rate"])

    def _build_purchase_section(self):
        parent = getattr(self, '_current_parent', self)
        frame = ctk.CTkFrame(parent, corner_radius=10)
        frame.grid(row=1, column=0, padx=20, pady=8, sticky="ew")
        frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(frame, text="1) Datos de Compra", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=14, pady=(12, 8), sticky="w"
        )

        self._add_option(frame, "Moneda", self.currency_var, ["USD", "EUR"], 1, 0)
        self._add_option(frame, "Origen", self.origin_var, ["China", "Europa", "USA", "Latinoamerica", "Otro"], 1, 1)

        self._add_entry(frame, "product_cost", "Costo del producto (USD o EUR)", 2, 0)
        self._add_entry(frame, "freight_cost", "Costo de flete (USD o EUR)", 2, 1)
        self._add_entry(frame, "usd_rate", "Tasa USD a COP (COP por USD)", 3, 0)
        self._add_entry(frame, "eur_rate", "Tasa EUR a COP (COP por EUR)", 3, 1)

    def _build_config_section(self):
        parent = getattr(self, '_current_parent', self)
        frame = ctk.CTkFrame(parent, corner_radius=10)
        frame.grid(row=2, column=0, padx=20, pady=8, sticky="ew")
        frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(frame, text="2) Configuracion (Editable)", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, columnspan=3, padx=14, pady=(12, 8), sticky="w"
        )

        self._add_entry(frame, "threshold", "Umbral de margen", 1, 0, DEFAULTS["threshold"])
        self._add_entry(frame, "low_margin", "Margen bajo (%)", 1, 1, DEFAULTS["low_margin"])
        self._add_entry(frame, "high_margin", "Margen alto (%)", 1, 2, DEFAULTS["high_margin"])
        self._add_entry(frame, "tariff", "Arancel importacion (%)", 2, 0, DEFAULTS["tariff"])
        self._add_entry(frame, "vat", "IVA (%)", 2, 1, DEFAULTS["vat"])

    def _build_results_section(self):
        parent = getattr(self, '_current_parent', self)
        frame = ctk.CTkFrame(parent, corner_radius=10)
        frame.grid(row=3, column=0, padx=20, pady=8, sticky="ew")
        frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(frame, text="3) Resultados", font=ctk.CTkFont(size=18, weight="bold")).grid(
            row=0, column=0, columnspan=2, padx=14, pady=(12, 8), sticky="w"
        )

        rows = [
            ("Total cost (moneda extranjera)", "total_cost"),
            ("Total cost en COP", "cost_cop"),
            ("Margen aplicado", "margin"),
            ("Ganancia en COP", "profit"),
            ("Precio antes de impuestos", "base_price"),
            ("Valor arancel", "tariff"),
            ("Subtotal", "subtotal"),
            ("Valor IVA", "vat"),
        ]

        for row, (text, key) in enumerate(rows, start=1):
            ctk.CTkLabel(frame, text=f"{text}:", anchor="w").grid(row=row, column=0, padx=18, pady=3, sticky="w")
            label = ctk.CTkLabel(frame, text="0.00", anchor="e")
            label.grid(row=row, column=1, padx=18, pady=3, sticky="e")
            self.result_labels[key] = label

        ctk.CTkLabel(frame, text="FINAL PRICE:", font=ctk.CTkFont(size=20, weight="bold")).grid(
            row=10, column=0, padx=18, pady=(12, 16), sticky="w"
        )
        final_label = ctk.CTkLabel(
            frame,
            text="COP 0.00",
            text_color="#0F4C81",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        final_label.grid(row=10, column=1, padx=18, pady=(12, 16), sticky="e")
        self.result_labels["final_price"] = final_label

    def _build_action_buttons(self):
        parent = getattr(self, '_current_parent', self)
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=4, column=0, padx=20, pady=(6, 20), sticky="ew")
        frame.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(frame, text="Calcular", command=self.on_calculate).grid(
            row=0, column=0, padx=(0, 4), pady=4, sticky="ew"
        )
        ctk.CTkButton(frame, text="Guardar Tasas", command=self.on_save_rates).grid(
            row=0, column=1, padx=(4, 4), pady=4, sticky="ew"
        )
        ctk.CTkButton(frame, text="Limpiar", command=self.on_clear).grid(
            row=0, column=2, padx=(4, 0), pady=4, sticky="ew"
        )

    def _add_entry(self, parent, key, label, row, col, default=""):
        ctk.CTkLabel(parent, text=label).grid(row=row * 2 - 1, column=col, padx=14, pady=(6, 2), sticky="w")
        entry = ctk.CTkEntry(parent)
        entry.grid(row=row * 2, column=col, padx=14, pady=(0, 8), sticky="ew")
        if default:
            entry.insert(0, default)
        self.entries[key] = entry

    def _add_option(self, parent, label, variable, values, row, col):
        ctk.CTkLabel(parent, text=label).grid(row=row * 2 - 1, column=col, padx=14, pady=(6, 2), sticky="w")
        ctk.CTkOptionMenu(parent, variable=variable, values=values).grid(
            row=row * 2, column=col, padx=14, pady=(0, 8), sticky="ew"
        )

    def _reset_results(self):
        for key, label in self.result_labels.items():
            if key == "margin":
                label.configure(text="0.00%")
            elif key == "final_price":
                label.configure(text="COP 0.00")
            else:
                label.configure(text="0.00")

    def _load_rates(self):
        if os.path.exists(RATES_FILE):
            try:
                with open(RATES_FILE, 'r') as f:
                    return json.load(f)
            except:
                return {"usd_rate": "", "eur_rate": ""}
        return {"usd_rate": "", "eur_rate": ""}

    def _save_rates(self):
        rates = {
            "usd_rate": self.entries["usd_rate"].get(),
            "eur_rate": self.entries["eur_rate"].get(),
        }
        try:
            with open(RATES_FILE, 'w') as f:
                json.dump(rates, f)
            messagebox.showinfo("Guardado", "Tasas guardadas correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron guardar las tasas: {e}")

    def on_save_rates(self):
        self._save_rates()

    def _read_form(self):
        values = {
            "currency": self.currency_var.get(),
            "origin": self.origin_var.get(),
            "product_cost": to_float(self.entries["product_cost"].get(), "Costo del producto"),
            "freight_cost": to_float(self.entries["freight_cost"].get(), "Costo de flete"),
            "usd_rate": to_float(self.entries["usd_rate"].get(), "Tasa USD a COP"),
            "eur_rate": to_float(self.entries["eur_rate"].get(), "Tasa EUR a COP"),
            "threshold": to_float(self.entries["threshold"].get(), "Umbral de margen"),
            "low_margin": to_float(self.entries["low_margin"].get(), "Margen bajo") / 100,
            "high_margin": to_float(self.entries["high_margin"].get(), "Margen alto") / 100,
            "tariff_percent": to_float(self.entries["tariff"].get(), "Arancel") / 100,
            "vat_percent": to_float(self.entries["vat"].get(), "IVA") / 100,
        }

        # validate the required rate for the selected currency
        if values["currency"] == "USD":
            if values["usd_rate"] <= 0:
                raise ValueError("La tasa USD debe ser mayor a 0.")
        else:
            if values["eur_rate"] <= 0:
                raise ValueError("La tasa EUR debe ser mayor a 0.")

        if values["product_cost"] < 0 or values["freight_cost"] < 0:
            raise ValueError("Los costos no pueden ser negativos.")

        return values

    def _render_results(self, result):
        # show total_cost with two decimals (foreign currency)
        self.result_labels["total_cost"].configure(text=f"{result['total_cost']:,.2f}")
        # COP fields tend to be large integers; drop unnecessary decimals
        for key in ("cost_cop", "profit", "base_price", "tariff", "subtotal", "vat", "final_price"):
            value = result[key]
            # if the value is effectively an integer, format without decimals
            if abs(value - round(value)) < 0.005:
                text = f"COP {value:,.0f}"
            else:
                text = f"COP {value:,.2f}"
            self.result_labels[key].configure(text=text)
        self.result_labels["margin"].configure(text=f"{result['margin'] * 100:.2f}%")

    def on_calculate(self):
        try:
            form_data = self._read_form()
            result = calculate_values(form_data)
            self._render_results(result)
        except ValueError as error:
            messagebox.showerror("Error de validacion", str(error))

    def on_clear(self):
        for key in ["product_cost", "freight_cost"]:
            self.entries[key].delete(0, "end")

        # reload saved rates
        self.entries["usd_rate"].delete(0, "end")
        if self.saved_rates.get("usd_rate"):
            self.entries["usd_rate"].insert(0, self.saved_rates["usd_rate"])
        self.entries["eur_rate"].delete(0, "end")
        if self.saved_rates.get("eur_rate"):
            self.entries["eur_rate"].insert(0, self.saved_rates["eur_rate"])

        self.entries["threshold"].delete(0, "end")
        self.entries["threshold"].insert(0, DEFAULTS["threshold"])
        self.entries["low_margin"].delete(0, "end")
        self.entries["low_margin"].insert(0, DEFAULTS["low_margin"])
        self.entries["high_margin"].delete(0, "end")
        self.entries["high_margin"].insert(0, DEFAULTS["high_margin"])
        self.entries["tariff"].delete(0, "end")
        self.entries["tariff"].insert(0, DEFAULTS["tariff"])
        self.entries["vat"].delete(0, "end")
        self.entries["vat"].insert(0, DEFAULTS["vat"])

        self.currency_var.set("USD")
        self.origin_var.set("China")
        self._reset_results()


if __name__ == "__main__":
    app = App()
    app.mainloop()
