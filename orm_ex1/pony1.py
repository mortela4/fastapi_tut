from pony.orm import Database, PrimaryKey, Required, Optional, Set, db_session

db = Database()
db.bind('sqlite', ':memory:')   # In-memory SQLite DB only --> for testing ...

# Model:

class Sensor(db.Entity):
    partno = Required(str)
    bus_type = Required(str)    # one of "I2C", "SPI" or "UART"
    unit_name = Optional(str)
    hubs_where_used = Set("SensorHub")

class SensorHub(db.Entity):
    ser_no = PrimaryKey(int)
    name = Required(str)
    bus_id = Optional(str)
    sensors = Set(Sensor)

# Create database tables:
db.generate_mapping(create_tables=True)


# Create sensor entities:
@db_session
def create_entities():
    bma380 = Sensor(partno="BMA280", bus_type="SPI", unit_name="RhT")
    adxl255 = Sensor(partno="ADXL255", bus_type="UART", unit_name="G")
    fxs3008 = Sensor(partno="FXS3008", bus_type="I2C", unit_name="Bar")
    # Then sensor-hub entities ...
    SensorHub(ser_no=123, name="TestHub1", bus_id="SPI_0.3 UART0, I2C1.0x48", sensors=(bma380, adxl255, fxs3008))
    SensorHub(ser_no=223, name="TestHub2", bus_id="SPI_0.1 UART3, I2C1.0x56", sensors=(bma380, adxl255, fxs3008))
    SensorHub(ser_no=323, name="TestHub3", bus_id="SPI_3.0 UART1, I2C1.0x71", sensors=(bma380, adxl255, fxs3008))

create_entities()
db.commit()     # Redundant, done at exit from 'create_etities()' func)

# Retrieve from DB:
@db_session
def retrieve_entities():
    peticular_hub = SensorHub[123]                              # Retrieve single entity
    print(f"Name of the peticular hub: {peticular_hub.name}")

    hubs = SensorHub.select(lambda hub: hub.ser_no > 200)       # Retrieve multiple entitities
    print("All hubs with serial no. over 200:")
    for hub in hubs:
        print(f"{hub.name}")


if __name__ == "__main__":
    retrieve_entities()
    # Finalize
    db.disconnect()











