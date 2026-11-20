import asyncio
import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os
import random
import re
import threading
import traceback
import discord
from discord.ext import commands, tasks

# ----------------- PROSTY SERWER HTTP DLA HEALTH CHECK (Fly.io / Docker) ----------------- #


class HealthCheckHandler(BaseHTTPRequestHandler):

  def do_GET(self):
    self.send_response(200)
    self.send_header("Content-type", "text/plain; charset=utf-8")
    self.end_headers()
    self.wfile.write(b"Bot Emerald Shop jest online!")

  def log_message(self, format, *args):
    return


def uruchom_serwer_http():
  try:
    server_address = ("0.0.0.0", 8080)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    print(
        ">>> [SERWER HTTP] Nasłuchiwanie na 0.0.0.0:8080 dla Health Check"
        " zakończone sukcesem."
    )
    httpd.serve_forever()
  except Exception as e:
    print(f"[OSTRZEŻENIE HTTP] Nie udało się uruchomić serwera HTTP: {e}")


threading.Thread(target=uruchom_serwer_http, daemon=True).start()

# ----------------- KONFIGURACJA BOTA DISCORD ----------------- #

TOKEN = "MTU2ODY4NzU5NzM2OTI5OTA0NA.GwJcUV.q3KjrjRq7DRPep9VYB4nyYSzROTuK-RrqyQUT0"

intents = discord.Intents.default()
intents.guilds = True
intents.message_content = True
intents.presences = True
intents.members = True
intents.invites = True
intents.reactions = True

bot = commands.Bot(command_prefix="!", intents=intents)

ADMIN_ROLE_IDS = [1517904000995954899, 1517895800343232674]
LIDER_ROLE_ID = 1517894479305117906
WERYFIKOWANY_ROLE_ID = 1517896335599341608

PLIK_CENNIK = "cennik_dane.json"
PLIK_SKUP = "skup_dane.json"
PLIK_STATYSTYK = "statystyki_dane.json"
PLIK_LEGIT_HISTORIA = "legitchecki_historia.json"

domyslne_dane_cennik = {
    "Anarchia.gg - Lifesteal": [
        {"ilosc": "11000$", "cena": "1 PLN"},
        {"ilosc": "50000$", "cena": "4 PLN"},
        {"ilosc": "Ranga VIP", "cena": "15 PLN"},
    ],
    "Anarchia.gg - BoxPVP": [
        {"ilosc": "Start", "cena": "5 PLN"},
        {"ilosc": "BoxVip", "cena": "20 PLN"},
        {"ilosc": "Klucze", "cena": "10 PLN"},
    ],
    "Minestar.gg - SkyPvP": [
        {"ilosc": "11000$", "cena": "1 PLN"},
        {"ilosc": "50000$", "cena": "4 PLN"},
        {"ilosc": "Ranga VIP", "cena": "15 PLN"},
    ],
    "Minestar.gg - Lifesteal": [
        {"ilosc": "11000$", "cena": "1 PLN"},
        {"ilosc": "50000$", "cena": "4 PLN"},
        {"ilosc": "Ranga VIP", "cena": "15 PLN"},
    ],
    "Rapy.gg - EarthSMP": [
        {"ilosc": "11000$", "cena": "1 PLN"},
        {"ilosc": "50000$", "cena": "4 PLN"},
        {"ilosc": "Ranga VIP", "cena": "15 PLN"},
    ],
    "Rapy.gg - Wojny Gildii": [
        {"ilosc": "11000$", "cena": "1 PLN"},
        {"ilosc": "50000$", "cena": "4 PLN"},
        {"ilosc": "Ranga VIP", "cena": "15 PLN"},
    ],
    "Rapy.gg - BoxPVP": [
        {"ilosc": "Start", "cena": "5 PLN"},
        {"ilosc": "BoxVip", "cena": "20 PLN"},
        {"ilosc": "Klucze", "cena": "10 PLN"},
    ],
}

domyslne_dane_skup = {
    "Anarchia.gg - Lifesteal": [
        {"ilosc": "100000$", "cena": "5 PLN"},
        {"ilosc": "Pakiet startowy", "cena": "10 PLN"},
    ],
    "Anarchia.gg - BoxPVP": [{"ilosc": "Itemy PVP", "cena": "15 PLN"}],
    "Minestar.gg - SkyPvP": [{"ilosc": "Waluta 50k", "cena": "3 PLN"}],
    "Minestar.gg - Lifesteal": [{"ilosc": "Waluta 50k", "cena": "3 PLN"}],
    "Rapy.gg - EarthSMP": [{"ilosc": "Waluta 50k", "cena": "3 PLN"}],
    "Rapy.gg - Wojny Gildii": [{"ilosc": "Waluta 50k", "cena": "3 PLN"}],
    "Rapy.gg - BoxPVP": [{"ilosc": "Waluta 50k", "cena": "3 PLN"}],
}


def wczytaj_plik(sciezka, domyslne):
  if os.path.exists(sciezka):
    try:
      with open(sciezka, "r", encoding="utf-8") as f:
        dane = json.load(f)
        if not isinstance(dane, dict):
          return domyslne.copy()
        zmieniono = False
        for k, v in domyslne.items():
          if k not in dane:
            dane[k] = v
            zmieniono = True
        if zmieniono:
          with open(sciezka, "w", encoding="utf-8") as f_out:
            json.dump(dane, f_out, ensure_ascii=False, indent=4)
        return dane
    except Exception:
      return domyslne.copy()
  else:
    try:
      with open(sciezka, "w", encoding="utf-8") as f:
        json.dump(domyslne, f, ensure_ascii=False, indent=4)
    except Exception:
      pass
    return domyslne.copy()


cennik_dane = wczytaj_plik(PLIK_CENNIK, domyslne_dane_cennik)
skup_dane = wczytaj_plik(PLIK_SKUP, domyslne_dane_skup)


def zapisz_cennik():
  try:
    with open(PLIK_CENNIK, "w", encoding="utf-8") as f:
      json.dump(cennik_dane, f, ensure_ascii=False, indent=4)
  except Exception:
    pass


def zapisz_skup():
  try:
    with open(PLIK_SKUP, "w", encoding="utf-8") as f:
      json.dump(skup_dane, f, ensure_ascii=False, indent=4)
  except Exception:
    pass


def stworz_puste_statystyki(zachowaj_lc_calkowite=0):
  return {
      "data": datetime.datetime.now().strftime("%d.%m.%Y"),
      "zamowienia_ilosc": 0,
      "zamowienia_kwota": 0.0,
      "sprzedane_itemy_kwota": 0.0,
      "dolaczylo": 0,
      "wyszlo": 0,
      "lc_osiagniete": 0,
      "legitchecki_licznik": zachowaj_lc_calkowite,
      "aktywna_wiadomosc_stats_id": None,
  }


def wczytaj_statystyki():
  domyslne = stworz_puste_statystyki(0)
  if os.path.exists(PLIK_STATYSTYK):
    try:
      with open(PLIK_STATYSTYK, "r", encoding="utf-8") as f:
        dane = json.load(f)
        if isinstance(dane, dict):
          for k, v in domyslne.items():
            if k not in dane:
              dane[k] = v
          return dane
    except Exception:
      pass
  try:
    with open(PLIK_STATYSTYK, "w", encoding="utf-8") as f:
      json.dump(domyslne, f, ensure_ascii=False, indent=4)
  except Exception:
    pass
  return domyslne


def zapisz_statystyki():
  try:
    with open(PLIK_STATYSTYK, "w", encoding="utf-8") as f:
      json.dump(stats_dane, f, ensure_ascii=False, indent=4)
  except Exception:
    pass


def zapisz_legitcheck_do_historii(wpis):
  lista = []
  if os.path.exists(PLIK_LEGIT_HISTORIA):
    try:
      with open(PLIK_LEGIT_HISTORIA, "r", encoding="utf-8") as f:
        wczytane = json.load(f)
        if isinstance(wczytane, list):
          lista = wczytane
    except Exception:
      lista = []
  lista.append(wpis)
  try:
    with open(PLIK_LEGIT_HISTORIA, "w", encoding="utf-8") as f:
      json.dump(lista, f, ensure_ascii=False, indent=4)
  except Exception:
    pass


stats_dane = wczytaj_statystyki()
invites_cache = {}


async def cache_all_invites(guild):
  try:
    invs = await guild.invites()
    invites_cache[guild.id] = {inv.code: inv.uses for inv in invs}
  except Exception:
    pass


def dodaj_statystyke_zamowienia(kwota):
  global stats_dane
  stats_dane["zamowienia_ilosc"] += 1
  stats_dane["zamowienia_kwota"] += kwota
  zapisz_statystyki()


def dodaj_statystyke_skupu(kwota):
  global stats_dane
  stats_dane["sprzedane_itemy_kwota"] += kwota
  zapisz_statystyki()


def dodaj_legitcheck_stat():
  global stats_dane
  stats_dane["legitchecki_licznik"] = (
      stats_dane.get("legitchecki_licznik", 0) + 1
  )
  stats_dane["lc_osiagniete"] = stats_dane.get("lc_osiagniete", 0) + 1
  zapisz_statystyki()


def parsuj_kwote(tekst):
  match = re.search(r"\d+([.,]\d+)?", tekst.strip())
  return float(match.group().replace(",", ".")) if match else 0.0


def parsuj_czas(czas_str):
  match = re.fullmatch(r"(\d+)\s*([smhdSMHD])", czas_str.strip())
  if not match:
    return None
  wartosc = int(match.group(1))
  jednostka = match.group(2).lower()
  if wartosc <= 0:
    return None
  if jednostka == "s":
    return wartosc
  if jednostka == "m":
    return wartosc * 60
  if jednostka == "h":
    return wartosc * 3600
  if jednostka == "d":
    return wartosc * 86400
  return None


def oblicz_platnosc_zakup(wybor, bazowa_kwota):
  if "Kod BLIK" in wybor:
    prowizja = 0.10
    metoda = "Kod BLIK"
    proc = 10
  elif "Paysafecard" in wybor:
    prowizja = 0.15
    metoda = "Paysafecard"
    proc = 15
  elif "LTC" in wybor:
    prowizja = 0.05
    metoda = "LTC"
    proc = 5
  else:
    prowizja = 0.0
    metoda = "BLIK"
    proc = 0

  koncowa = bazowa_kwota * (1.0 + prowizja)
  opis_ticket = f"{wybor} (Do zapłaty: {koncowa:.2f} PLN | +{proc}%)"
  opis_legit = f"{metoda} (Zapłacono: {koncowa:.2f} PLN)"
  return koncowa, opis_ticket, opis_legit


def oblicz_platnosc_skup(wybor, bazowa_kwota):
  if "Kod BLIK" in wybor:
    potracenie = 0.10
    metoda = "Kod BLIK"
    proc = 10
  elif "Paysafecard" in wybor:
    potracenie = 0.15
    metoda = "Paysafecard"
    proc = 15
  elif "LTC" in wybor:
    potracenie = 0.05
    metoda = "LTC"
    proc = 5
  else:
    potracenie = 0.0
    metoda = "BLIK"
    proc = 0

  koncowa = max(0.0, bazowa_kwota * (1.0 - potracenie))
  opis_ticket = f"{wybor} (Do wypłaty: {koncowa:.2f} PLN | -{proc}%)"
  opis_legit = f"{metoda} (Wypłacono: {koncowa:.2f} PLN)"
  return koncowa, opis_ticket, opis_legit


