import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
from datetime import datetime, timedelta
import holidays
from tkinter import messagebox
from calendar import monthrange

class Pracownik:
    def __init__(self, imie):
        self.imie = imie
        self.punkty = 0
        self.dni_wolne = set()
        self.dni_pracy = set()
        self.godziny_tygodniowo = {}
    
    def dodaj_punkty(self, punkty):
        self.punkty += punkty
        
    def wyczysc_harmonogram(self):
        self.dni_pracy.clear()
        self.godziny_tygodniowo.clear()

class HarmonogramGUI(tk.Toplevel):
    def __init__(self, parent, start_date, end_date, pracownicy):
        super().__init__(parent)
        self.title("Harmonogram Pracy")
        self.geometry("1000x600")
        
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(self.main_frame)
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="horizontal", 
                                     command=self.canvas.xview)
        self.scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.canvas.configure(xscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.content_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        
        self.create_headers(start_date, end_date)
        self.fill_schedule(start_date, end_date, pracownicy)
        
        self.content_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def create_headers(self, start_date, end_date):
        ttk.Label(self.content_frame, text="", width=15).grid(row=0, column=0)
        
        current_date = start_date
        col = 1
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            cell = ttk.Label(self.content_frame, text=date_str, width=15)
            cell.grid(row=0, column=col, padx=1, pady=1)
            
            if current_date.weekday() >= 5:
                cell.configure(background='lightgray')
            col += 1
            current_date += timedelta(days=1)

    def fill_schedule(self, start_date, end_date, pracownicy):
        for i, pracownik in enumerate(pracownicy, 1):
            ttk.Label(self.content_frame, text=pracownik.imie, width=15).grid(row=i, column=0)
            
            current_date = start_date
            col = 1
            while current_date <= end_date:
                if current_date in pracownik.dni_pracy:
                    status = "Praca"
                    bg_color = "#90EE90"  # Jasny zielony
                elif current_date in pracownik.dni_wolne:
                    status = "Wolne"
                    bg_color = "#FFB6C1"  # Jasny czerwony
                else:
                    status = ""
                    bg_color = "white"
                
                label = ttk.Label(self.content_frame, text=status, width=15, background=bg_color)
                label.grid(row=i, column=col, padx=1, pady=1)
                
                col += 1
                current_date += timedelta(days=1)

class AplikacjaHarmonogramu(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("System zarządzania czasem pracy")
        self.geometry("1200x800")

        self.pracownicy = [Pracownik(f"Pracownik {i+1}") for i in range(5)]
        self.pl_holidays = holidays.Poland()
        self.aktualny_pracownik = None
        self.start_date = None
        self.end_date = None
        self.wybrane_dni = set()

        self.utworz_interface()

    def utworz_interface(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Lewy panel
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Wybór dat
        dates_frame = ttk.LabelFrame(left_panel, text="Wybór zakresu dat")
        dates_frame.pack(fill=tk.X, pady=5)

        self.start_cal = Calendar(dates_frame, selectmode='day', date_pattern='y-mm-dd')
        self.start_cal.pack(pady=5)
        ttk.Label(dates_frame, text="Data początkowa").pack()

        self.end_cal = Calendar(dates_frame, selectmode='day', date_pattern='y-mm-dd')
        self.end_cal.pack(pady=5)
        ttk.Label(dates_frame, text="Data końcowa").pack()

        ttk.Button(dates_frame, text="Zatwierdź zakres dat", 
                  command=self.zatwierdz_zakres).pack(pady=5)

        # Prawy panel
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Lista pracowników
        workers_frame = ttk.LabelFrame(right_panel, text="Pracownicy")
        workers_frame.pack(fill=tk.X, pady=5)

        for pracownik in self.pracownicy:
            frame = ttk.Frame(workers_frame)
            frame.pack(fill=tk.X, pady=2)
            ttk.Label(frame, text=f"{pracownik.imie} (Punkty: {pracownik.punkty})").pack(side=tk.LEFT)
            ttk.Button(frame, text="Wybierz dni wolne", 
                      command=lambda p=pracownik: self.wybierz_pracownika(p)).pack(side=tk.RIGHT)

        # Kalendarz wyboru dni wolnych
        self.calendar_frame = ttk.LabelFrame(right_panel, text="Wybór dni wolnych")
        self.calendar_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.calendar = Calendar(self.calendar_frame, selectmode='day', date_pattern='y-mm-dd')
        self.calendar.pack(fill=tk.BOTH, expand=True, pady=5)
        self.calendar.bind('<<CalendarSelected>>', self.on_date_select)
        self.calendar.pack_forget()

        # Lista wybranych dni
        self.wybrane_dni_frame = ttk.LabelFrame(right_panel, text="Wybrane dni wolne")
        self.wybrane_dni_frame.pack(fill=tk.X, pady=5)
        self.wybrane_dni_lista = tk.Listbox(self.wybrane_dni_frame, height=5)
        self.wybrane_dni_lista.pack(fill=tk.X, pady=5)
        ttk.Button(self.wybrane_dni_frame, text="Usuń zaznaczony dzień", 
                  command=self.usun_wybrany_dzien).pack(pady=2)

        # Przyciski akcji
        buttons_frame = ttk.Frame(right_panel)
        buttons_frame.pack(fill=tk.X, pady=5)

        ttk.Button(buttons_frame, text="Zapisz dni wolne", 
                  command=self.zapisz_dni_wolne).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Generuj harmonogram", 
                  command=self.generuj_harmonogram).pack(side=tk.LEFT, padx=5)

    def sprawdz_dni_pod_rzad(self, pracownik, data):
        kolejne_dni_pracy = 0
        for i in range(6):
            if data - timedelta(days=i) in pracownik.dni_pracy:
                kolejne_dni_pracy += 1
            else:
                break
        return kolejne_dni_pracy

    def czy_wymaga_odpoczynku(self, pracownik, data):
        if self.sprawdz_dni_pod_rzad(pracownik, data) >= 6:
            for i in range(1, 3):
                next_date = data + timedelta(days=i)
                if next_date in pracownik.dni_pracy:
                    return True
        return False

    def czy_moze_pracowac(self, pracownik, data):
        poprzednie_dni = self.sprawdz_dni_pod_rzad(pracownik, data)
        if poprzednie_dni >= 6:
            return False
        
        for i in range(1, 3):
            if data - timedelta(days=i) in pracownik.dni_pracy and self.sprawdz_dni_pod_rzad(pracownik, data - timedelta(days=i)) >= 6:
                return False
        
        return True

    def przydziel_dni_pracy(self):
        if not self.start_date or not self.end_date:
            messagebox.showerror("Błąd", "Najpierw zatwierdź zakres dat!")
            return False

        # Czyszczenie poprzedniego harmonogramu
        for pracownik in self.pracownicy:
            pracownik.wyczysc_harmonogram()

        # Pierwszy przebieg - zapewnienie minimum 2 pracowników na dzień
        current_date = self.start_date
        while current_date <= self.end_date:
            dostepni = []
            tydzien = current_date.isocalendar()[1]

            for pracownik in self.pracownicy:
                if (current_date not in pracownik.dni_wolne and 
                    self.czy_moze_pracowac(pracownik, current_date)):
                    if tydzien not in pracownik.godziny_tygodniowo:
                        pracownik.godziny_tygodniowo[tydzien] = 0
                    if pracownik.godziny_tygodniowo[tydzien] < 40:
                        dostepni.append(pracownik)

            pracujacy = []
            for pracownik in dostepni[:2]:
                pracujacy.append(pracownik)
                pracownik.dni_pracy.add(current_date)
                pracownik.godziny_tygodniowo[tydzien] += 8
                self.oblicz_punkty(current_date, pracownik)
                
                if self.sprawdz_dni_pod_rzad(pracownik, current_date) >= 6:
                    for i in range(1, 3):
                        next_date = current_date + timedelta(days=i)
                        if next_date <= self.end_date:
                            pracownik.dni_wolne.add(next_date)

            current_date += timedelta(days=1)

        # Drugi przebieg - uzupełnienie do 40h tygodniowo
        current_date = self.start_date
        while current_date <= self.end_date:
            tydzien = current_date.isocalendar()[1]
            
            for pracownik in self.pracownicy:
                if (current_date not in pracownik.dni_wolne and 
                    current_date not in pracownik.dni_pracy and
                    self.czy_moze_pracowac(pracownik, current_date)):
                    
                    if tydzien in pracownik.godziny_tygodniowo and pracownik.godziny_tygodniowo[tydzien] < 40:
                        pracujacy_dzis = [p for p in self.pracownicy if current_date in p.dni_pracy]
                        if len(pracujacy_dzis) >= 2:
                            pracownik.dni_pracy.add(current_date)
                            pracownik.godziny_tygodniowo[tydzien] += 8
                            self.oblicz_punkty(current_date, pracownik)
                            
                            if self.sprawdz_dni_pod_rzad(pracownik, current_date) >= 6:
                                for i in range(1, 3):
                                    next_date = current_date + timedelta(days=i)
                                    if next_date <= self.end_date:
                                        pracownik.dni_wolne.add(next_date)

            current_date += timedelta(days=1)

        return True

    def generuj_harmonogram(self):
        if self.przydziel_dni_pracy():
            # Otwórz nowe okno z harmonogramem
            HarmonogramGUI(self, self.start_date, self.end_date, self.pracownicy)
            
    def on_date_select(self, event):
        try:
            selected_date = datetime.strptime(self.calendar.get_date(), "%Y-%m-%d")
            if self.start_date <= selected_date <= self.end_date:
                if selected_date not in self.wybrane_dni:
                    self.wybrane_dni.add(selected_date)
                    self.wybrane_dni_lista.insert(tk.END, selected_date.strftime("%Y-%m-%d"))
            else:
                messagebox.showwarning("Ostrzeżenie", "Data poza wybranym zakresem!")
        except Exception as e:
            print(f"Error in on_date_select: {e}")
            messagebox.showerror("Błąd", f"Błąd podczas wyboru daty: {e}")

    def usun_wybrany_dzien(self):
        selection = self.wybrane_dni_lista.curselection()
        if selection:
            date_str = self.wybrane_dni_lista.get(selection[0])
            date = datetime.strptime(date_str, "%Y-%m-%d")
            self.wybrane_dni.remove(date)
            self.wybrane_dni_lista.delete(selection[0])

    def zatwierdz_zakres(self):
        try:
            self.start_date = datetime.strptime(self.start_cal.get_date(), "%Y-%m-%d")
            self.end_date = datetime.strptime(self.end_cal.get_date(), "%Y-%m-%d")
            if self.start_date > self.end_date:
                raise ValueError("Data początkowa nie może być późniejsza niż końcowa")
            print(f"Start date: {self.start_date}")
            print(f"End date: {self.end_date}")
            messagebox.showinfo("Sukces", "Zakres dat został zatwierdzony")
        except Exception as e:
            print(f"Error in zatwierdz_zakres: {e}")
            messagebox.showerror("Błąd", f"Błąd podczas zatwierdzania dat: {e}")

    def wybierz_pracownika(self, pracownik):
        if self.start_date is None or self.end_date is None:
            messagebox.showerror("Błąd", "Najpierw zatwierdź zakres dat!")
            return
        
        self.aktualny_pracownik = pracownik
        self.calendar.pack(fill=tk.BOTH, expand=True, pady=5)
        self.wybrane_dni.clear()
        self.wybrane_dni_lista.delete(0, tk.END)
        
        for data in pracownik.dni_wolne:
            self.wybrane_dni.add(data)
            self.wybrane_dni_lista.insert(tk.END, data.strftime("%Y-%m-%d"))

    def zapisz_dni_wolne(self):
        if not self.aktualny_pracownik:
            messagebox.showerror("Błąd", "Najpierw wybierz pracownika!")
            return

        self.aktualny_pracownik.dni_wolne = self.wybrane_dni.copy()
        messagebox.showinfo("Sukces", f"Zapisano dni wolne dla {self.aktualny_pracownik.imie}")

    def czy_swieto(self, data):
        return data in self.pl_holidays

    def oblicz_punkty(self, data, pracownik):
        if data.weekday() == 5:  # sobota
            pracownik.dodaj_punkty(1)
        elif data.weekday() == 6:  # niedziela
            pracownik.dodaj_punkty(2)
        elif self.czy_swieto(data):  # święto
            pracownik.dodaj_punkty(5)

    def sprawdz_ciaglosc_pracy(self, pracownik, data):
        # Sprawdź czy pracownik pracował 2 dni przed datą
        for i in range(1, 3):
            if data - timedelta(days=i) not in pracownik.dni_pracy:
                return False
        return True

def sprawdz_dni_pod_rzad(self, pracownik, data):
    # Sprawdź 6 poprzednich dni
    kolejne_dni_pracy = 0
    for i in range(6):
        if data - timedelta(days=i) in pracownik.dni_pracy:
            kolejne_dni_pracy += 1
        else:
            break
    return kolejne_dni_pracy

def czy_wymaga_odpoczynku(self, pracownik, data):
    # Sprawdź czy pracownik ma za sobą 6 dni pracy
    if self.sprawdz_dni_pod_rzad(pracownik, data) >= 6:
        # Sprawdź czy następne 2 dni są wolne
        for i in range(1, 3):
            next_date = data + timedelta(days=i)
            if next_date in pracownik.dni_pracy:
                return True
    return False

def czy_moze_pracowac(self, pracownik, data):
    # Sprawdź czy pracownik nie wymaga odpoczynku po 6 dniach
    poprzednie_dni = self.sprawdz_dni_pod_rzad(pracownik, data)
    if poprzednie_dni >= 6:
        return False
    
    # Sprawdź czy nie jest w trakcie obowiązkowego odpoczynku
    for i in range(1, 3):
        if data - timedelta(days=i) in pracownik.dni_pracy and self.sprawdz_dni_pod_rzad(pracownik, data - timedelta(days=i)) >= 6:
            return False
    
    return True

def sprawdz_dni_pod_rzad(self, pracownik, data):
    # Sprawdź 6 poprzednich dni
    kolejne_dni_pracy = 0
    for i in range(6):
        if data - timedelta(days=i) in pracownik.dni_pracy:
            kolejne_dni_pracy += 1
        else:
            break
    return kolejne_dni_pracy

def czy_wymaga_odpoczynku(self, pracownik, data):
    # Sprawdź czy pracownik ma za sobą 6 dni pracy
    if self.sprawdz_dni_pod_rzad(pracownik, data) >= 6:
        # Sprawdź czy następne 2 dni są wolne
        for i in range(1, 3):
            next_date = data + timedelta(days=i)
            if next_date in pracownik.dni_pracy:
                return True
    return False

def czy_moze_pracowac(self, pracownik, data):
    # Sprawdź czy pracownik nie wymaga odpoczynku po 6 dniach
    poprzednie_dni = self.sprawdz_dni_pod_rzad(pracownik, data)
    if poprzednie_dni >= 6:
        return False
    
    # Sprawdź czy nie jest w trakcie obowiązkowego odpoczynku
    for i in range(1, 3):
        if data - timedelta(days=i) in pracownik.dni_pracy and self.sprawdz_dni_pod_rzad(pracownik, data - timedelta(days=i)) >= 6:
            return False
    
    return True

def przydziel_dni_pracy(self):
    if not self.start_date or not self.end_date:
        messagebox.showerror("Błąd", "Najpierw zatwierdź zakres dat!")
        return False

    # Czyszczenie poprzedniego harmonogramu
    for pracownik in self.pracownicy:
        pracownik.wyczysc_harmonogram()

    # Pierwszy przebieg - zapewnienie minimum 2 pracowników na dzień
    current_date = self.start_date
    while current_date <= self.end_date:
        dostepni = []
        tydzien = current_date.isocalendar()[1]

        for pracownik in self.pracownicy:
            if (current_date not in pracownik.dni_wolne and 
                self.czy_moze_pracowac(pracownik, current_date)):
                if tydzien not in pracownik.godziny_tygodniowo:
                    pracownik.godziny_tygodniowo[tydzien] = 0
                if pracownik.godziny_tygodniowo[tydzien] < 40:
                    dostepni.append(pracownik)

        pracujacy = []
        for pracownik in dostepni[:2]:
            pracujacy.append(pracownik)
            pracownik.dni_pracy.add(current_date)
            pracownik.godziny_tygodniowo[tydzien] += 8
            self.oblicz_punkty(current_date, pracownik)
            
            # Jeśli pracownik osiągnął 6 dni, zaplanuj 2 dni wolne
            if self.sprawdz_dni_pod_rzad(pracownik, current_date) >= 6:
                for i in range(1, 3):
                    next_date = current_date + timedelta(days=i)
                    if next_date <= self.end_date:
                        pracownik.dni_wolne.add(next_date)

        current_date += timedelta(days=1)

    # Drugi przebieg - uzupełnienie do 40h tygodniowo
    current_date = self.start_date
    while current_date <= self.end_date:
        tydzien = current_date.isocalendar()[1]
        
        for pracownik in self.pracownicy:
            if (current_date not in pracownik.dni_wolne and 
                current_date not in pracownik.dni_pracy and
                self.czy_moze_pracowac(pracownik, current_date)):
                
                if tydzien in pracownik.godziny_tygodniowo and pracownik.godziny_tygodniowo[tydzien] < 40:
                    pracujacy_dzis = [p for p in self.pracownicy if current_date in p.dni_pracy]
                    if len(pracujacy_dzis) >= 2:
                        pracownik.dni_pracy.add(current_date)
                        pracownik.godziny_tygodniowo[tydzien] += 8
                        self.oblicz_punkty(current_date, pracownik)
                        
                        # Sprawdź czy potrzebny jest odpoczynek
                        if self.sprawdz_dni_pod_rzad(pracownik, current_date) >= 6:
                            for i in range(1, 3):
                                next_date = current_date + timedelta(days=i)
                                if next_date <= self.end_date:
                                    pracownik.dni_wolne.add(next_date)

        current_date += timedelta(days=1)

    return True
    
    def generuj_harmonogram(self):
        if self.przydziel_dni_pracy():
            # Sprawdź czy są pracownicy na każdy dzień
            current_date = self.start_date
            while current_date <= self.end_date:
                pracujacy = [p for p in self.pracownicy if current_date in p.dni_pracy]
                if len(pracujacy) < 2:
                    messagebox.showwarning("Ostrzeżenie", 
                        f"Brak wystarczającej liczby pracowników na {current_date.strftime('%Y-%m-%d')}")
                current_date += timedelta(days=1)

            # Sprawdź 40h tygodniowo dla każdego pracownika
            for pracownik in self.pracownicy:
                for tydzien, godziny in pracownik.godziny_tygodniowo.items():
                    if godziny != 40:
                        messagebox.showwarning("Ostrzeżenie", 
                            f"{pracownik.imie} ma {godziny}h w tygodniu {tydzien} (powinno być 40h)")

            # Otwórz okno z harmonogramem
            HarmonogramGUI(self, self.start_date, self.end_date, self.pracownicy)

    def sprawdz_dostepnosc(self, data, pracownicy_na_zmianie):
        return len([p for p in pracownicy_na_zmianie if data in p.dni_pracy]) >= 2

def main():
    try:
        app = AplikacjaHarmonogramu()
        app.mainloop()
    except Exception as e:
        print(f"Błąd podczas uruchamiania aplikacji: {e}")
        messagebox.showerror("Błąd krytyczny", 
            "Wystąpił błąd podczas uruchamiania aplikacji. Sprawdź logi.")

if __name__ == "__main__":
    main()