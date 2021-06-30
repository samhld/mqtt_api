import os
import random
import json
from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
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

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="./static"), name="static")

# base_api = "/api/v2"
base_flux = 'from(bucket: "mqtt")'\
            '   |> range(start: -10m)'

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

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
                '|> mean()'\
                '|> duplicate(column: "_stop", as: "_time")'\
                '|> keep(columns: ["_value", "_time"])'\
                '|> rename(columns: {_value: "mean_usage_user"})'

    df = query_api.query_data_frame(flux)

    return templates.TemplateResponse("endpoint.html", {"request": request, "data": df.to_html(), "device_id": device_id})

@app.get("/devices/{device_id}/cpu/last", response_class=HTMLResponse)
def read_last_cpu(request: Request, device_id: str):
    flux =     f'{base_flux}'\
                '|> filter(fn: (r) => r._measurement == "cpu")'\
               f'|> filter(fn: (r) => r.host == "{device_id}")'\
                '|> filter(fn: (r) => r.cpu == "cpu-total")'\
                '|> filter(fn: (r) => r._field == "usage_user")'\
                '|> last()'

    df = query_api.query_data_frame(flux)

    return templates.TemplateResponse("endpoint.html", {"request": request, "data": df.to_html(), "device_id": device_id})

@app.get("/devices/{device_id}/mem/average", response_class=HTMLResponse)
def read_last_cpu(request: Request, device_id: str):
    flux =     f'{base_flux}'\
                '|> filter(fn: (r) => r._measurement == "mem")'\
               f'|> filter(fn: (r) => r.host == "{device_id}")'\
                '|> filter(fn: (r) => r.cpu == "cpu-total")'\
                '|> filter(fn: (r) => r._field == "usage_user")'\
                '|> mean()'

    df = query_api.query_data_frame(flux)

    return templates.TemplateResponse("endpoint.html", {"request": request, "data": df.to_html(), "device_id": device_id})

@app.get("/devices/{device_id}/mem/last", response_class=HTMLResponse)
def read_last_cpu(request: Request, device_id):
    flux =     f'{base_flux}'\
                '|> filter(fn: (r) => r._measurement == "mem")'\
               f'|> filter(fn: (r) => r.host == "{device_id}")'\
                '|> filter(fn: (r) => r.cpu == "cpu-total")'\
                '|> filter(fn: (r) => r._field == "usage_user")'\
                '|> last()'

    df = query_api.query_data_frame(flux)

    return templates.TemplateResponse("endpoint.html", {"request": request, "data": df.to_html(), "device_id": device_id})

@app.post("/")
def handle_form_data(request: Request,
                     device_id: str=Form(...), 
                     metric: str=Form(...), 
                     function: str=Form(...)):

    if metric == "cpu":
        if function in ("mean", "average"):
            read_mean_cpu(device_id)
        elif function == "last":
            read_last_cpu(device_id)
    elif metric in ("mem", "memory"):
        if function in ("mean", "average"):
            read_mean_mem(device_id)
        elif function == "last":
            read_last_mem(device_id)
        else:
            return "Function not available"
    else:
        return "Metric not available"


@app.post("/devices/{device_id}/cpu")
def write_cpu(device_id, value, timestamp):
    point = Point("cpu").tag("host", f"{device_id}").field("usage_user", value)
    write_api.write(bucket="mqtt", record=point)
