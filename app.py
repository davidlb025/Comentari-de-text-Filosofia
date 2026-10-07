"""
Comentari de text · Filosofia PAU Catalunya
-------------------------------------------
Requisits:  pip install customtkinter
Execució:   python comentari_pau.py

Plantilla generada (en català):
  Aquest és un fragment de [obra], de [autor], on es tracta el tema /
  es tracten els temes [temes]. El problema que ens planteja és: [problema]?
  [Autor] afirma que [tesi]. En aquest fragment l'autor comença plantejant
  [desenvolupament]...
"""

import re
import customtkinter as ctk
from tkinter import filedialog, messagebox

ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")

# ──────────────────────────────────────────────────────────────────────────
# DADES  (edita aquí autors i temes si el currículum de la PAU canvia)
# ──────────────────────────────────────────────────────────────────────────

# Nom del tema  ->  forma per inserir a la frase ("el tema de ...")
TEMES = {
    "EPISTEMOLOGIA": "de l'epistemologia",
    "METAFÍSICA": "de la metafísica",
    "ANTROPOLOGIA": "de l'antropologia",
    "ÈTICA": "de l'ètica",
    "FILOSOFIA POLÍTICA": "de la filosofia política",
}

TOTS = list(TEMES.keys())

# Autors PAU Catalunya: nom complet -> cognom curt, gènere i temes que treballa
AUTORS = {
    "Plató": {"curt": "Plató", "f": False, "temes": TOTS},
    "René Descartes": {
        "curt": "Descartes", "f": False,
        "temes": ["EPISTEMOLOGIA", "METAFÍSICA", "ANTROPOLOGIA"],
    },
    "David Hume": {
        "curt": "Hume", "f": False,
        "temes": ["EPISTEMOLOGIA", "METAFÍSICA", "ANTROPOLOGIA"],
    },
    "Immanuel Kant": {
        "curt": "Kant", "f": False,
        "temes": ["ÈTICA", "ANTROPOLOGIA"],
    },
    "John Stuart Mill": {
        "curt": "Mill", "f": False,
        "temes": ["ÈTICA", "FILOSOFIA POLÍTICA"],
    },
    "Friedrich Nietzsche": {
        "curt": "Nietzsche", "f": False,
        "temes": ["ÈTICA", "METAFÍSICA", "ANTROPOLOGIA"],
    },
    "Martha Nussbaum": {
        "curt": "Nussbaum", "f": True,
        "temes": ["ÈTICA", "ANTROPOLOGIA", "FILOSOFIA POLÍTICA"],
    },
}

# Interval orientatiu de paraules (editable des de la interfície)
MIN_PARAULES = 250
MAX_PARAULES = 450


# ──────────────────────────────────────────────────────────────────────────
# UTILITATS
# ──────────────────────────────────────────────────────────────────────────

def paraules(text: str) -> int:
    return len(re.findall(r"\S+", text))


def prep_de(nom: str) -> str:
    """'de Plató' / "d'Immanuel Kant" """
    return ("d'" if nom[0].lower() in "aeiouàèéíòóúh" else "de ") + nom


def llista(items):
    if len(items) == 1:
        return items[0]
    return ", ".join(items[:-1]) + " i " + items[-1]