def sprawdzenie_kadry(user):
  is_admin = user.guild_permissions.administrator
  is_lider = any(r.id == LIDER_ROLE_ID for r in user.roles)
  is_sprzedawca = any(r.id in ADMIN_ROLE_IDS for r in user.roles)
  return is_admin or is_lider or is_sprzedawca


def stworz_embed_sprzedaj_itemy():
  embed = discord.Embed(
      title="💎 ￤ EMERALD SHOP × SPRZEDAJ ITEMY",
      color=discord.Color.from_rgb(46, 204, 113),
  )
  embed.description = (
      "💸 **Skupuję itemy za prawdziwą kasę!** 💸\n\n"
      "💬 ￤ CHCESZ SPRZEDAĆ SWOJE ITEMY NA JAKIMŚ SERWERZE ZA PRAWDZIWĄ"
      " KASĘ?\n\n"
      "💸 **× MINIMALNA WARTOŚĆ**\n"
      "➖ ￤ Skupujemy itemy oraz kasę od wartości minimum: `20 zł z cennika`\n\n"
      "🏷️ **× ILE OTRZYMASZ ZA ITEMY**\n"
      "➖ ￤ Oferuję od `30-65%` z mojego cennika – zależy od wielu"
      " czynników.\n"
      "➖ ￤ Każdemu daję indywidualny % po dogadaniu się.\n\n"
      "💳 **× METODY PŁATNOŚCI**\n"
      "🔒 ￤ PaySafeCard\n"
      "🅱️ ￤ Blik\n"
      "🅿️ ￤ PayPal\n"
      "🪙 ￤ KryptoWaluty\n"
      "➖ ￤ Zakup usług itd.\n\n"
      "📩 **× JAK ROZPOCZĄĆ SPRZEDAŻ**\n"
      "➖ ￤ Wybierz tryb z kategorii **SKUP EMERALD** i kliknij **Zgłoś"
      " skup**."
  )
  embed.set_footer(text="© 2026 EMERALD SHOP × SPRZEDAJ ITEMY")
  return embed


def stworz_embed_czy_jestesmy_legit():
  embed = discord.Embed(
      title="🧐 ￤ EMERALD SHOP × CZY JESTEŚMY LEGIT?",
      description=(
          "Zostaw swoją opinię klikając odpowiednią reakcję poniżej!\n\n"
          "✅ — **Tak, Emerald Shop jest w 100% legit!**\n"
          "❌ — **Nie**\n\n"
          "🛡️ Wszystkie zrealizowane transakcje znajdziesz na kanale z"
          " legit-checkami."
      ),
      color=discord.Color.from_rgb(46, 204, 113),
  )
  embed.set_footer(text="© 2026 EMERALD SHOP × OPINIE KLIENTÓW")
  return embed


def stworz_embed_statystyk(archiwum=False):
  saldo = stats_dane["dolaczylo"] - stats_dane["wyszlo"]
  laczna_kwota = (
      stats_dane["zamowienia_kwota"] + stats_dane["sprzedane_itemy_kwota"]
  )

  embed = discord.Embed(
      title="📊 ￤ EMERALD SHOP × DZIENNE STATYSTYKI",
      color=(
          discord.Color.from_rgb(149, 165, 166)
          if archiwum
          else discord.Color.from_rgb(46, 204, 113)
      ),
  )
  embed.add_field(
      name="📅 Statystyki dotyczą dnia:",
      value=f"`{stats_dane['data']}`",
      inline=False,
  )
  embed.add_field(
      name="👥 Ruch na serwerze",
      value=(
          f"❗ ￤ Dzisiaj wbiło do nas: `{stats_dane['dolaczylo']}` osób\n"
          f"❗ ￤ Niestety, postanowiło wyjść: `{stats_dane['wyszlo']}` osób\n"
          f"❗ ￤ Saldo osób wyniosło: `{saldo}` osób"
      ),
      inline=False,
  )
  embed.add_field(
      name="💰 Finanse i transakcje",
      value=(
          f"✔️ ￤ Osiągnęliśmy dzięki wam: `{stats_dane['lc_osiagniete']}` LC\n"
          f"💸 ￤ Kwota za którą dzisiaj zrobiliście zakupy:"
          f" `{stats_dane['zamowienia_kwota']:.2f}` PLN\n"
          f"💳 ￤ Kwota za którą dzisiaj sprzedaliście itemy:"
          f" `{stats_dane['sprzedane_itemy_kwota']:.2f}` PLN\n"
          f"💰 ￤ Łączna kwota transakcji wyniosła:"
          f" `{laczna_kwota:.2f}` PLN"
      ),
      inline=False,
  )
  if archiwum:
    embed.add_field(
        name="⏰ Status aktualizacji",
        value=(
            "🔒 ￤ Status dnia: `Podsumowanie dnia zakończone (archiwum)`\n"
            "📅 ￤ Kolejny dzień: `Nowa tabela poniżej`"
        ),
        inline=False,
    )
  else:
    embed.add_field(
        name="⏰ Status aktualizacji",
        value=(
            "⏱️ ￤ Ostatnia aktualizacja: `w tej chwili`\n"
            "⏳ ￤ Następna aktualizacja: `za 5 minut (nowa tabela o 00:00)`"
        ),
        inline=False,
    )
  embed.set_footer(text="© 2026 EMERALD SHOP × DZIENNE STATYSTYKI")
  return embed


def stworz_embed_cennika(tryb_nazwa, produkty):
  czastki = tryb_nazwa.split(" - ")
  serwer = czastki[0]
  tryb = czastki[1] if len(czastki) > 1 else ""
  embed = discord.Embed(
      title=(
          "🛒 ── 🌟 **EMERALD SHOP** 🌟 ── 🛒\n✨ CENNIK: **"
          + tryb_nazwa.upper()
          + "** ✨"
      ),
      color=discord.Color.from_rgb(46, 204, 113),
  )
  embed.add_field(
      name="📌 **Informacje o serwerze**",
      value=f"» **Serwer:** `{serwer}`\n» **Tryb:** `{tryb}`",
      inline=False,
  )
  oferty_tekst = "» *Brak aktywnych ofert.*"
  if produkty:
    oferty_tekst = ""
    for idx, p in enumerate(produkty, start=1):
      oferty_tekst += (
          f"💎 `{idx}.` **{p.get('ilosc', 'Brak')}** ──"
          f" `💸 {p.get('cena', '0 PLN')}`\n"
      )
  embed.add_field(
      name="📦 **Dostępne oferty** (max. 3)", value=oferty_tekst, inline=False
  )
  podatki_tekst = (
      "🟢 **Kod BLIK:** `+10%` podatek\n"
      "🔵 **Przelew na numer (BLIK):** `0%` podatek\n"
      "🟠 **Paysafecard:** `+15%` podatek\n"
      "🟣 **LTC:** `+5%` podatek"
  )
  embed.add_field(
      name="💳 **Podatki & Formy Płatności**", value=podatki_tekst, inline=False
  )
  embed.set_footer(
      text="✨ Emerald Shop ✕ Oficjalny System Cenników ✦ Bezpieczne zakupy ✨"
  )
  return embed


def stworz_embed_skupu(tryb_nazwa, produkty):
  czastki = tryb_nazwa.split(" - ")
  serwer = czastki[0]
  tryb = czastki[1] if len(czastki) > 1 else ""
  embed = discord.Embed(
      title=(
          "💰 ── 🌟 **EMERALD SKUP** 🌟 ── 💰\n✨ CENNIK SKUPU: **"
          + tryb_nazwa.upper()
          + "** ✨"
      ),
      color=discord.Color.from_rgb(241, 196, 15),
  )
  embed.add_field(
      name="📌 **Informacje o serwerze**",
      value=f"» **Serwer:** `{serwer}`\n» **Tryb:** `{tryb}`",
      inline=False,
  )
  oferty_tekst = "» *Brak ofert skupu.*"
  if produkty:
    oferty_tekst = ""
    for idx, p in enumerate(produkty, start=1):
      oferty_tekst += (
          f"📦 `{idx}.` **{p.get('ilosc', 'Brak')}** ──"
          f" `💸 {p.get('cena', '0 PLN')}`\n"
      )
  embed.add_field(
      name="💎 **Oferowane przedmioty do skupu**", value=oferty_tekst, inline=False
  )
  prowizje_skup_tekst = (
      "🟢 **Kod BLIK:** `-10%` potrącenia\n"
      "🔵 **Przelew na numer (BLIK):** `0%` potrącenia\n"
      "🟠 **Paysafecard:** `-15%` potrącenia\n"
      "🟣 **LTC:** `-5%` potrącenia"
  )
  embed.add_field(
      name="💳 **Wypłaty & Oprocentowanie**",
      value=prowizje_skup_tekst,
      inline=False,
  )
  embed.add_field(
      name="ℹ️ **Informacja**",
      value=(
          "» Chcesz nam sprzedać walutę lub itemy? Kliknij przycisk poniżej i"
          " stwórz zgłoszenie!"
      ),
      inline=False,
  )
  embed.set_footer(text="✨ Emerald Shop ✕ Oficjalny System Skupu ✨")
  return embed


def zbuduj_embed_potwierdzonego_legita(
    sprzedawca_mention,
    klient_etykieta,
    serwer,
    tryb,
    typ_transakcji,
    przedmiot,
    platnosc_opis,
    formulka_rep,
):
  embed = discord.Embed(
      title="🛡️ — EMERALD SHOP × POTWIERDZONY LEGIT — 🛡️",
      color=discord.Color.from_rgb(46, 204, 113),
  )
  embed.add_field(name="👤 Sprzedawca", value=sprzedawca_mention, inline=True)
  embed.add_field(name="🤝 Klient", value=klient_etykieta, inline=True)
  embed.add_field(
      name="📌 Serwer / Tryb", value=f"`{serwer} / {tryb}`", inline=False
  )
  embed.add_field(
      name=f"📦 {typ_transakcji}",
      value=(
          f"Produkt: `{przedmiot}`\n"
          f"Płatność: `{platnosc_opis}`\n\n"
          f"💬 **Formułka rep**\n`{formulka_rep}`\n\n"
          "✨ Dziękujemy za transakcję! ✨"
      ),
      inline=False,
  )
  return embed


# ----------------- SYNCHRONIZACJA LEGITCHECKÓW, REAKCJI I STATYSTYK ----------------- #


async def dodaj_reakcje_legitcheck(message):
  for emoji in ("✅", "❤️"):
    try:
      await message.add_reaction(emoji)
    except Exception:
      pass


async def dodaj_reakcje_czy_legit(message):
  for emoji in ("✅", "❌"):
    try:
      await message.add_reaction(emoji)
    except Exception:
      pass


async def pobierz_lub_utworz_wiadomosc_statystyk(chan):
  aktywne_id = stats_dane.get("aktywna_wiadomosc_stats_id")
  if aktywne_id:
    try:
      msg = await chan.fetch_message(int(aktywne_id))
      return msg
    except Exception:
      pass

  async for m in chan.history(limit=15):
    if m.author == bot.user and m.embeds:
      tytul = m.embeds[0].title or ""
      if "DZIENNE STATYSTYKI" in tytul:
        stats_dane["aktywna_wiadomosc_stats_id"] = m.id
        zapisz_statystyki()
        return m

  nowa = await chan.send(embed=stworz_embed_statystyk(archiwum=False))
  stats_dane["aktywna_wiadomosc_stats_id"] = nowa.id
  zapisz_statystyki()
  return nowa


