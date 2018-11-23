from guizero import App, Text

app = App(title="Battery Monitor" layout="grid" )
batteryMessage      = Text(app, text="Battery Voltage" grid=[0,0])
temperatureMessage  = Text(app, text="Temperature" grid=[1,0])

app.display()

print("Connected to Pi") # Added to Github