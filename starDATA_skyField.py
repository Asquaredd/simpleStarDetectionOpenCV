from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PySide6.QtGui import QAction
from skyfield.api import load, Topos
from skyfield.data import hipparcos
from PIL import Image, ImageDraw
from functools import partial

# Define a dictionary of constellations and their major stars' HIP numbers
constellation_presets = {
    'Andromeda': 677,     # Alpheratz (Alpha Andromedae)
    'Aquarius': 106278,   # Sadalmelik (Alpha Aquarii)
    'Aries': 9884,        # Hamal (Alpha Arietis)
    'Cancer': 43103,      # Al Tarf (Beta Cancri)
    'Canis Major': 32349, # Sirius (Alpha Canis Majoris)
    'Capricornus': 107556,# Deneb Algedi (Delta Capricorni)
    'Cassiopeia': 3179,   # Schedar (Alpha Cassiopeiae)
    'Cygnus': 102098,     # Deneb (Alpha Cygni)
    'Gemini': 37826,      # Pollux (Beta Geminorum)
    'Leo': 49669,         # Regulus (Alpha Leonis)
    'Libra': 72622,       # Zubeneschamali (Beta Librae)
    'Lyra': 91262,        # Vega (Alpha Lyrae)
    'Orion': 26727,       # Betelgeuse (Alpha Orionis)
    'Pegasus': 113963,    # Enif (Epsilon Pegasi)
    'Pisces': 9487,       # Alpherg (Eta Piscium)
    'Sagittarius': 88635, # Kaus Australis (Epsilon Sagittarii)
    'Scorpius': 80763,    # Antares (Alpha Scorpii)
    'Taurus': 21421,      # Aldebaran (Alpha Tauri)
    'Ursa Major': 54061,
    'Ursa Minor': 11767, # Dubhe (Alpha Ursae Majoris)
    'Virgo': 65474,       # Spica (Alpha Virginis)
}


class StarFinder(QMainWindow):
    def __init__(self, stars):
        super().__init__()
        self.stars = stars
        self.initUI()
        self.initMenuBar()

    def initUI(self):
        # Create a central widget
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Set the layout for the central widget
        self.layout = QVBoxLayout(central_widget)

        # Rest of the UI elements like labels, buttons, etc.
        self.label = QLabel("Enter Star HIP Number:", self)
        self.layout.addWidget(self.label)

        self.starInput = QLineEdit(self)
        self.layout.addWidget(self.starInput)

        self.findButton = QPushButton("Find Star", self)
        self.findButton.clicked.connect(self.find_star)
        self.layout.addWidget(self.findButton)

        self.resultLabel = QLabel("", self)
        self.layout.addWidget(self.resultLabel)
        
        self.altAzLabel = QLabel("", self)
        self.layout.addWidget(self.altAzLabel)

        self.setLayout(self.layout)
        self.setWindowTitle("Star Finder")

    def initMenuBar(self):
        # Create the menu bar
        menu_bar = self.menuBar()

        # Create the 'Stars' menu
        stars_menu = menu_bar.addMenu('Stars')

        # Add presets to 'Stars' menu
        for constellation, hip_num in constellation_presets.items():
            action = QAction(constellation, self)
            # Use partial to correctly pass the hip_num to the load_star_by_hip method
            action.triggered.connect(partial(self.load_star_by_hip, hip_num))
            stars_menu.addAction(action)

    def find_star(self):
        star_hip_number = self.starInput.text()
        try:
            hip_number = int(star_hip_number)
            ra_dec_coordinates, alt_az_coordinates = self.get_star_coordinates(hip_number)
            self.resultLabel.setText(f"RA/DEC: {ra_dec_coordinates}")
            self.altAzLabel.setText(f"Alt/Az: {alt_az_coordinates}")
        except ValueError:
            self.resultLabel.setText("Invalid HIP number")
        except KeyError:
            self.resultLabel.setText("Star not found in catalog")

    def get_star_coordinates(self, hip_number):
        planets = load('de421.bsp')
        earth = planets['earth']

        # Load the star data from the catalog
        star_data = self.stars.loc[hip_number]

        # Create a Star object from the star data
        from skyfield.api import Star
        star = Star(ra_hours=star_data['ra_hours'], dec_degrees=star_data['dec_degrees'])

        # Observer's location (replace with actual latitude and longitude)
        observer = earth + Topos(latitude_degrees=34.0, longitude_degrees=-118.0)

        # Current time
        ts = load.timescale()
        t = ts.now()

        # Get the astrometric position of the star
        astrometric = observer.at(t).observe(star)
        alt, az, distance = astrometric.apparent().altaz()

        ra_dec_coordinates = f"RA: {star.ra.hours}, DEC: {star.dec.degrees}"
        alt_az_coordinates = f"Altitude: {alt.degrees:.2f}, Azimuth: {az.degrees:.2f}"
        return ra_dec_coordinates, alt_az_coordinates
    
    def load_star_by_hip(self, hip_number):
        self.starInput.setText(str(hip_number))
        self.find_star()



def load_star_catalog():
    try:
        with load.open(hipparcos.URL) as f:
            stars = hipparcos.load_dataframe(f)
        return stars
    except Exception as e:
        print(f"Failed to load star catalog: {e}")
        return None

if __name__ == '__main__':
    app = QApplication([])

    stars = load_star_catalog()
    if stars is not None:
        ex = StarFinder(stars)
        ex.show()
        app.exec()
    else:
        print("Unable to load the star catalog. Please check your internet connection and try again.")