async def zsynchronizuj_liczniki_i_statystyki(guild, aktualizuj_nazwe_lc=False):
  for chan in guild.text_channels:
    nazwa_lower = chan.name.lower()
    if "dzienne-statystyki" in nazwa_lower:
      try:
        msg = await pobierz_lub_utworz_wiadomosc_statystyk(chan)
        await msg.edit(embed=stworz_embed_statystyk(archiwum=False))
      except Exception:
        pass
    elif aktualizuj_nazwe_lc and (
        "legit-check" in nazwa_lower or "legit" in nazwa_lower
    ):
      nowa_nazwa = re.sub(
          r"\d+$", str(stats_dane.get("legitchecki_licznik", 0)), chan.name
      )
      if nowa_nazwa != chan.name:
        try:
          await chan.edit(name=nowa_nazwa)
        except Exception:
          pass


async def sprawdz_polnoc_i_nowa_tabele():
  dzisiaj = datetime.datetime.now().strftime("%d.%m.%Y")
  zapisana_data = stats_dane.get("data")

  if not zapisana_data:
    stats_dane["data"] = dzisiaj
    zapisz_statystyki()
    return

  if zapisana_data != dzisiaj:
    # 1. Zamknij starą tabelę na kanale (zostaje widoczna jako archiwum dnia)
    for guild in bot.guilds:
      for chan in guild.text_channels:
        if "dzienne-statystyki" in chan.name.lower():
          try:
            stara_msg = await pobierz_lub_utworz_wiadomosc_statystyk(chan)
            await stara_msg.edit(embed=stworz_embed_statystyk(archiwum=True))
          except Exception:
            pass

    # 2. Wyzeruj statystyki na nowy dzień (zachowując łączną liczbę legitchecków)
    calkowite_lc = stats_dane.get("legitchecki_licznik", 0)
    stats_dane.clear()
    stats_dane.update(stworz_puste_statystyki(zachowaj_lc_calkowite=calkowite_lc))
    stats_dane["data"] = dzisiaj
    zapisz_statystyki()

    # 3. Wyślij nową tabelę na nowy dzień pod starą tabelą
    for guild in bot.guilds:
      for chan in guild.text_channels:
        if "dzienne-statystyki" in chan.name.lower():
          try:
            nowa_msg = await chan.send(
                embed=stworz_embed_statystyk(archiwum=False)
            )
            stats_dane["aktywna_wiadomosc_stats_id"] = nowa_msg.id
            zapisz_statystyki()
          except Exception:
            pass


# ----------------- SYSTEM KONKURSÓW ----------------- #


def zbuduj_embed_konkursu_aktywnego(
    nagroda, liczba_zwyciezcow, koniec_dt, uczestnicy_ids, baner_url=None
):
  ts = int(koniec_dt.timestamp())
  embed = discord.Embed(
      title="🎉 ── **EMERALD SHOP × KONKURS** ── 🎉",
      description=(
          f"🎁 **Nagroda:** `{nagroda}`\n"
          f"🏆 **Liczba zwycięzców:** `{liczba_zwyciezcow}`\n"
          f"👥 **Uczestników:** `{len(uczestnicy_ids)}`\n"
          f"⏰ **Koniec:** <t:{ts}:R> (<t:{ts}:f>)"
      ),
      color=discord.Color.from_rgb(255, 140, 0),
  )
  if baner_url:
    embed.set_image(url=baner_url)
  embed.set_footer(text="© 2026 EMERALD SHOP × KONKURS W TRAKCIE")
  return embed


def zbuduj_embed_konkursu_zakonczonego(
    guild, nagroda, zwyciezcy_ids, uczestnicy_ids, baner_url=None
):
  if zwyciezcy_ids:
    zwyciezcy_txt = ", ".join(f"<@{uid}>" for uid in zwyciezcy_ids)
  else:
    zwyciezcy_txt = "`Brak zwycięzców (brak uczestników)`"

  wzmianki_uczestnikow = []
  for uid in uczestnicy_ids:
    member = guild.get_member(uid) if guild else None
    wzmianki_uczestnikow.append(member.mention if member else f"<@{uid}>")

  limit_wyswietlania = 33
  if len(wzmianki_uczestnikow) > limit_wyswietlania:
    reszta = len(wzmianki_uczestnikow) - limit_wyswietlania
    lista_txt = (
        ", ".join(wzmianki_uczestnikow[:limit_wyswietlania]) + f" +{reszta}"
    )
  elif wzmianki_uczestnikow:
    lista_txt = ", ".join(wzmianki_uczestnikow)
  else:
    lista_txt = "*Brak uczestników*"

  embed = discord.Embed(
      description=(
          f"🎁 **Nagroda:** `{nagroda}`\n"
          f"🏆 **Zwycięzcy:** {zwyciezcy_txt}\n"
          f"👥 **Uczestników:** `{len(uczestnicy_ids)}`\n\n"
          f"Lista uczestników ({len(uczestnicy_ids)}): {lista_txt}"
      ),
      color=discord.Color.from_rgb(255, 140, 0),
  )
  if baner_url:
    embed.set_image(url=baner_url)
  embed.set_footer(text="© 2026 EMERALD SHOP × KONKURS ZAKOŃCZONY")
  return embed


class GiveawayView(discord.ui.View):

  def __init__(
      self, nagroda, liczba_zwyciezcow, koniec_dt, baner_url=None, timeout=None
  ):
    super().__init__(timeout=timeout)
    self.nagroda = nagroda
    self.liczba_zwyciezcow = liczba_zwyciezcow
    self.koniec_dt = koniec_dt
    self.baner_url = baner_url
    self.uczestnicy = []
    self.zakonczony = False

  @discord.ui.button(
      label="🎉 Weź udział",
      style=discord.ButtonStyle.success,
      custom_id="giveaway_join_btn",
  )
  async def join_giveaway(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    if self.zakonczony:
      await interaction.response.send_message(
          "⚠️ **Ten konkurs został już zakończony!**", ephemeral=True
      )
      return

    uid = interaction.user.id
    if uid in self.uczestnicy:
      self.uczestnicy.remove(uid)
      msg = "🚪 **Wypisałeś się z konkursu.**"
    else:
      self.uczestnicy.append(uid)
      msg = "🎉 **Dołączyłeś do konkursu! Powodzenia!**"

    await interaction.message.edit(
        embed=zbuduj_embed_konkursu_aktywnego(
            self.nagroda,
            self.liczba_zwyciezcow,
            self.koniec_dt,
            self.uczestnicy,
            self.baner_url,
        ),
        view=self,
    )
    await interaction.response.send_message(msg, ephemeral=True)


async def uruchom_odliczanie_konkursu(
    message, sekundy, nagroda, liczba_zwyciezcow, view, baner_url=None
):
  await asyncio.sleep(sekundy)
  view.zakonczony = True
  for item in view.children:
    item.disabled = True

  pul = list(dict.fromkeys(view.uczestnicy))
  ile_losowac = min(liczba_zwyciezcow, len(pul))
  zwyciezcy = random.sample(pul, ile_losowac) if ile_losowac > 0 else []

  final_embed = zbuduj_embed_konkursu_zakonczonego(
      message.guild, nagroda, zwyciezcy, pul, baner_url
  )
  try:
    await message.edit(embed=final_embed, view=view)
  except Exception:
    pass

  if zwyciezcy:
    wzmianki = ", ".join(f"<@{uid}>" for uid in zwyciezcy)
    try:
      await message.channel.send(
          f"🎉 **Konkurs zakończony!** Gratulacje dla {wzmianki} — wygraliście"
          f" `{nagroda}`!"
      )
    except Exception:
      pass
  else:
    try:
      await message.channel.send(
          f"ℹ️ **Konkurs na `{nagroda}` zakończył się bez wyłaniania"
          " zwycięzców (brak uczestników).**"
      )
    except Exception:
      pass


# ----------------- MODALE I WIDOKI ZAKUPÓW ORAZ SKUPU ----------------- #


class PurchaseModal(discord.ui.Modal, title="✨ Stwórz zamówienie w Emerald Shop"):
  przedmiot = discord.ui.TextInput(
      label="Co chcesz kupić?",
      placeholder="Np. Ranga VIP / 50000$",
      required=True,
      max_length=100,
  )
  kwota = discord.ui.TextInput(
      label="Kwota w PLN (wpisz samą liczbę)",
      placeholder="Np. 150",
      required=True,
      max_length=100,
  )
  uwagi = discord.ui.TextInput(
      label="Twój Nick w grze",
      placeholder="Dokładny nick",
      required=True,
      max_length=100,
  )

  def __init__(self, tryb_nazwa):
    super().__init__()
    self.tryb_nazwa = tryb_nazwa

  async def on_submit(self, interaction: discord.Interaction):
    guild = interaction.guild
    user = interaction.user
    c_name = "🛒│zakup-" + user.name.lower()
    if discord.utils.get(guild.channels, name=c_name):
      await interaction.response.send_message(
          "⚠️ **Masz już otwarty kanał zakupu!**", ephemeral=True
      )
      return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(
            read_messages=False, view_channel=False, send_messages=False
        ),
        user: discord.PermissionOverwrite(
            read_messages=True, view_channel=True, send_messages=True
        ),
        guild.me: discord.PermissionOverwrite(
            read_messages=True,
            view_channel=True,
            send_messages=True,
            manage_channels=True,
        ),
    }
    zweryfikowany_role = guild.get_role(WERYFIKOWANY_ROLE_ID)
    if zweryfikowany_role:
      overwrites[zweryfikowany_role] = discord.PermissionOverwrite(
          read_messages=False, view_channel=False
      )

    for rid in ADMIN_ROLE_IDS:
      r = guild.get_role(rid)
      if r:
        overwrites[r] = discord.PermissionOverwrite(
            read_messages=True, view_channel=True, send_messages=True
        )
    lr = guild.get_role(LIDER_ROLE_ID)
    if lr:
      overwrites[lr] = discord.PermissionOverwrite(
          read_messages=True, view_channel=True, send_messages=True
      )

    kat_ticketow = discord.utils.get(
        guild.categories, name="🎟️ ── TICKETY"
    ) or await guild.create_category("🎟️ ── TICKETY")
    chan = await guild.create_text_channel(
        name=c_name, category=kat_ticketow, overwrites=overwrites
    )

    bazowa_wartosc = parsuj_kwote(self.kwota.value)

    embed = discord.Embed(
        title="🎟️ ── **NOWE ZGŁOSZENIE ZAMÓWIENIA** ── 🎟️",
        color=discord.Color.from_rgb(46, 204, 113),
    )
    embed.add_field(name="👤 **Klient**", value=user.mention, inline=True)
    embed.add_field(name="🎮 **Tryb**", value=f"`{self.tryb_nazwa}`", inline=True)
    embed.add_field(
        name="📦 **Przedmiot**", value=f"`{self.przedmiot.value}`", inline=False
    )
    embed.add_field(
        name="💰 **Kwota bazowa**",
        value=f"`{bazowa_wartosc:.2f} PLN`",
        inline=True,
    )
    embed.add_field(
        name="🏷️ **Nick w grze**", value=f"`{self.uwagi.value}`", inline=True
    )
    embed.add_field(
        name="💳 **Forma płatności**",
        value="⭐ *Oczekiwanie na wybór klienta...*",
        inline=False,
    )
    embed.set_footer(text="✨ Emerald Shop ✕ System Zamówień ✨")

    view_obj = TicketControlView(
        user, self.tryb_nazwa, self.przedmiot.value, bazowa_wartosc
    )
    await chan.send(embed=embed, view=view_obj)
    await interaction.response.send_message(
        f"✅ **Pomyślnie utworzono kanał zamówienia:** {chan.mention}",
        ephemeral=True,
    )


