import os
import random
import json
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from influxdb_client import InfluxDBClient, Point

templates = Jinja2Templates(directory="templates")

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
@app.get("/devices/{device_id}/cpu/average", response_class=HTMLResponse) # device_id may also be 'client_id' in client
def read_mean_cpu(request: Request, device_id):
    # with open(f"{QUERIES_PATH}/cpu_mean.flux", 'r') as file:
    #     flux = f'{file.read()}'
    flux =     f'{base_flux}'\
                '|> filter(fn: (r) => r._measurement == "cpu")'\
               f'|> filter(fn: (r) => r.host == "{device_id}")'\
                '|> filter(fn: (r) => r.cpu == "cpu-total")'\
                '|> filter(fn: (r) => r._field == "usage_user")'\
                '|> mean()'

    # tables = query_api.query(flux)
    # data = []
    # for table in tables:
    #     rows = []
    #     for row in table.records:
    #         rows.append(row.values)
    #     data.append(rows)
    df = query_api.query_data_frame(flux)
    # render_df = df.to_html()

    return templates.TemplateResponse("home.html", {"request": request, "data": df.to_html()})

@app.get("/devices/{device_id}/cpu/last", response_class=HTMLResponse)
def read_last_cpu(request: Request, device_id: str):
    flux =     f'{base_flux}'\
                '|> filter(fn: (r) => r._measurement == "cpu")'\
               f'|> filter(fn: (r) => r.host == "{device_id}")'\
                '|> filter(fn: (r) => r.cpu == "cpu-total")'\
                '|> filter(fn: (r) => r._field == "usage_user")'\
                '|> last()'

    df = query_api.query_dataframe(flux)

    return templates.TemplateResponse("home.html", {"request": request, "data": df.to_string()})

@app.get("/devices/{device_id}/mem/average", response_class=HTMLResponse)
def read_last_cpu(request: Request, device_id: str):
    flux =     f'{base_flux}'\
                '|> filter(fn: (r) => r._measurement == "mem")'\
               f'|> filter(fn: (r) => r.host == "{device_id}")'\
                '|> filter(fn: (r) => r.cpu == "cpu-total")'\
                '|> filter(fn: (r) => r._field == "usage_user")'\
                '|> mean()'

    data = query_api.query(flux)

    return templates.TemplateResponse("home.html", {"request": request, "data": data})

@app.get("/devices/{device_id}/mem/last", response_class=HTMLResponse)
def read_last_cpu(request: Request, device_id):
    flux =     f'{base_flux}'\
                '|> filter(fn: (r) => r._measurement == "mem")'\
               f'|> filter(fn: (r) => r.host == "{device_id}")'\
                '|> filter(fn: (r) => r.cpu == "cpu-total")'\
                '|> filter(fn: (r) => r._field == "usage_user")'\
                '|> last()'

    data = query_api.query(flux)

    return templates.TemplateResponse("home.html", {"request": request, "data": data})

@app.post("/devices/{device_id}/cpu")
def write_cpu(device_id, value, timestamp):
    point = Point("cpu").tag("host", f"{device_id}").field("usage_user", value)
    write_api.write(bucket="mqtt", record=point)
