import os
from fastapi import FastAPI
from influxdb_client import InfluxDBClient, Point

INFLUX_HOST = os.environ["INFLUX_HOST"]
INFLUX_TOKEN = os.environ["INFLUX_TOKEN"]
INFLUX_BUCKET = os.environ["INFLUX_BUCKET"]
INFLUX_ORG = os.environ["INFLUX_ORG"]
QUERIES_PATH = os.environ["FLUX_QUERIES_PATH"]

influx_client = InfluxDBClient(url=INFLUX_HOST, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = influx_client.write_api()
query_api = influx_client.query_api()

app = FastAPI()

# base_api = "/api/v2"
base_flux = 'from(bucket: "mqtt")'\
            '   |> range(start: -10m)'
 

'''
Endpoints below (and above the PUBLISH ones) are   
'''
@app.get("/devices/{device_id}/cpu/average") # device_id may also be 'client_id' in client
def read_mean_cpu(device_id):
    # with open(f"{QUERIES_PATH}/cpu_mean.flux", 'r') as file:
    #     flux = f'{file.read()}'
    flux =     f'{base_flux}'\
                '|> filter(fn: (r) => r._measurement == "cpu")'\
               f'|> filter(fn: (r) => r.host == "{device_id}")'\
                '|> filter(fn: (r) => r.cpu == "cpu-total")'\
                '|> filter(fn: (r) => r._field == "usage_user")'\
                '|> mean()'

    return query_api.query(flux)

@app.get("/devices/{device_id}/cpu/last")
def read_last_cpu(device_id):
    flux =     f'{base_flux}'\
                '|> filter(fn: (r) => r._measurement == "cpu")'\
               f'|> filter(fn: (r) => r.host == "{device_id}")'\
                '|> filter(fn: (r) => r.cpu == "cpu-total")'\
                '|> filter(fn: (r) => r._field == "usage_user")'\
                '|> last()'

    return query_api.query(flux)

@app.get("/devices/{device_id}/mem/average")
def read_last_cpu(device_id):
    flux =     f'{base_flux}'\
                '|> filter(fn: (r) => r._measurement == "mem")'\
               f'|> filter(fn: (r) => r.host == "{device_id}")'\
                '|> filter(fn: (r) => r.cpu == "cpu-total")'\
                '|> filter(fn: (r) => r._field == "usage_user")'\
                '|> mean()'

    return query_api.query(flux)

@app.get("/devices/{device_id}/mem/last")
def read_last_cpu(device_id):
    flux =     f'{base_flux}'\
                '|> filter(fn: (r) => r._measurement == "mem")'\
               f'|> filter(fn: (r) => r.host == "{device_id}")'\
                '|> filter(fn: (r) => r.cpu == "cpu-total")'\
                '|> filter(fn: (r) => r._field == "usage_user")'\
                '|> last()'

    return query_api.query(flux)