class SkupModal(discord.ui.Modal, title="✨ Zgłoś skup waluty/itemów"):
  przedmiot = discord.ui.TextInput(
      label="Co nam sprzedajesz?",
      placeholder="Np. 500000$ / Itemy",
      required=True,
      max_length=100,
  )
  oczekiwana_kwota = discord.ui.TextInput(
      label="Kwota w PLN (wpisz samą liczbę)",
      placeholder="Np. 50",
      required=True,
      max_length=100,
  )
  uwagi = discord.ui.TextInput(
      label="Twój Nick w grze",
      placeholder="Dokładny nick",
      required=True,
      max_length=100,
  )

  def __init__(self, tryb_nazwa):
    super().__init__()
    self.tryb_nazwa = tryb_nazwa

  async def on_submit(self, interaction: discord.Interaction):
    guild = interaction.guild
    user = interaction.user
    c_name = "💰│skup-" + user.name.lower()
    if discord.utils.get(guild.channels, name=c_name):
      await interaction.response.send_message(
          "⚠️ **Masz już otwarty kanał skupu!**", ephemeral=True
      )
      return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(
            read_messages=False, view_channel=False, send_messages=False
        ),
        user: discord.PermissionOverwrite(
            read_messages=True, view_channel=True, send_messages=True
        ),
        guild.me: discord.PermissionOverwrite(
            read_messages=True,
            view_channel=True,
            send_messages=True,
            manage_channels=True,
        ),
    }
    zweryfikowany_role = guild.get_role(WERYFIKOWANY_ROLE_ID)
    if zweryfikowany_role:
      overwrites[zweryfikowany_role] = discord.PermissionOverwrite(
          read_messages=False, view_channel=False
      )

    for rid in ADMIN_ROLE_IDS:
      r = guild.get_role(rid)
      if r:
        overwrites[r] = discord.PermissionOverwrite(
            read_messages=True, view_channel=True, send_messages=True
        )
    lr = guild.get_role(LIDER_ROLE_ID)
    if lr:
      overwrites[lr] = discord.PermissionOverwrite(
          read_messages=True, view_channel=True, send_messages=True
      )

    kat_ticketow = discord.utils.get(
        guild.categories, name="🎟️ ── TICKETY"
    ) or await guild.create_category("🎟️ ── TICKETY")
    chan = await guild.create_text_channel(
        name=c_name, category=kat_ticketow, overwrites=overwrites
    )

    bazowa_wartosc = parsuj_kwote(self.oczekiwana_kwota.value)

    embed = discord.Embed(
        title="💰 ── **NOWE ZGŁOSZENIE SKUPU** ── 💰",
        color=discord.Color.from_rgb(241, 196, 15),
    )
    embed.add_field(
        name="👤 **Sprzedający (Klient)**", value=user.mention, inline=True
    )
    embed.add_field(name="🎮 **Tryb**", value=f"`{self.tryb_nazwa}`", inline=True)
    embed.add_field(
        name="📦 **Przedmiot / Waluta**",
        value=f"`{self.przedmiot.value}`",
        inline=False,
    )
    embed.add_field(
        name="💰 **Kwota bazowa**",
        value=f"`{bazowa_wartosc:.2f} PLN`",
        inline=True,
    )
    embed.add_field(
        name="🏷️ **Nick w grze**", value=f"`{self.uwagi.value}`", inline=True
    )
    embed.add_field(
        name="💳 **Forma wypłaty**",
        value="⭐ *Oczekiwanie na wybór klienta...*",
        inline=False,
    )
    embed.set_footer(text="✨ Emerald Shop ✕ System Skupu ✨")

    view_obj = SkupControlView(
        user, self.tryb_nazwa, self.przedmiot.value, bazowa_wartosc
    )
    await chan.send(embed=embed, view=view_obj)
    await interaction.response.send_message(
        f"✅ **Pomyślnie utworzono kanał skupu:** {chan.mention}", ephemeral=True
    )