def net(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


# ──────────────────────────────────────────────────────────────────────────
# APLICACIÓ
# ──────────────────────────────────────────────────────────────────────────

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Comentari de text · Filosofia PAU Catalunya")
        self.geometry("1320x860")
        self.minsize(1080, 720)

        self.grid_columnconfigure(0, weight=5, uniform="cols")
        self.grid_columnconfigure(1, weight=6, uniform="cols")
        self.grid_rowconfigure(0, weight=1)

        self.temes_widgets = {}
        self.plain_text = ""

        self._build_form()
        self._build_preview()
        self._apply_tag_colors()
        self.on_autor()

    # ── Formulari (columna esquerra) ──────────────────────────────────────
    def _label(self, parent, text, hint=None):
        ctk.CTkLabel(
            parent, text=text, anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(fill="x", padx=14, pady=(14, 0 if hint else 4))
        if hint:
            ctk.CTkLabel(
                parent, text=hint, anchor="w", text_color=("gray40", "gray65"),
                font=ctk.CTkFont(size=12),
            ).pack(fill="x", padx=14, pady=(0, 4))

    def _textbox(self, parent, height):
        tb = ctk.CTkTextbox(parent, height=height, wrap="word",
                            font=ctk.CTkFont(size=14))
        tb.pack(fill="x", padx=14)
        tb.bind("<KeyRelease>", lambda e: self.refresh())
        tb.bind("<<Paste>>", lambda e: self.after(50, self.refresh))
        tb.bind("<<Cut>>", lambda e: self.after(50, self.refresh))
        return tb

    def _build_form(self):
        form = ctk.CTkScrollableFrame(self, label_text="  Dades del comentari",
                                      label_anchor="w",
                                      label_font=ctk.CTkFont(size=15, weight="bold"))
        form.grid(row=0, column=0, sticky="nsew", padx=(14, 7), pady=14)

        # 1. Obra
        self._label(form, "1 · Obra", "Aquest és un fragment de …")
        self.obra_var = ctk.StringVar()
        self.obra_var.trace_add("write", lambda *a: self.refresh())
        ctk.CTkEntry(form, textvariable=self.obra_var, height=34,
                     placeholder_text="Ex.: Meditacions metafísiques"
                     ).pack(fill="x", padx=14)

        # 2. Autor
        self._label(form, "2 · Autor/a", "… de [autor/a]")
        self.autor_var = ctk.StringVar(value="Selecciona un autor/a…")
        self.cb_autor = ctk.CTkComboBox(
            form, values=list(AUTORS.keys()), variable=self.autor_var,
            state="readonly", height=34, command=self.on_autor,
        )
        self.cb_autor.pack(fill="x", padx=14)

        # 3. Temes
        self._label(
            form, "3 · Tema/es",
            "on es tracta el tema / es tracten els temes …  "
            "(només s'activen els que treballa l'autor/a)",
        )
        box = ctk.CTkFrame(form, fg_color="transparent")
        box.pack(fill="x", padx=14)
        for t in TEMES:
            var = ctk.BooleanVar(value=False)
            cb = ctk.CTkCheckBox(box, text=t, variable=var,
                                 command=self.refresh, state="disabled")
            cb.pack(anchor="w", pady=3)
            self.temes_widgets[t] = (cb, var)

        # 4. Problema
        self._label(form, "4 · Problema",
                    "El problema que ens planteja és: … ?   (no cal escriure el «?»)")
        self.t_problema = self._textbox(form, 80)

        # 5. Tesi
        self._label(form, "5 · Tesi de l'autor/a",
                    "[Autor] afirma que …   (no cal escriure el punt final)")
        self.t_tesi = self._textbox(form, 100)

        # 6. Desenvolupament
        self._label(form, "6 · Desenvolupament",
                    "En aquest fragment l'autor comença plantejant …  "
                    "(estructura, idees principals, conceptes, context, valoració…)")
        self.t_desenv = self._textbox(form, 260)

        ctk.CTkLabel(form, text="").pack(pady=4)

    # ── Previsualització + comptador (columna dreta) ──────────────────────
    def _build_preview(self):
        right = ctk.CTkFrame(self)
        right.grid(row=0, column=1, sticky="nsew", padx=(7, 14), pady=14)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        head = ctk.CTkFrame(right, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 4))
        head.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(head, text="Comentari resultant", anchor="w",
                     font=ctk.CTkFont(size=16, weight="bold")
                     ).grid(row=0, column=0, sticky="w")
        self.seg_mode = ctk.CTkSegmentedButton(
            head, values=["Automàtic", "Clar", "Fosc"], command=self._set_mode)
        self.seg_mode.set("Automàtic")
        self.seg_mode.grid(row=0, column=1, sticky="e")

        self.preview = ctk.CTkTextbox(right, wrap="word",
                                      font=ctk.CTkFont(size=15), spacing2=4)
        self.preview.grid(row=1, column=0, sticky="nsew", padx=14, pady=6)

        ctk.CTkLabel(
            right, anchor="w", text_color=("gray40", "gray65"),
            font=ctk.CTkFont(size=12),
            text="Blau = fórmula fixa de la plantilla · Gris = camp pendent · "
                 "Negre/blanc = el teu text",
        ).grid(row=2, column=0, sticky="w", padx=16)

        # Comptador
        cnt = ctk.CTkFrame(right)
        cnt.grid(row=3, column=0, sticky="ew", padx=14, pady=(8, 6))
        cnt.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(cnt, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 0))
        top.grid_columnconfigure(0, weight=1)
        self.lbl_total = ctk.CTkLabel(top, text="0 paraules", anchor="w",
                                      font=ctk.CTkFont(size=22, weight="bold"))
        self.lbl_total.grid(row=0, column=0, sticky="w")

        lim = ctk.CTkFrame(top, fg_color="transparent")
        lim.grid(row=0, column=1, sticky="e")
        ctk.CTkLabel(lim, text="Interval orientatiu:").pack(side="left", padx=(0, 6))
        self.min_var = ctk.StringVar(value=str(MIN_PARAULES))
        self.max_var = ctk.StringVar(value=str(MAX_PARAULES))
        for v in (self.min_var, self.max_var):
            v.trace_add("write", lambda *a: self.refresh())
        ctk.CTkEntry(lim, textvariable=self.min_var, width=56).pack(side="left")
        ctk.CTkLabel(lim, text=" – ").pack(side="left")
        ctk.CTkEntry(lim, textvariable=self.max_var, width=56).pack(side="left")

        self.bar = ctk.CTkProgressBar(cnt, height=14)
        self.bar.grid(row=1, column=0, sticky="ew", padx=12, pady=8)
        self.bar.set(0)

        self.lbl_estat = ctk.CTkLabel(cnt, text="", anchor="w",
                                      font=ctk.CTkFont(size=13))
        self.lbl_estat.grid(row=2, column=0, sticky="w", padx=12)
        self.lbl_parts = ctk.CTkLabel(cnt, text="", anchor="w",
                                      text_color=("gray40", "gray65"),
                                      font=ctk.CTkFont(size=12))
        self.lbl_parts.grid(row=3, column=0, sticky="w", padx=12, pady=(0, 2))
        self.lbl_falta = ctk.CTkLabel(cnt, text="", anchor="w", justify="left",
                                      wraplength=560, text_color="#D97706",
                                      font=ctk.CTkFont(size=12))
        self.lbl_falta.grid(row=4, column=0, sticky="w", padx=12, pady=(0, 10))

        # Botons
        btns = ctk.CTkFrame(right, fg_color="transparent")
        btns.grid(row=4, column=0, sticky="ew", padx=14, pady=(0, 12))
        btns.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkButton(btns, text="Copiar", command=self.copiar
                      ).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkButton(btns, text="Desar com a .txt", command=self.desar
                      ).grid(row=0, column=1, sticky="ew", padx=6)
        ctk.CTkButton(btns, text="Netejar tot", fg_color="#B91C1C",
                      hover_color="#991B1B", command=self.netejar
                      ).grid(row=0, column=2, sticky="ew", padx=(6, 0))

    # ── Aparença ──────────────────────────────────────────────────────────
    def _set_mode(self, value):
        ctk.set_appearance_mode(
            {"Automàtic": "system", "Clar": "light", "Fosc": "dark"}[value])
        self.after(50, self._apply_tag_colors)

    def _apply_tag_colors(self):
        dark = ctk.get_appearance_mode() == "Dark"
        self.preview.tag_config("fix", foreground="#60A5FA" if dark else "#1D4ED8")
        self.preview.tag_config("ph", foreground="#9CA3AF")

    # ── Lògica ────────────────────────────────────────────────────────────
    def on_autor(self, _=None):
        info = AUTORS.get(self.autor_var.get())
        disponibles = info["temes"] if info else []
        for t, (cb, var) in self.temes_widgets.items():
            if t in disponibles:
                cb.configure(state="normal")
            else:
                var.set(False)
                cb.configure(state="disabled")
        self.refresh()

    def _get(self, tb):
        return tb.get("1.0", "end").strip()

    def construir(self):
        """Retorna (segments, dict_de_paraules_per_part, llista_de_camps_que_falten)."""
        obra = net(self.obra_var.get())
        autor = self.autor_var.get()
        info = AUTORS.get(autor)
        temes = [t for t, (_, v) in self.temes_widgets.items() if v.get()]
        problema = net(self._get(self.t_problema)).rstrip("?").strip()
        tesi = net(self._get(self.t_tesi)).rstrip(".").strip()
        desenv = self._get(self.t_desenv)

        segs = []
        falta = []

        def fix(t):
            segs.append((t, "fix"))

        def usr(t, ph, nom):
            if t:
                segs.append((t, "usr"))
            else:
                segs.append((ph, "ph"))
                falta.append(nom)

        fix('Aquest és un fragment de "')
        usr(obra, "[obra]", "obra")
        fix('", ')
        if info:
            segs.append((prep_de(autor), "usr"))
        else:
            segs.append(("de [autor/a]", "ph"))
            falta.append("autor/a")
        fix(', on es tracta el tema ' if len(temes) <= 1
            else ', on es tracten els temes ')
        if temes:
            segs.append((llista([TEMES[t] for t in temes]), "usr"))
        else:
            segs.append(("[tema]", "ph"))
            falta.append("tema")
        fix(". El problema que ens planteja és: ")
        usr(problema, "[problema]", "problema")
        fix("? ")
        curt = info["curt"] if info else "[Autor/a]"
        segs.append((curt, "usr" if info else "ph"))
        fix(" afirma que ")
        usr(tesi, "[tesi]", "tesi")
        fix(". En aquest fragment ")
        fix("l'autora" if (info and info["f"]) else "l'autor")
        fix(" comença plantejant ")
        usr(desenv, "[desenvolupament]", "desenvolupament")

        parts = {
            "Problema": paraules(problema),
            "Tesi": paraules(tesi),
            "Desenvolupament": paraules(desenv),
        }
        return segs, parts, falta

    def refresh(self, *_):
        segs, parts, falta = self.construir()

        self.preview.configure(state="normal")
        self.preview.delete("1.0", "end")
        for text, tag in segs:
            if tag == "usr":
                self.preview.insert("end", text)
            else:
                self.preview.insert("end", text, tag)
        self.preview.configure(state="disabled")

        self.plain_text = "".join(t for t, _ in segs)
        total = paraules("".join(t for t, tag in segs if tag != "ph"))

        # Límits
        def to_int(s, d):
            try:
                return max(0, int(s))
            except ValueError:
                return d
        mn = to_int(self.min_var.get(), MIN_PARAULES)
        mx = max(to_int(self.max_var.get(), MAX_PARAULES), mn + 1)

        self.lbl_total.configure(text=f"{total} paraules")
        self.bar.set(min(total / mx, 1))
        if total < mn:
            color, msg = "#DC2626", f"Et falten ≈ {mn - total} paraules per arribar al mínim."
        elif total <= mx:
            color, msg = "#16A34A", "Dins de l'interval orientatiu."
        else:
            color, msg = "#D97706", f"T'has passat ≈ {total - mx} paraules del màxim."
        self.bar.configure(progress_color=color)
        self.lbl_estat.configure(text=msg, text_color=color)

        self.lbl_parts.configure(
            text="Paraules per apartat →  " +
                 "   ·   ".join(f"{k}: {v}" for k, v in parts.items()))
        self.lbl_falta.configure(
            text=("Pendent: " + ", ".join(falta) + ".") if falta else "")

    # ── Accions ───────────────────────────────────────────────────────────
    def _confirmar_si_incomplet(self):
        _, _, falta = self.construir()
        if falta:
            return messagebox.askyesno(
                "Comentari incomplet",
                "Encara falten: " + ", ".join(falta) + ".\nVols continuar igualment?")
        return True

    def copiar(self):
        if not self._confirmar_si_incomplet():
            return
        self.clipboard_clear()
        self.clipboard_append(self.plain_text)
        messagebox.showinfo("Copiat", "Comentari copiat al porta-retalls.")

    def desar(self):
        if not self._confirmar_si_incomplet():
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text", "*.txt")],
            initialfile="comentari_filosofia.txt")
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.plain_text)

    def netejar(self):
        if not messagebox.askyesno("Netejar", "Segur que vols esborrar-ho tot?"):
            return
        self.obra_var.set("")
        self.autor_var.set("Selecciona un autor/a…")
        for tb in (self.t_problema, self.t_tesi, self.t_desenv):
            tb.delete("1.0", "end")
        self.on_autor()


if __name__ == "__main__":
    App().mainloop()