class TicketControlView(discord.ui.View):

  def __init__(self, client, tryb_nazwa, przedmiot, bazowa_kwota):
    super().__init__(timeout=None)
    self.client = client
    self.claimed_by = None
    self.tryb_nazwa = tryb_nazwa
    self.przedmiot = przedmiot
    self.bazowa_kwota = bazowa_kwota
    self.wybrana_platnosc_ticket = "⭐ Nie wybrano"
    self.wybrana_platnosc_legit = f"BLIK (Zapłacono: {bazowa_kwota:.2f} PLN)"
    self.koncowa_kwota_transakcji = bazowa_kwota

    self.payment_select = discord.ui.Select(
        placeholder="💳 Wybierz formę płatności...",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="Kod BLIK", description="Podatek +10%", emoji="🟢"
            ),
            discord.SelectOption(
                label="Przelew na numer (BLIK)",
                description="Podatek 0%",
                emoji="🔵",
            ),
            discord.SelectOption(
                label="Paysafecard", description="Podatek +15%", emoji="🟠"
            ),
            discord.SelectOption(
                label="LTC", description="Podatek +5%", emoji="🟣"
            ),
        ],
    )
    self.payment_select.callback = self.payment_callback
    self.add_item(self.payment_select)

  async def payment_callback(self, interaction: discord.Interaction):
    wybor = self.payment_select.values[0]
    (
        self.koncowa_kwota_transakcji,
        self.wybrana_platnosc_ticket,
        self.wybrana_platnosc_legit,
    ) = oblicz_platnosc_zakup(wybor, self.bazowa_kwota)

    try:
      emb = interaction.message.embeds[0]
      for i, field in enumerate(emb.fields):
        if field.name in [
            "💳 **Forma płatności**",
            "💳 **Wybrana płatność**",
            "💳 Status płatności",
        ]:
          emb.set_field_at(
              i,
              name="💳 **Forma płatności**",
              value=f"`{self.wybrana_platnosc_ticket}`",
              inline=False,
          )
          break
      await interaction.message.edit(embed=emb)
    except Exception:
      pass

    await interaction.response.send_message(
        f"✅ **Wybrano metodę płatności:** `{wybor}`. **Kwota po zmianie:**"
        f" `{self.koncowa_kwota_transakcji:.2f} PLN`",
        ephemeral=True,
    )

  @discord.ui.button(
      label="🛡️ Przejmij",
      style=discord.ButtonStyle.success,
      custom_id="take_btn",
  )
  async def take(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    if not sprawdzenie_kadry(interaction.user):
      await interaction.response.send_message(
          "⛔ **Brak uprawnień!**", ephemeral=True
      )
      return
    if self.claimed_by:
      await interaction.response.send_message(
          "⚠️ **Ten kanał jest już przejęty!**", ephemeral=True
      )
      return
    self.claimed_by = interaction.user
    button.disabled = True
    button.label = f"Przejęte ({interaction.user.name})"
    await interaction.message.edit(view=self)
    await interaction.response.send_message(
        f"✅ **Przejęte przez:** {interaction.user.mention}",
        allowed_mentions=discord.AllowedMentions(users=True),
    )

  @discord.ui.button(
      label="🔔 Pinguj kadrę",
      style=discord.ButtonStyle.secondary,
      custom_id="ping_btn",
  )
  async def ping(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    pings = [
        interaction.guild.get_role(rid).mention
        for rid in ADMIN_ROLE_IDS
        if interaction.guild.get_role(rid)
    ]
    lr = interaction.guild.get_role(LIDER_ROLE_ID)
    if lr:
      pings.append(lr.mention)
    if pings:
      await interaction.channel.send(
          " ".join(pings) + " 🔔 **Potrzebna pomoc na kanale!**",
          allowed_mentions=discord.AllowedMentions(roles=True),
      )
      await interaction.response.send_message(
          "✅ **Spingowano kadrę.**", ephemeral=True
      )
    else:
      await interaction.response.send_message(
          "⚠️ **Brak ról do spingowania.**", ephemeral=True
      )

  @discord.ui.button(
      label="📋 Wystaw Legit",
      style=discord.ButtonStyle.success,
      custom_id="wystaw_btn",
  )
  async def wystaw(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    if not sprawdzenie_kadry(interaction.user):
      await interaction.response.send_message(
          "⛔ **Brak uprawnień!**", ephemeral=True
      )
      return

    sprzedawca = self.claimed_by if self.claimed_by else interaction.user
    if self.koncowa_kwota_transakcji > 0:
      dodaj_statystyke_zamowienia(self.koncowa_kwota_transakcji)

    view = LegitCheckChoiceView(
        self.client,
        sprzedawca,
        self.tryb_nazwa,
        self.przedmiot,
        self.wybrana_platnosc_legit,
        typ_transakcji="Zakup",
    )
    embed = discord.Embed(
        title="🛡️ ── **EMERALD SHOP ✕ WYSTAW LEGIT** ── 🛡️",
        color=discord.Color.from_rgb(46, 204, 113),
    )
    embed.add_field(
        name="👤 **Sprzedawca**", value=sprzedawca.mention, inline=True
    )
    embed.add_field(
        name="📌 **Serwer / Tryb**", value=f"`{self.tryb_nazwa}`", inline=True
    )
    embed.add_field(
        name="📦 **Szczegóły**",
        value=(
            f"Produkt: `{self.przedmiot}`\nPłatność:"
            f" `{self.wybrana_platnosc_legit}`"
        ),
        inline=False,
    )
    embed.set_footer(text="✨ Wybierz widoczność poniżej ✨")
    await interaction.channel.send(
        embed=embed,
        view=view,
        allowed_mentions=discord.AllowedMentions(users=True),
    )
    await interaction.response.send_message(
        "✅ **Wygenerowano tabelę legitchecka!**", ephemeral=True
    )

  @discord.ui.button(
      label="🔒 Usuń kanał",
      style=discord.ButtonStyle.danger,
      custom_id="delete_ticket_btn",
  )
  async def delete_ticket(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    user = interaction.user
    if not (
        user.guild_permissions.administrator
        or any(r.id == LIDER_ROLE_ID for r in user.roles)
        or self.claimed_by == user
    ):
      await interaction.response.send_message(
          "⛔ **Brak uprawnień do usunięcia kanału!**", ephemeral=True
      )
      return
    await interaction.response.send_message(
        "🔒 **Usuwanie kanału za 3 sekundy...**", ephemeral=True
    )
    await asyncio.sleep(3)
    try:
      await interaction.channel.delete()
    except Exception:
      pass


class SkupControlView(discord.ui.View):

  def __init__(self, client, tryb_nazwa, przedmiot, bazowa_kwota):
    super().__init__(timeout=None)
    self.client = client
    self.claimed_by = None
    self.tryb_nazwa = tryb_nazwa
    self.przedmiot = przedmiot
    self.bazowa_kwota = bazowa_kwota
    self.wybrana_platnosc_ticket = "⭐ Nie wybrano"
    self.wybrana_platnosc_legit = f"BLIK (Wypłacono: {bazowa_kwota:.2f} PLN)"
    self.koncowa_kwota_transakcji = bazowa_kwota

    self.payment_select = discord.ui.Select(
        placeholder="💳 Wybierz formę wypłaty (zniżka wg %)",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="Kod BLIK", description="Potrącenie -10%", emoji="🟢"
            ),
            discord.SelectOption(
                label="Przelew na numer (BLIK)",
                description="Potrącenie 0%",
                emoji="🔵",
            ),
            discord.SelectOption(
                label="Paysafecard", description="Potrącenie -15%", emoji="🟠"
            ),
            discord.SelectOption(
                label="LTC", description="Potrącenie -5%", emoji="🟣"
            ),
        ],
    )
    self.payment_select.callback = self.payment_callback
    self.add_item(self.payment_select)

  async def payment_callback(self, interaction: discord.Interaction):
    wybor = self.payment_select.values[0]
    (
        self.koncowa_kwota_transakcji,
        self.wybrana_platnosc_ticket,
        self.wybrana_platnosc_legit,
    ) = oblicz_platnosc_skup(wybor, self.bazowa_kwota)

    try:
      emb = interaction.message.embeds[0]
      for i, field in enumerate(emb.fields):
        if field.name in [
            "💳 **Forma wypłaty**",
            "💳 **Forma płatności**",
            "💳 **Wybrana płatność**",
        ]:
          emb.set_field_at(
              i,
              name="💳 **Forma wypłaty**",
              value=f"`{self.wybrana_platnosc_ticket}`",
              inline=False,
          )
          break
      await interaction.message.edit(embed=emb)
    except Exception:
      pass

    await interaction.response.send_message(
        f"✅ **Wybrano metodę wypłaty:** `{wybor}`. **Kwota po zmianie:**"
        f" `{self.koncowa_kwota_transakcji:.2f} PLN`",
        ephemeral=True,
    )

  @discord.ui.button(
      label="🛡️ Przejmij",
      style=discord.ButtonStyle.success,
      custom_id="skup_take_btn",
  )
  async def take(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    if not sprawdzenie_kadry(interaction.user):
      await interaction.response.send_message(
          "⛔ **Brak uprawnień!**", ephemeral=True
      )
      return
    if self.claimed_by:
      await interaction.response.send_message(
          "⚠️ **Ten kanał jest już przejęty!**", ephemeral=True
      )
      return
    self.claimed_by = interaction.user
    button.disabled = True
    button.label = f"Przejęte ({interaction.user.name})"
    await interaction.message.edit(view=self)
    await interaction.response.send_message(
        f"✅ **Przejęte przez:** {interaction.user.mention}",
        allowed_mentions=discord.AllowedMentions(users=True),
    )

  @discord.ui.button(
      label="🔔 Pinguj kadrę",
      style=discord.ButtonStyle.secondary,
      custom_id="skup_ping_btn",
  )
  async def ping(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    pings = [
        interaction.guild.get_role(rid).mention
        for rid in ADMIN_ROLE_IDS
        if interaction.guild.get_role(rid)
    ]
    lr = interaction.guild.get_role(LIDER_ROLE_ID)
    if lr:
      pings.append(lr.mention)
    if pings:
      await interaction.channel.send(
          " ".join(pings) + " 🔔 **Potrzebna pomoc przy skupie!**",
          allowed_mentions=discord.AllowedMentions(roles=True),
      )
      await interaction.response.send_message(
          "✅ **Spingowano kadrę.**", ephemeral=True
      )
    else:
      await interaction.response.send_message(
          "⚠️ **Brak ról do spingowania.**", ephemeral=True
      )

  @discord.ui.button(
      label="📋 Wystaw Legit",
      style=discord.ButtonStyle.success,
      custom_id="skup_wystaw_btn",
  )
  async def wystaw(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    if not sprawdzenie_kadry(interaction.user):
      await interaction.response.send_message(
          "⛔ **Brak uprawnień!**", ephemeral=True
      )
      return

    kupujacy_skup = self.claimed_by if self.claimed_by else interaction.user
    if self.koncowa_kwota_transakcji > 0:
      dodaj_statystyke_skupu(self.koncowa_kwota_transakcji)

    view = LegitCheckChoiceView(
        self.client,
        kupujacy_skup,
        self.tryb_nazwa,
        self.przedmiot,
        self.wybrana_platnosc_legit,
        typ_transakcji="Skup",
    )
    embed = discord.Embed(
        title="🛡️ ── **EMERALD SHOP ✕ WYSTAW LEGIT (SKUP)** ── 🛡️",
        color=discord.Color.from_rgb(241, 196, 15),
    )
    embed.add_field(
        name="👤 **Sprzedawca / Skupujący**",
        value=kupujacy_skup.mention,
        inline=True,
    )
    embed.add_field(
        name="📌 **Serwer / Tryb**", value=f"`{self.tryb_nazwa}`", inline=True
    )
    embed.add_field(
        name="📦 **Szczegóły**",
        value=(
            f"Itemy: `{self.przedmiot}`\nWypłata:"
            f" `{self.wybrana_platnosc_legit}`"
        ),
        inline=False,
    )
    embed.set_footer(text="✨ Wybierz widoczność poniżej ✨")
    await interaction.channel.send(
        embed=embed,
        view=view,
        allowed_mentions=discord.AllowedMentions(users=True),
    )
    await interaction.response.send_message(
        "✅ **Wygenerowano tabelę legitchecka dla skupu!**", ephemeral=True
    )

  @discord.ui.button(
      label="🔒 Usuń kanał",
      style=discord.ButtonStyle.danger,
      custom_id="skup_delete_ticket_btn",
  )
  async def delete_ticket(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    user = interaction.user
    if not (
        user.guild_permissions.administrator
        or any(r.id == LIDER_ROLE_ID for r in user.roles)
        or self.claimed_by == user
    ):
      await interaction.response.send_message(
          "⛔ **Brak uprawnień do usunięcia kanału!**", ephemeral=True
      )
      return
    await interaction.response.send_message(
        "🔒 **Usuwanie kanału za 3 sekundy...**", ephemeral=True
    )
    await asyncio.sleep(3)
    try:
      await interaction.channel.delete()
    except Exception:
      pass


class LegitCheckChoiceView(discord.ui.View):

  def __init__(
      self,
      client_user,
      staff_user,
      tryb_nazwa,
      przedmiot,
      kwota_info,
      typ_transakcji="Zakup",
  ):
    super().__init__(timeout=None)
    self.client_user = client_user
    self.staff_user = staff_user
    self.tryb_nazwa = tryb_nazwa
    self.przedmiot = przedmiot
    self.kwota_info = kwota_info
    self.typ_transakcji = typ_transakcji
    self._przetwarzanie = False

  async def wyslij_na_legit(
      self, interaction: discord.Interaction, anonimowo: bool
  ):
    if self._przetwarzanie:
      try:
        await interaction.response.send_message(
            "⏳ **Ten legitcheck jest już przetwarzany...**", ephemeral=True
        )
      except Exception:
        pass
      return

    self._przetwarzanie = True

    try:
      await interaction.response.defer(ephemeral=True)
    except discord.NotFound:
      self._przetwarzanie = False
      return
    except Exception:
      pass

    try:
      guild = interaction.guild
      legit_chan = None
      for chan in guild.text_channels:
        if "legit-check" in chan.name.lower():
          legit_chan = chan
          break
      if not legit_chan:
        kat_legit = discord.utils.get(
            guild.categories, name="🛡️ — EMERALD LEGIT"
        ) or await guild.create_category("🛡️ — EMERALD LEGIT")
        legit_chan = await guild.create_text_channel(
            name=f"🛡️│legit-check-{stats_dane.get('legitchecki_licznik', 0)}",
            category=kat_legit,
        )

      czastki = self.tryb_nazwa.split(" - ")
      serwer = czastki[0].strip()
      tryb = czastki[1].strip() if len(czastki) > 1 else self.tryb_nazwa

      klient_etykieta = (
          "⭐ Klient anonimowy"
          if anonimowo
          else f"👤 {self.client_user.mention}"
      )
      formulka_rep = (
          f"+rep <@{self.staff_user.id}> {serwer} {tryb} {self.przedmiot}"
          f" {self.kwota_info}"
      )

      embed = zbuduj_embed_potwierdzonego_legita(
          sprzedawca_mention=self.staff_user.mention,
          klient_etykieta=klient_etykieta,
          serwer=serwer,
          tryb=tryb,
          typ_transakcji=self.typ_transakcji,
          przedmiot=self.przedmiot,
          platnosc_opis=self.kwota_info,
          formulka_rep=formulka_rep,
      )

      wyslana = await legit_chan.send(
          content=f"{self.staff_user.mention}",
          embed=embed,
          allowed_mentions=discord.AllowedMentions(users=True),
      )

      await dodaj_reakcje_legitcheck(wyslana)
      dodaj_legitcheck_stat()
      zapisz_legitcheck_do_historii({
          "numer": stats_dane.get("legitchecki_licznik", 0),
          "data": datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
          "sprzedawca_id": self.staff_user.id,
          "sprzedawca_nazwa": self.staff_user.name,
          "klient_id": None if anonimowo else self.client_user.id,
          "anonimowy": anonimowo,
          "typ": self.typ_transakcji,
          "serwer": serwer,
          "tryb": tryb,
          "produkt": self.przedmiot,
          "platnosc": self.kwota_info,
          "formulka": formulka_rep,
          "wiadomosc_id": wyslana.id,
      })

      await zsynchronizuj_liczniki_i_statystyki(guild, aktualizuj_nazwe_lc=True)

      for child in self.children:
        child.disabled = True
      try:
        await interaction.message.edit(view=self)
      except Exception:
        pass

      try:
        await interaction.followup.send(
            f"✅ **Wysłano legitchecka z reakcjami na** {legit_chan.mention}!",
            ephemeral=True,
        )
      except Exception:
        pass
    finally:
      self._przetwarzanie = False

  @discord.ui.button(
      label="👤 Zostań anonimowy",
      style=discord.ButtonStyle.secondary,
      custom_id="anon_rep_btn",
  )
  async def anon_btn(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await self.wyslij_na_legit(interaction, anonimowo=True)

  @discord.ui.button(
      label="📢 Upublicznij nick",
      style=discord.ButtonStyle.success,
      custom_id="public_rep_btn",
  )
  async def public_btn(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await self.wyslij_na_legit(interaction, anonimowo=False)


class CennikView(discord.ui.View):

  def __init__(self, tryb):
    super().__init__(timeout=None)
    self.tryb = tryb

  @discord.ui.button(
      label="🛒 Stwórz zamówienie",
      style=discord.ButtonStyle.success,
      custom_id="order_btn",
  )
  async def order(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await interaction.response.send_modal(PurchaseModal(self.tryb))

  @discord.ui.button(
      label="⚙️ Edytuj cennik",
      style=discord.ButtonStyle.secondary,
      custom_id="edit_cennik_btn",
  )
  async def edit(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    if not sprawdzenie_kadry(interaction.user):
      await interaction.response.send_message(
          "⛔ **Brak uprawnień!**", ephemeral=True
      )
      return
    prod = cennik_dane.get(self.tryb, [])
    tekst = (
        "\n".join([
            f"{i}. {p.get('ilosc', '')} - {p.get('cena', '')}"
            for i, p in enumerate(prod, 1)
        ])
        or "Brak pozycji."
    )
    await interaction.response.send_message(
        f"✨ **Edycja cennika: {self.tryb}**\n\n{tekst}\n📝 Wpisz na czacie:"
        " `zapisz` lub `nr|przedmiot|cena` lub `dodaj|przedmiot|cena` lub"
        " `usun|nr`",
        ephemeral=True,
    )

    def check(m):
      return m.author == interaction.user and m.channel == interaction.channel

    try:
      msg = await bot.wait_for("message", timeout=60.0, check=check)
      try:
        await msg.delete()
      except Exception:
        pass
      tresc = msg.content.strip()
      if tresc.lower() == "zapisz":
        zapisz_cennik()
        await interaction.followup.send("✅ **Zapisano cennik!**", ephemeral=True)
        return
      parts = [p.strip() for p in tresc.split("|")]
      op = parts[0].lower()
      if self.tryb not in cennik_dane:
        cennik_dane[self.tryb] = []
      lista = cennik_dane[self.tryb]
      if (op == "usun" or op == "usuń") and len(parts) == 2:
        nr = int(parts[1]) - 1
        if 0 <= nr < len(lista):
          lista.pop(nr)
          zapisz_cennik()
          await interaction.message.edit(
              embed=stworz_embed_cennika(self.tryb, lista),
              view=CennikView(self.tryb),
          )
          await interaction.followup.send("🗑️ **Usunięto!**", ephemeral=True)
      elif op == "dodaj" and len(parts) == 3 and len(lista) < 3:
        lista.append({"ilosc": parts[1], "cena": parts[2]})
        zapisz_cennik()
        await interaction.message.edit(
            embed=stworz_embed_cennika(self.tryb, lista),
            view=CennikView(self.tryb),
        )
        await interaction.followup.send("➕ **Dodano!**", ephemeral=True)
      elif len(parts) == 3:
        nr = int(parts[0]) - 1
        if 0 <= nr < len(lista):
          lista[nr] = {"ilosc": parts[1], "cena": parts[2]}
          zapisz_cennik()
          await interaction.message.edit(
              embed=stworz_embed_cennika(self.tryb, lista),
              view=CennikView(self.tryb),
          )
          await interaction.followup.send("🔄 **Zaktualizowano!**", ephemeral=True)
    except asyncio.TimeoutError:
      await interaction.followup.send("⌛ **Czas minął.**", ephemeral=True)
    except Exception as e:
      await interaction.followup.send(f"❌ **Błąd:** {e}", ephemeral=True)


class SkupView(discord.ui.View):

  def __init__(self, tryb):
    super().__init__(timeout=None)
    self.tryb = tryb

  @discord.ui.button(
      label="💰 Zgłoś skup",
      style=discord.ButtonStyle.success,
      custom_id="skup_btn",
  )
  async def skup(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await interaction.response.send_modal(SkupModal(self.tryb))

  @discord.ui.button(
      label="⚙️ Edytuj skup",
      style=discord.ButtonStyle.secondary,
      custom_id="edit_skup_btn",
  )
  async def edit(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    if not sprawdzenie_kadry(interaction.user):
      await interaction.response.send_message(
          "⛔ **Brak uprawnień!**", ephemeral=True
      )
      return
    prod = skup_dane.get(self.tryb, [])
    tekst = (
        "\n".join([
            f"{i}. {p.get('ilosc', '')} - {p.get('cena', '')}"
            for i, p in enumerate(prod, 1)
        ])
        or "Brak pozycji."
    )
    await interaction.response.send_message(
        f"✨ **Edycja skupu: {self.tryb}**\n\n{tekst}\n📝 Wpisz na czacie:"
        " `zapisz` lub `nr|przedmiot|cena` lub `dodaj|przedmiot|cena` lub"
        " `usun|nr`",
        ephemeral=True,
    )

    def check(m):
      return m.author == interaction.user and m.channel == interaction.channel

    try:
      msg = await bot.wait_for("message", timeout=60.0, check=check)
      try:
        await msg.delete()
      except Exception:
        pass
      tresc = msg.content.strip()
      if tresc.lower() == "zapisz":
        zapisz_skup()
        await interaction.followup.send("✅ **Zapisano skup!**", ephemeral=True)
        return
      parts = [p.strip() for p in tresc.split("|")]
      op = parts[0].lower()
      if self.tryb not in skup_dane:
        skup_dane[self.tryb] = []
      lista = skup_dane[self.tryb]
      if (op == "usun" or op == "usuń") and len(parts) == 2:
        nr = int(parts[1]) - 1
        if 0 <= nr < len(lista):
          lista.pop(nr)
          zapisz_skup()
          await interaction.message.edit(
              embed=stworz_embed_skupu(self.tryb, lista), view=SkupView(self.tryb)
          )
          await interaction.followup.send("🗑️ **Usunięto!**", ephemeral=True)
      elif op == "dodaj" and len(parts) == 3 and len(lista) < 3:
        lista.append({"ilosc": parts[1], "cena": parts[2]})
        zapisz_skup()
        await interaction.message.edit(
            embed=stworz_embed_skupu(self.tryb, lista), view=SkupView(self.tryb)
        )
        await interaction.followup.send("➕ **Dodano!**", ephemeral=True)
      elif len(parts) == 3:
        nr = int(parts[0]) - 1
        if 0 <= nr < len(lista):
          lista[nr] = {"ilosc": parts[1], "cena": parts[2]}
          zapisz_skup()
          await interaction.message.edit(
              embed=stworz_embed_skupu(self.tryb, lista), view=SkupView(self.tryb)
          )
          await interaction.followup.send("🔄 **Zaktualizowano!**", ephemeral=True)
    except asyncio.TimeoutError:
      await interaction.followup.send("⌛ **Czas minął.**", ephemeral=True)
    except Exception as e:
      await interaction.followup.send(f"❌ **Błąd:** {e}", ephemeral=True)


class RecruitModal(discord.ui.Modal, title="📋 Ticket rekrutacyjny na Sprzedawcę"):
  wiek = discord.ui.TextInput(
      label="1. Ile masz lat?",
      placeholder="Wpisz swój wiek",
      required=True,
      max_length=10,
  )
  doswiadczenie = discord.ui.TextInput(
      label="2. Doświadczenie na innych shopach?",
      placeholder="Opisz swoje doświadczenie",
      required=True,
      max_length=200,
  )
  serwery = discord.ui.TextInput(
      label="3. Z jakich trybów chcesz sprzedawać?",
      placeholder="Np. Anarchia.gg",
      required=True,
      max_length=100,
  )
  umiejetnosci = discord.ui.TextInput(
      label="4. Umiejętności w skali 1/10?",
      placeholder="Np. 9/10",
      required=True,
      max_length=10,
  )
  kaucja_zgoda = discord.ui.TextInput(
      label="5. Czy jesteś świadom płacenia kaucji?",
      placeholder="Tak / Nie",
      required=True,
      max_length=10,
  )

  async def on_submit(self, interaction: discord.Interaction):
    guild = interaction.guild
    user = interaction.user
    c_name = "📋│rekrutacja-" + user.name.lower()
    if discord.utils.get(guild.channels, name=c_name):
      await interaction.response.send_message(
          "⚠️ **Masz już otwarty ticket rekrutacyjny!**", ephemeral=True
      )
      return

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(
            read_messages=False, view_channel=False, send_messages=False
        ),
        user: discord.PermissionOverwrite(
            read_messages=True, view_channel=True, send_messages=True
        ),
        guild.me: discord.PermissionOverwrite(
            read_messages=True,
            view_channel=True,
            send_messages=True,
            manage_channels=True,
        ),
    }
    for rid in ADMIN_ROLE_IDS:
      r = guild.get_role(rid)
      if r:
        overwrites[r] = discord.PermissionOverwrite(
            read_messages=True, view_channel=True, send_messages=True
        )
    lr = guild.get_role(LIDER_ROLE_ID)
    if lr:
      overwrites[lr] = discord.PermissionOverwrite(
          read_messages=True, view_channel=True, send_messages=True
      )

    kat_ticketow = discord.utils.get(
        guild.categories, name="🎟️ ── TICKETY"
    ) or await guild.create_category("🎟️ ── TICKETY")
    chan = await guild.create_text_channel(
        name=c_name, category=kat_ticketow, overwrites=overwrites
    )

    embed = discord.Embed(
        title="📋 ── **NOWY TICKET REKRUTACYJNY** ── 📋",
        color=discord.Color.from_rgb(46, 204, 113),
    )
    embed.add_field(name="👤 Kandydat", value=user.mention, inline=False)
    embed.add_field(name="1. Wiek", value=f"`{self.wiek.value}`", inline=True)
    embed.add_field(
        name="4. Umiejętności", value=f"`{self.umiejetnosci.value}`", inline=True
    )
    embed.add_field(
        name="3. Tryby", value=f"`{self.serwery.value}`", inline=False
    )
    embed.add_field(
        name="2. Doświadczenie",
        value=f"`{self.doswiadczenie.value}`",
        inline=False,
    )
    embed.add_field(
        name="5. Kaucja", value=f"`{self.kaucja_zgoda.value}`", inline=False
    )
    embed.set_footer(text="✨ Poczekaj na odpowiedź kadry wyższej ✨")

    view = TicketDeleteOnlyView()
    await chan.send(embed=embed, view=view)
    await interaction.response.send_message(
        f"✅ **Utworzono ticket rekrutacyjny:** {chan.mention}", ephemeral=True
    )


class RecruitSetupView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(
      label="📋 Stwórz ticket rekrutacyjny",
      style=discord.ButtonStyle.success,
      custom_id="persistent_recruit_ticket_btn",
  )
  async def recruit_btn(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    await interaction.response.send_modal(RecruitModal())


class TicketDeleteOnlyView(discord.ui.View):

  def __init__(self):
    super().__init__(timeout=None)

  @discord.ui.button(
      label="🔒 Usuń kanał",
      style=discord.ButtonStyle.danger,
      custom_id="delete_recruit_btn",
  )
  async def delete_btn(
      self, interaction: discord.Interaction, button: discord.ui.Button
  ):
    user = interaction.user
    if not (
        user.guild_permissions.administrator
        or any(r.id == LIDER_ROLE_ID for r in user.roles)
        or sprawdzenie_kadry(user)
    ):
      await interaction.response.send_message(
          "⛔ **Brak uprawnień!**", ephemeral=True
      )
      return
    await interaction.response.send_message(
        "🔒 **Usuwanie kanału za 3 sekundy...**", ephemeral=True
    )
    await asyncio.sleep(3)
    try:
      await interaction.channel.delete()
    except Exception:
      pass


@tasks.loop(minutes=1)
async def sprawdz_polnoc_loop():
  await sprawdz_polnoc_i_nowa_tabele()


@sprawdz_polnoc_loop.before_loop
async def before_sprawdz_polnoc_loop():
  await bot.wait_until_ready()


@tasks.loop(minutes=5)
async def odswiez_statystyki_loop():
  await sprawdz_polnoc_i_nowa_tabele()
  for guild in bot.guilds:
    await zsynchronizuj_liczniki_i_statystyki(guild, aktualizuj_nazwe_lc=False)


@odswiez_statystyki_loop.before_loop
async def before_odswiez_statystyki_loop():
  await bot.wait_until_ready()


@bot.event
async def on_member_join(member):
  if member.bot:
    return
  await sprawdz_polnoc_i_nowa_tabele()
  stats_dane["dolaczylo"] = stats_dane.get("dolaczylo", 0) + 1
  zapisz_statystyki()


@bot.event
async def on_member_remove(member):
  if member.bot:
    return
  await sprawdz_polnoc_i_nowa_tabele()
  stats_dane["wyszlo"] = stats_dane.get("wyszlo", 0) + 1
  zapisz_statystyki()


@bot.event
async def on_message(message):
  if message.guild and not message.author.bot:
    nazwa_kanalu = message.channel.name.lower()
    if "legit-check" in nazwa_kanalu:
      if "+rep" in message.content.lower():
        await dodaj_reakcje_legitcheck(message)
        dodaj_legitcheck_stat()
        zapisz_legitcheck_do_historii({
            "numer": stats_dane.get("legitchecki_licznik", 0),
            "data": datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
            "autor_id": message.author.id,
            "autor_nazwa": message.author.name,
            "tresc": message.content,
            "wiadomosc_id": message.id,
        })
        await zsynchronizuj_liczniki_i_statystyki(
            message.guild, aktualizuj_nazwe_lc=True
        )
    elif "czy-jesteśmy-legit" in nazwa_kanalu or "czy-jestesmy-legit" in nazwa_kanalu:
      await dodaj_reakcje_czy_legit(message)

  await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload):
  if payload.member is None or payload.member.bot:
    return
  guild = bot.get_guild(payload.guild_id)
  if not guild:
    return
  channel = guild.get_channel(payload.channel_id)
  if (
      channel
      and "weryfikacja" in channel.name.lower()
      and str(payload.emoji) == "✅"
  ):
    role = guild.get_role(WERYFIKOWANY_ROLE_ID)
    if role and role not in payload.member.roles:
      try:
        await payload.member.add_roles(
            role, reason="Zweryfikowano poprzez kanał weryfikacji (reakcja ✅)"
        )
      except Exception:
        pass


@bot.event
async def on_raw_reaction_remove(payload):
  guild = bot.get_guild(payload.guild_id)
  if not guild:
    return
  channel = guild.get_channel(payload.channel_id)
  if (
      channel
      and "weryfikacja" in channel.name.lower()
      and str(payload.emoji) == "✅"
  ):
    member = guild.get_member(payload.user_id)
    if member and not member.bot:
      role = guild.get_role(WERYFIKOWANY_ROLE_ID)
      if role and role in member.roles:
        try:
          await member.remove_roles(
              role, reason="Usunięto reakcję ✅ z weryfikacji"
          )
        except Exception:
          pass


@bot.event
async def on_ready():
  bot.add_view(RecruitSetupView())
  print("\n" + "=" * 50)
  print(" [SUKCES] BOT EMERALD SHOP ZOSTAŁ URUCHOMIONY I JEST ONLINE!")
  print(f" Zalogowano jako: {bot.user.name} (ID: {bot.user.id})")
  print("=" * 50 + "\n")
  await sprawdz_polnoc_i_nowa_tabele()
  for guild in bot.guilds:
    await cache_all_invites(guild)
    await zsynchronizuj_liczniki_i_statystyki(guild, aktualizuj_nazwe_lc=False)
  await bot.change_presence(
      status=discord.Status.online,
      activity=discord.Game(name="Emerald Shop 🛒 | !setup_emerald"),
  )
  if not sprawdz_polnoc_loop.is_running():
    sprawdz_polnoc_loop.start()
  if not odswiez_statystyki_loop.is_running():
    odswiez_statystyki_loop.start()


async def zbuduj_strukture_serwera(
    guild, usun_istniejace=False, resetuj_statystyki=False
):
  global cennik_dane, skup_dane, stats_dane
  cennik_dane = wczytaj_plik(PLIK_CENNIK, domyslne_dane_cennik)
  skup_dane = wczytaj_plik(PLIK_SKUP, domyslne_dane_skup)
  if resetuj_statystyki:
    stats_dane = stworz_puste_statystyki(0)
  else:
    stats_dane = wczytaj_statystyki()
    stats_dane["aktywna_wiadomosc_stats_id"] = None
  zapisz_cennik()
  zapisz_skup()
  zapisz_statystyki()

  if usun_istniejace:
    for ch in list(guild.channels):
      if ch.category and ch.category.name == "🎟️ ── TICKETY":
        continue
      try:
        await ch.delete()
      except Exception:
        pass

  zweryfikowany_role = guild.get_role(WERYFIKOWANY_ROLE_ID)

  overwrites_tylko_zweryfikowany = {
      guild.default_role: discord.PermissionOverwrite(
          read_messages=False, view_channel=False, send_messages=False
      ),
      guild.me: discord.PermissionOverwrite(
          read_messages=True, view_channel=True, send_messages=True
      ),
  }
  if zweryfikowany_role:
    overwrites_tylko_zweryfikowany[zweryfikowany_role] = (
        discord.PermissionOverwrite(
            read_messages=True, view_channel=True, send_messages=False
        )
    )

  # 0. Weryfikacja
  overwrites_weryfikacja = {
      guild.default_role: discord.PermissionOverwrite(
          read_messages=True,
          view_channel=True,
          send_messages=False,
          add_reactions=True,
      ),
      guild.me: discord.PermissionOverwrite(
          read_messages=True,
          send_messages=True,
          manage_channels=True,
          view_channel=True,
      ),
  }
  kat_weryfikacja = discord.utils.get(
      guild.categories, name="🔒 ── WERYFIKACJA"
  ) or await guild.create_category(
      "🔒 ── WERYFIKACJA", overwrites=overwrites_weryfikacja, position=0
  )
  await kat_weryfikacja.edit(overwrites=overwrites_weryfikacja)

  ver_chan = discord.utils.get(
      kat_weryfikacja.text_channels, name="✅│weryfikacja"
  ) or await guild.create_text_channel(
      name="✅│weryfikacja",
      category=kat_weryfikacja,
      overwrites=overwrites_weryfikacja,
  )
  await ver_chan.edit(overwrites=overwrites_weryfikacja)

  async for m in ver_chan.history(limit=5):
    if m.author == bot.user:
      try:
        await m.delete()
      except discord.NotFound:
        pass

  embed_ver = discord.Embed(
      title="🌟 ── **EMERALD SHOP ✕ WERYFIKACJA** ── 🌟",
      description=(
          "Witaj na oficjalnym serwerze **Emerald Shop**!\n\nAby odblokować"
          " dostęp do całego serwera (cenniki, zakupy, skup waluty, czat), musisz"
          " się zweryfikować.\n\n🔓 **Instrukcja:**\nKliknij zieloną reakcję"
          " **(✅)** poniżej tej wiadomości!"
      ),
      color=discord.Color.from_rgb(46, 204, 113),
  )
  embed_ver.set_footer(text="✨ Emerald Shop ✕ System Weryfikacji ✨")
  msg_ver = await ver_chan.send(embed=embed_ver)
  try:
    await msg_ver.add_reaction("✅")
  except Exception:
    pass

  async def stworz_kategorie_bezpieczna(nazwa, pos):
    kat = discord.utils.get(
        guild.categories, name=nazwa
    ) or await guild.create_category(
        nazwa, overwrites=overwrites_tylko_zweryfikowany, position=pos
    )
    await kat.edit(overwrites=overwrites_tylko_zweryfikowany)
    return kat

  # 1. Dołączenia
  kat_dolaczenia = await stworz_kategorie_bezpieczna("👋 ── DOŁĄCZENIA", 1)
  for cname in ["👋│dołączenia", "🎟️│zaproszenia"]:
    ch = discord.utils.get(
        kat_dolaczenia.text_channels, name=cname
    ) or await guild.create_text_channel(name=cname, category=kat_dolaczenia)
    await ch.edit(overwrites=overwrites_tylko_zweryfikowany)

  # 2. Sklep
  kat_sklep = await stworz_kategorie_bezpieczna("🛒 ── SKLEP EMERALD", 2)
  tryby = [
      ("🔥│anarchia-lifesteal", "Anarchia.gg - Lifesteal"),
      ("🔥│anarchia-boxpvp", "Anarchia.gg - BoxPVP"),
      ("⭐│minestar-skypvp", "Minestar.gg - SkyPvP"),
      ("⭐│minestar-lifesteal", "Minestar.gg - Lifesteal"),
      ("💎│rapy-earthsmp", "Rapy.gg - EarthSMP"),
      ("💎│rapy-wojny-gildii", "Rapy.gg - Wojny Gildii"),
      ("💎│rapy-boxpvp", "Rapy.gg - BoxPVP"),
  ]
  for kname, tkey in tryby:
    chan = discord.utils.get(
        kat_sklep.text_channels, name=kname
    ) or await guild.create_text_channel(kname, category=kat_sklep)
    await chan.edit(overwrites=overwrites_tylko_zweryfikowany)
    async for m in chan.history(limit=5):
      if m.author == bot.user:
        try:
          await m.delete()
        except discord.NotFound:
          pass
    await chan.send(
        embed=stworz_embed_cennika(tkey, cennik_dane.get(tkey, [])),
        view=CennikView(tkey),
    )

  # 3. Skup waluty
  kat_skup = await stworz_kategorie_bezpieczna("💰 ── SKUP EMERALD", 3)
  c_sprzedaj = discord.utils.get(
      kat_skup.text_channels, name="💎│sprzedaj-itemy"
  ) or await guild.create_text_channel(
      name="💎│sprzedaj-itemy", category=kat_skup
  )
  await c_sprzedaj.edit(overwrites=overwrites_tylko_zweryfikowany)
  async for m in c_sprzedaj.history(limit=5):
    if m.author == bot.user:
      try:
        await m.delete()
      except discord.NotFound:
        pass
  await c_sprzedaj.send(embed=stworz_embed_sprzedaj_itemy())

  skup_tryby = [
      ("📥│skup-anarchia-lifesteal", "Anarchia.gg - Lifesteal"),
      ("📥│skup-anarchia-boxpvp", "Anarchia.gg - BoxPVP"),
      ("📥│skup-minestar-skypvp", "Minestar.gg - SkyPvP"),
      ("📥│skup-minestar-lifesteal", "Minestar.gg - Lifesteal"),
      ("📥│skup-rapy-earthsmp", "Rapy.gg - EarthSMP"),
      ("📥│skup-rapy-wojny-gildii", "Rapy.gg - Wojny Gildii"),
      ("📥│skup-rapy-boxpvp", "Rapy.gg - BoxPVP"),
  ]
  for kname, tkey in skup_tryby:
    chan = discord.utils.get(
        kat_skup.text_channels, name=kname
    ) or await guild.create_text_channel(kname, category=kat_skup)
    await chan.edit(overwrites=overwrites_tylko_zweryfikowany)
    async for m in chan.history(limit=5):
      if m.author == bot.user:
        try:
          await m.delete()
        except discord.NotFound:
          pass
    await chan.send(
        embed=stworz_embed_skupu(tkey, skup_dane.get(tkey, [])),
        view=SkupView(tkey),
    )

  # 4. 🛡️ — EMERALD LEGIT (tylko 3 kanały, bez stworz-ticket)
  kat_legit = await stworz_kategorie_bezpieczna("🛡️ — EMERALD LEGIT", 4)

  overwrites_legit = {
      guild.default_role: discord.PermissionOverwrite(
          read_messages=False, view_channel=False, send_messages=False
      ),
      guild.me: discord.PermissionOverwrite(
          read_messages=True,
          view_channel=True,
          send_messages=True,
          add_reactions=True,
      ),
  }
  if zweryfikowany_role:
    overwrites_legit[zweryfikowany_role] = discord.PermissionOverwrite(
        read_messages=True,
        view_channel=True,
        send_messages=True,
        add_reactions=True,
    )

  lc_nr = stats_dane.get("legitchecki_licznik", 0)
  c_legit = None
  for ch in kat_legit.text_channels:
    if "legit-check" in ch.name.lower():
      c_legit = ch
      break
  if not c_legit:
    c_legit = await guild.create_text_channel(
        name=f"🛡️│legit-check-{lc_nr}", category=kat_legit
    )
  await c_legit.edit(overwrites=overwrites_legit)

  c_czy_legit = discord.utils.get(
      kat_legit.text_channels, name="🧐│czy-jesteśmy-legit"
  ) or await guild.create_text_channel(
      name="🧐│czy-jesteśmy-legit", category=kat_legit
  )
  await c_czy_legit.edit(overwrites=overwrites_legit)
  ma_ankiete = False
  async for m in c_czy_legit.history(limit=10):
    if m.author == bot.user and m.embeds:
      ma_ankiete = True
      await dodaj_reakcje_czy_legit(m)
      break
  if not ma_ankiete:
    msg_czy = await c_czy_legit.send(embed=stworz_embed_czy_jestesmy_legit())
    await dodaj_reakcje_czy_legit(msg_czy)

  c_stats = discord.utils.get(
      kat_legit.text_channels, name="📊│dzienne-statystyki"
  ) or await guild.create_text_channel(
      name="📊│dzienne-statystyki", category=kat_legit
  )
  await c_stats.edit(overwrites=overwrites_tylko_zweryfikowany)
  msg_stats = await pobierz_lub_utworz_wiadomosc_statystyk(c_stats)
  await msg_stats.edit(embed=stworz_embed_statystyk(archiwum=False))

  # 5. Tickety
  overwrites_tickety = {
      guild.default_role: discord.PermissionOverwrite(
          read_messages=False, view_channel=False
      ),
      guild.me: discord.PermissionOverwrite(
          read_messages=True,
          view_channel=True,
          send_messages=True,
          manage_channels=True,
      ),
  }
  if zweryfikowany_role:
    overwrites_tickety[zweryfikowany_role] = discord.PermissionOverwrite(
        read_messages=False, view_channel=False
    )
  for rid in ADMIN_ROLE_IDS:
    r = guild.get_role(rid)
    if r:
      overwrites_tickety[r] = discord.PermissionOverwrite(
          read_messages=True, view_channel=True, send_messages=True
      )
  lr = guild.get_role(LIDER_ROLE_ID)
  if lr:
    overwrites_tickety[lr] = discord.PermissionOverwrite(
        read_messages=True, view_channel=True, send_messages=True
    )

  kat_tickety = discord.utils.get(
      guild.categories, name="🎟️ ── TICKETY"
  ) or await guild.create_category(
      "🎟️ ── TICKETY", overwrites=overwrites_tickety, position=5
  )
  await kat_tickety.edit(overwrites=overwrites_tickety)

  # 6. Konkursy
  kat_konkursy = await stworz_kategorie_bezpieczna("🎉 ── KONKURSY", 6)
  c_konkursy = discord.utils.get(
      kat_konkursy.text_channels, name="🎉│konkursy"
  ) or await guild.create_text_channel(
      name="🎉│konkursy", category=kat_konkursy
  )
  await c_konkursy.edit(overwrites=overwrites_tylko_zweryfikowany)

  # 7. Współpraca
  kat_wspolpraca = await stworz_kategorie_bezpieczna("🤝 ── WSPÓŁPRACA", 7)
  overwrites_chat = {
      guild.default_role: discord.PermissionOverwrite(
          read_messages=False, view_channel=False
      ),
      guild.me: discord.PermissionOverwrite(
          read_messages=True, view_channel=True, send_messages=True
      ),
  }
  if zweryfikowany_role:
    overwrites_chat[zweryfikowany_role] = discord.PermissionOverwrite(
        read_messages=True, view_channel=True, send_messages=True
    )

  c_chat = discord.utils.get(
      kat_wspolpraca.text_channels, name="💬│chat"
  ) or await guild.create_text_channel(name="💬│chat", category=kat_wspolpraca)
  await c_chat.edit(overwrites=overwrites_chat)

  reg_chan = discord.utils.get(
      kat_wspolpraca.text_channels, name="📜│regulamin"
  ) or await guild.create_text_channel(
      name="📜│regulamin", category=kat_wspolpraca
  )
  await reg_chan.edit(overwrites=overwrites_tylko_zweryfikowany)
  async for m in reg_chan.history(limit=5):
    if m.author == bot.user:
      try:
        await m.delete()
      except discord.NotFound:
        pass
  embed_reg = discord.Embed(
      title="📜 ── **EMERALD SHOP ✕ REGULAMIN** ── 📜",
      color=discord.Color.from_rgb(46, 204, 113),
  )
  embed_reg.add_field(
      name="📌 Podstawowe zasady serwera",
      value=(
          "1. Szanuj każdego użytkownika oraz kadrę.\n2. Zakaz reklamowania"
          " innych serwerów i sklepów.\n3. Przestrzegaj poleceń"
          " administracji.\n4. Transakcje przeprowadzaj wyłącznie na"
          " oficjalnych ticketach.\n5. Oszustwa i próby scamu kończą się"
          " permanentnym banem."
      ),
      inline=False,
  )
  embed_reg.set_footer(text="© 2026 Emerald Shop ✕ Regulamin")
  await reg_chan.send(embed=embed_reg)

  rec_chan = discord.utils.get(
      kat_wspolpraca.text_channels, name="📋│rekrutacja"
  ) or await guild.create_text_channel(
      name="📋│rekrutacja", category=kat_wspolpraca
  )
  await rec_chan.edit(overwrites=overwrites_tylko_zweryfikowany)
  async for m in rec_chan.history(limit=5):
    if m.author == bot.user:
      try:
        await m.delete()
      except discord.NotFound:
        pass
  embed_rec = discord.Embed(
      title="📋 ── **EMERALD SHOP ✕ REKRUTACJA** ── 📋",
      description=(
          "Chcesz zostać sprzedawcą na **EMERALD SHOP**?\nKliknij poniższy"
          " przycisk, aby otworzyć ticket rekrutacyjny."
      ),
      color=discord.Color.from_rgb(241, 196, 15),
  )
  embed_rec.set_footer(text="✨ System Rekrutacji ✨")
  await rec_chan.send(embed=embed_rec, view=RecruitSetupView())

  # 8. Głosowe
  kat_voice = await stworz_kategorie_bezpieczna("🔊 ── KANAŁY GŁOSOWE", 8)
  if len(kat_voice.voice_channels) < 2:
    v_c = await guild.create_voice_channel(
        name="🔊│Strefa Unlimited #1", category=kat_voice, user_limit=0
    )
    await v_c.edit(overwrites=overwrites_tylko_zweryfikowany)

  # 9. Kadra
  overwrites_kadra = {
      guild.default_role: discord.PermissionOverwrite(
          read_messages=False, view_channel=False
      ),
      guild.me: discord.PermissionOverwrite(
          read_messages=True, view_channel=True, send_messages=True
      ),
  }
  for rid in ADMIN_ROLE_IDS:
    r = guild.get_role(rid)
    if r:
      overwrites_kadra[r] = discord.PermissionOverwrite(
          read_messages=True, view_channel=True, send_messages=True
      )
  lr = guild.get_role(LIDER_ROLE_ID)
  if lr:
    overwrites_kadra[lr] = discord.PermissionOverwrite(
        read_messages=True, view_channel=True, send_messages=True
    )

  kat_kadra = discord.utils.get(
      guild.categories, name="🔒 ── KADRA"
  ) or await guild.create_category(
      "🔒 ── KADRA", overwrites=overwrites_kadra, position=9
  )
  await kat_kadra.edit(overwrites=overwrites_kadra)
  if not discord.utils.get(kat_kadra.text_channels, name="🛠│admin-chat"):
    c_adm = await guild.create_text_channel(
        name="🛠│admin-chat", category=kat_kadra, overwrites=overwrites_kadra
    )
    await c_adm.edit(overwrites=overwrites_kadra)


@bot.command(name="konkurs")
@commands.has_permissions(administrator=True)
async def konkurs(ctx, czas: str, wygrani: int, *, nagroda: str):
  try:
    await ctx.message.delete()
  except Exception:
    pass

  sekundy = parsuj_czas(czas)
  if not sekundy:
    await ctx.send(
        "⚠️ **Błędny format czasu!** Użyj np. `30s`, `10m`, `1h`, `2d`.",
        delete_after=8,
    )
    return
  if wygrani <= 0:
    await ctx.send(
        "⚠️ **Liczba zwycięzców musi być większa niż 0!**", delete_after=8
    )
    return

  baner_url = ctx.message.attachments[0].url if ctx.message.attachments else None
  koniec_dt = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
      seconds=sekundy
  )

  view = GiveawayView(
      nagroda=nagroda,
      liczba_zwyciezcow=wygrani,
      koniec_dt=koniec_dt,
      baner_url=baner_url,
  )
  embed = zbuduj_embed_konkursu_aktywnego(
      nagroda, wygrani, koniec_dt, view.uczestnicy, baner_url
  )
  msg = await ctx.send(embed=embed, view=view)
  asyncio.create_task(
      uruchom_odliczanie_konkursu(
          msg, sekundy, nagroda, wygrani, view, baner_url
      )
  )


@bot.command(name="reset_all")
@commands.has_permissions(administrator=True)
async def reset_all(ctx):
  try:
    await ctx.message.delete()
  except Exception:
    pass

  await zbuduj_strukture_serwera(
      ctx.guild, usun_istniejace=True, resetuj_statystyki=True
  )
  await zsynchronizuj_liczniki_i_statystyki(
      ctx.guild, aktualizuj_nazwe_lc=True
  )

  potwierdzenie = discord.utils.get(
      ctx.guild.text_channels, name="🛠│admin-chat"
  ) or discord.utils.get(ctx.guild.text_channels, name="💬│chat")
  if potwierdzenie:
    await potwierdzenie.send(
        "🔄 **Wykonano `!reset_all`:** odtworzono strukturę kanałów"
        " (`🛡️ — EMERALD LEGIT` bez `stworz-ticket`) i wyzerowano statystyki.",
        delete_after=12,
    )


@bot.command(name="setup_emerald")
@commands.has_permissions(administrator=True)
async def setup_emerald(ctx):
  try:
    await ctx.message.delete()
  except Exception:
    pass

  await zbuduj_strukture_serwera(
      ctx.guild, usun_istniejace=False, resetuj_statystyki=False
  )
  await zsynchronizuj_liczniki_i_statystyki(
      ctx.guild, aktualizuj_nazwe_lc=True
  )

  await ctx.send(
      "✨ **Zaktualizowano kategorię `🛡️ — EMERALD LEGIT`, reakcje na"
      " `🧐│czy-jesteśmy-legit` oraz trwały zapis statystyk i legitchecków!**",
      delete_after=10,
  )


if __name__ == "__main__":
  try:
    print(">>> Uruchamianie bota Emerald Shop...")
    bot.run(TOKEN)
  except Exception as e:
    print(f"\n[BŁĄD KRYTYCZNY]: {e}")
    traceback.print_exc()
    input("\nNaciśnij Enter, aby zamknąć okno...")