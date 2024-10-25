#Importing Libraries
#import ctkSlidingPanel
import os.path
import customtkinter as ctk
from PIL import ImageTk, Image
import datetime as dt
import time
import requests
from libtado.api import Tado
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import sys
sys.path.insert(0, 'src/GUI')
import ctkSlidingPanel as ptk

#Setting screen dimensions
screen_width = 1920
screen_height = 1080

# Weather query details
units ='metric'
lat = '53.56404'
lon = '-2.89697'
# OpenWeatherAPI url
request_url = ('https://api.open-meteo.com/v1/forecast?latitude='+lat+'&longitude='+lon+
               '&current=temperature_2m,relative_humidity_2m,is_day,precipitation,weather_code,wind_speed_10m'
               '&daily=weather_code,temperature_2m_max&wind_speed_unit=mph&timeformat=unixtime')

class Google_Calender():
    def __init__(self):
        SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
        creds = None
        if os.path.exists('./Credentials/google_token.json'):
            creds = Credentials.from_authorized_user_file('./Credentials/google_token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    './Credentials/google_cred.json', SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open('./Credentials/google_token.json', 'w') as token:
                token.write(creds.to_json())
        try:
            self.service = build('calendar', 'v3', credentials=creds)
        except:
            print('Unable to connect to Google Calendar')


    def get_n_events(self, number):
        if self.service is not None:
            current_dt = dt.datetime.utcnow().isoformat() + 'Z'
            res = (
                self.service.events().list(
                    calendarId="primary",
                    timeMin=current_dt,
                    maxResults=number,
                    singleEvents=True,
                    orderBy="startTime",
                ).execute()
            )
            events = res.get('items', [])
            return events

class Radio_Slider(ctk.CTkFrame):
    def __init__(self, master, color, bg_color,x,y, width, height, min_height, min_value, max_value, border_width, font, text=''):
        super().__init__(master=master, bg_color=bg_color,fg_color=color)
        self.place(relx=x, rely=y, relwidth=width, relheight=height)
        self.update()
        self.max_height = ((self.winfo_reqheight())-(2*border_width))-min_height
        self.min_value = min_value
        self.max_value = max_value
        self.current_value = self.min_value
        self.background_frame = ctk.CTkFrame(self, fg_color=bg_color, bg_color=color, height=10)
        self.background_frame.pack(side='top',fill='both', padx=border_width, pady=border_width)
        self.text = text
        self.office_radio_slider_label = ctk.CTkLabel(self, font=font, text_color=bg_color)
        self.office_radio_slider_label.pack(side='top')

    def Update(self):
        if self.text == '':
            self.office_radio_slider_label.configure(text=self.current_value)
        else:
            self.office_radio_slider_label.configure(text=str(self.current_value)+ self.text)

        new_value = None
        try:
            new_value = self.remap(self.current_value, self.min_value, self.max_value, self.max_height, 0)
            new_value = self.max_height - new_value
        except:
            new_value = self.max_height
        self.background_frame.configure(height=new_value)

    def set_value(self, value):
        try:
            if value < self.min_value:
                value = self.min_value
            elif value > self.max_value:
                value = self.max_value
            self.current_value = value
        except:
            self.current_value = value

    def remap(self,value, cur_min, cur_max, new_max, new_min):
        ratio = (new_max-new_min)/(cur_max-cur_min)
        return (ratio * (value-cur_min)) + new_min
class ForecastCard(ctk.CTkFrame):
    def __init__(self, master, icon_id, temp):
        ctk.CTkFrame.__init__(self, master)
        self.configure(bg_color='black', fg_color='black')
        self.rowconfigure(0, weight=2)
        self.rowconfigure(1, weight=1)
        self.size = 80
        self.icon = ctk.CTkCanvas(self, width=self.size, height=int(self.size*0.8), background='black', bd=0, highlightthickness=0, relief='ridge')
        self.icon.grid(row=0, column=0)
        original = Image.open('../Mirror/WeatherIcons/' + icon_id + '.png').resize((self.size, int(self.size * 0.8)))
        self.image = ImageTk.PhotoImage(original)
        self.icon.create_image(0, 0, anchor='nw', image=self.image)
        self.sub_font = ctk.CTkFont(family='Moon 2.0 Regular', size=20)
        self.label = ctk.CTkLabel(self, text=str(temp), font=self.sub_font)
        self.label.grid(row=1,column=0,sticky='we')

    def update_card(self, icon_id, temp):
        original = Image.open('../Mirror/WeatherIcons/' + icon_id + '.png').resize((self.size, int(self.size * 0.8)))
        self.image = ImageTk.PhotoImage(original)
        self.icon.create_image(0, 0, anchor='nw', image=self.image)
        self.label.configure(text=str(temp))

class CalenderCard(ctk.CTkFrame):
    def __init__(self, master, title, location, time, border):
        ctk.CTkFrame.__init__(self, master, bg_color='black', fg_color='white')
        self.inner_frame = ctk.CTkFrame(self, bg_color='white', fg_color='black')
        self.inner_frame.pack(fill='both', padx=border, pady=border, ipady = border/2, ipadx = border/2)
        self.inner_frame.rowconfigure(0, weight=2)
        self.inner_frame.rowconfigure(1, weight=1)
        self.inner_frame.columnconfigure(0, weight=5)
        self.inner_frame.columnconfigure(1, weight=1, minsize=90)

        self.sub_font = ctk.CTkFont(family='Piboto Light', size=20)
        self.body_font = ctk.CTkFont(family='Piboto', size = 30)

        self.title_label = ctk.CTkLabel(self.inner_frame, text=title, font=self.body_font)
        self.location_label = ctk.CTkLabel(self.inner_frame, text=location, font=self.sub_font)
        self.time_label = ctk.CTkLabel(self.inner_frame, text=time, font=self.body_font)

        self.title_label.grid(row=0, column=0, sticky='e')
        self.location_label.grid(row=1, column=0, sticky='e')
        self.time_label.grid(row=0, column=1, sticky='w', rowspan=2)

class MirrorGUI(ctk.CTkFrame):

    def __init__(self, master):
        ctk.CTkFrame.__init__(self, master)
        self.configure(fg_color='black')

        #Fonts
        self.title_font = ctk.CTkFont(family='Piboto', size = 40)
        self.tera_font = ctk.CTkFont(family='Piboto', size =120)
        self.giga_font = ctk.CTkFont(family='Piboto', size =70)
        self.body_font = ctk.CTkFont(family='Piboto', size = 30)
        self.sub_font = ctk.CTkFont(family='Piboto Light', size = 20)
        self.weather_data = requests.get(request_url).json()

        #Google APi
        self.cal_api = Google_Calender()
        self.cal_api.get_n_events(5)

        self.weather_map = {
            '0': 'Clear Skies',
            '1': 'Mainly Clear',
            '2': 'Partly Cloudy',
            '3': 'Overcast',
            '45': 'Fog',
            '48': 'Rime Fog',
            '51': 'Light Drizzle',
            '53': 'Moderate Drizzle',
            '55': 'Severe Drizzle',
            '56': 'Light Freezing Drizzle',
            '57': 'Severe Freezing Drizzle',
            '61': 'Light Rain',
            '63': 'Moderate Rain',
            '65': 'Heavy Rain',
            '66': 'Light Freezing Rain',
            '67': 'Heavy Freezing Rain',
            '71': 'Light Snow',
            '73': 'Moderate Snow',
            '75': 'Heavy Snow',
            '77': 'Snow Grains',
            '80': 'Light Rain Shower',
            '81': 'Moderate Rain Shower',
            '82': 'Monsoon Difficulty',
            '85': 'Light Snow Shower',
            '86': 'Heavy Snow Shower',
            '95': 'Thunder Storm',
            '96': 'Severe Thunder Storm',
            '99': 'Calamity Level Thunder Storm'
        }

        #TADO API ----------------------------------
        self.tado_creds = {}
        if os.path.exists('./Credentials/tado_cred.txt'):
            with open('./Credentials/tado_cred.txt', 'r') as file:
                lines  = file.readline()
            lines = lines.split(':')
            for line in lines:
                key, value = line.split('-')
                self.tado_creds[key] = value
        else:
            print('No credentials present for TadoAPI')

        tado_api = Tado(self.tado_creds.get('username'), self.tado_creds.get('password'),
                        self.tado_creds.get('key'))

        try:
            self.bedroom_temp = (tado_api.get_zone_states()['zoneStates']['10']['setting']['temperature']['celsius'])
        except:
            self.bedroom_temp = 'N/A'

        try:
            self.office_temp = (tado_api.get_zone_states()['zoneStates']['13']['setting']['temperature']['celsius'])
        except:
            self.office_temp = 'N/A'
        self.system_time = time.localtime()

        # Setting the weather panel up, frame, labels, images ect.

        self.top_panel  = ptk.VerticalSlidePanel(self, 0, -0.2, 0.35, 0.3)
        self.top_panel.rowconfigure(0, weight=1)
        self.top_panel.columnconfigure(0, weight=1)
        self.time_label = ctk.CTkLabel(self.top_panel, font=self.tera_font, text=dt.datetime.now().strftime("%H:%M"),
                                                bg_color='black', fg_color='black').grid(row=0, column=0, sticky='nsew')

        self.right_panel = ptk.LateralSlidePanel(self, 0.7, 1, y=0.05, panel_height=0.4, invert=True)
        self.right_panel.columnconfigure(0, weight=2)
        self.right_panel.columnconfigure(1, weight=3)
        self.right_panel.rowconfigure(0, weight=1)
        self.right_panel.rowconfigure(1, weight=1)
        self.right_panel.rowconfigure(2, weight=1)

        self.weather_icon = ctk.CTkCanvas(self.right_panel, width=340, background='black', bd=0,
                                          highlightthickness=0, relief='ridge')
        self.weather_icon.grid(row=0, column=0, sticky='e')
        original = Image.open(
            '../Mirror/WeatherIcons/' + self.check_wmo(self.weather_data['current']['weather_code']) + '.png').resize(
            (340, int(340 * 0.8)))
        self.image = ImageTk.PhotoImage(original)
        self.weather_icon.create_image(0, 0, anchor='nw', image=self.image)

        self.weather_main_frame = ctk.CTkFrame(self.right_panel)
        self.weather_main_frame.configure(bg_color='black', fg_color='black')
        self.weather_main_frame.grid(row=0, column=1, sticky='w')
        self.weather_main_frame.rowconfigure(0, weight=1)
        self.weather_main_frame.rowconfigure(1, weight=4)
        self.main_location_label = ctk.CTkLabel(self.weather_main_frame, font=self.title_font, text='Ormskirk',
                                                bg_color='black', fg_color='black')
        self.main_location_label.grid(row=0, column=0)

        self.temperature_frame = ctk.CTkFrame(self.weather_main_frame)
        self.temperature_frame.grid(row=1, column=0, sticky='w')
        self.temperature_frame.configure(bg_color='black', fg_color='black')
        self.temperature_frame.columnconfigure(0, weight=5)
        self.temperature_frame.columnconfigure(1, weight=1)
        self.main_temp_label = ctk.CTkLabel(self.temperature_frame, font=self.giga_font,
                                            text=self.weather_data['current']['temperature_2m'], bg_color='black',
                                            fg_color='black')
        self.main_temp_label.grid(row=0, column=0, sticky='n')
        self.main_metric_label = ctk.CTkLabel(self.temperature_frame, font=self.body_font,
                                              text=self.weather_data['current_units']['temperature_2m'],
                                              bg_color='black', fg_color='black')
        self.main_metric_label.grid(row=0, column=1, sticky='n')

        self.weather_secondary_frame = (ctk.CTkFrame(self.right_panel))
        self.weather_secondary_frame.grid(row=1, column=0, columnspan=2, sticky='we')
        self.weather_secondary_frame.configure(bg_color='black', fg_color='black')
        self.weather_secondary_frame.columnconfigure(0, weight=1)
        self.weather_secondary_frame.columnconfigure(1, weight=1)
        self.weather_secondary_frame.columnconfigure(2, weight=1)
        self.description_label = ctk.CTkLabel(self.weather_secondary_frame, font=self.sub_font, text=self.weather_map[
            str(self.weather_data['current']['weather_code'])])
        self.description_label.grid(row=0, column=0, sticky='n')
        self.wind_speed_label = ctk.CTkLabel(self.weather_secondary_frame, font=self.sub_font, text='Wind Speed ' + str(
            self.weather_data['current']['wind_speed_10m']) + ' ' + self.weather_data['current_units'][
                                                                                                        'wind_speed_10m'])
        self.wind_speed_label.grid(row=0, column=1, sticky='n')
        self.humidity_label = ctk.CTkLabel(self.weather_secondary_frame, font=self.sub_font, text='Humidity ' + str(
            self.weather_data['current']['relative_humidity_2m']) + ' %')
        self.humidity_label.grid(row=0, column=2, sticky='n')

        self.weather_forecast_frame = (ctk.CTkFrame(self.right_panel))
        self.weather_forecast_frame.configure(bg_color='black', fg_color='black')
        self.weather_forecast_frame.grid(row=2, column=0, columnspan=2, sticky='we')
        for i in range(7):
            self.weather_forecast_frame.columnconfigure(i, weight=1)

        self.forecast_cards = []
        for day in range (7):
            self.forecast_cards.append(ForecastCard(self.weather_forecast_frame,
                                                    self.check_wmo(self.weather_data['daily']['weather_code'][day]),
                                                    str(self.weather_data['daily']['temperature_2m_max'][day]) +
                                                    self.weather_data['daily_units']['temperature_2m_max']))
            self.forecast_cards[day].grid(row=0,column=day,sticky='n')


        self.lower_panel = ptk.LateralSlidePanel(self, 0.7, 1, y=0.45, panel_height=0.5, invert=True)
        self.lower_panel.update()
        self.lower_panel.columnconfigure(0,weight=1, minsize=96)
        self.lower_panel.columnconfigure(1,weight=1, minsize=96)
        self.lower_panel.rowconfigure(0,weight=1,minsize=540)
        self.lower_panel.rowconfigure(1,weight=1,minsize=540)
        self.tado_frame = ctk.CTkFrame(self.lower_panel, bg_color='black', fg_color='black')
        self.tado_frame.grid(row=0, column=0, sticky='NSEW')
        self.tado_label = ctk.CTkLabel(self.tado_frame, text='Tado°', font=self.title_font).pack(side='top', pady=30)
        self.bedroom_radio_slider = Radio_Slider(self.tado_frame, min_value=5, max_value=25, color='white',
                                                             bg_color='black',
                                                             x=0.0625,
                                                             y=0.2,
                                                             width=0.375,
                                                             height=0.45,
                                                             min_height=0,
                                                             border_width=4,
                                                             font=self.sub_font,
                                                             text='°C')
        self.office_radio_slider = Radio_Slider(self.tado_frame, min_value=5, max_value=25, color='white',
                                                             bg_color='black',
                                                             x=0.5625,
                                                             y=0.2,
                                                             width=0.375,
                                                             height=0.45,
                                                             min_height=0,
                                                             border_width=4,
                                                             font=self.sub_font,
                                                             text='°C')


        self.calender_frame = ctk.CTkFrame(self.lower_panel, bg_color='black',fg_color='black')
        self.calender_frame.grid(row=0, column=1, sticky='NSEW')

        self.update_calendar_info()
        self.update_calendar_frame()

        self.office_radio_slider.set_value(self.office_temp)
        self.bedroom_radio_slider.set_value(self.bedroom_temp)

        self.office_radio_slider.Update()
        self.bedroom_radio_slider.Update()


    def update_weather(self):
        self.weather_data = requests.get(request_url).json()

        original = Image.open(
            '../Mirror/WeatherIcons/' + self.check_wmo(self.weather_data['current']['weather_code']) + '.png').resize(
            (340, int(340 * 0.8)))
        self.image = ImageTk.PhotoImage(original)
        self.weather_icon.create_image(0, 0, anchor='nw', image=self.image)

        self.main_temp_label.configure(text=self.weather_data['current']['temperature_2m'])
        self.main_metric_label.configure(text=self.weather_data['current_units']['temperature_2m'])

        self.description_label.configure(text=self.weather_map[str(self.weather_data['current']['weather_code'])])
        self.wind_speed_label.configure(text='Wind Speed ' + str(self.weather_data['current']['wind_speed_10m']) + ' ' + self.weather_data['current_units']['wind_speed_10m'])
        self.humidity_label.configure(text='Humidity ' + str(self.weather_data['current']['relative_humidity_2m']) + ' %')

        count = 0
        for card in self.forecast_cards:
            card.update_card(self.check_wmo(self.weather_data['daily']['weather_code'][count]),
                                                    str(self.weather_data['daily']['temperature_2m_max'][count]) +
                                                    self.weather_data['daily_units']['temperature_2m_max'])
            count = count+1

    def update_calendar_info(self):
        self.events = self.cal_api.get_n_events(5)
    def update_calendar_frame(self):
        date_label = ctk.CTkLabel(self.calender_frame, text=str(dt.date.today()), font=self.title_font,
                                       anchor='center')
        date_label.pack(side='top', pady=30)
        if not self.events:
            label = ctk.CTkLabel(self.calender_frame, text='No events').pack(side='top')
            return
        for event in self.events:
            datetime = event['start'].get('dateTime', event['start'].get('date'))
            datetime = datetime.split('T')
            date = datetime[0].split('-')
            if len(datetime) == 1:
                CalenderCard(self.calender_frame,
                             event['summary'],
                             date[2] + '-' + date[1] + '-' + date[0],
                             ' | ', 4
                             ).pack(side='top', fill='x', pady=2)
            else:
                time = datetime[1].split(':')
                CalenderCard(self.calender_frame,
                             event['summary'],
                             date[2] + '-' + date[1] + '-' + date[0],
                             ' | ' +time[0] + ':' + time[1],4
                             ).pack(side='top', fill='x', pady=2)

    def clear_frame(self, frame):
        for widgets in frame.winfo_children():
            widgets.destroy()


    def animate(self):
        self.update_weather()

        self.top_panel.animate()
        self.right_panel.animate()
        self.lower_panel.animate()

        self.ping_tado_system()
        self.office_radio_slider.set_value(self.office_temp)
        self.office_radio_slider.Update()
        self.bedroom_radio_slider.set_value(self.bedroom_temp)
        self.bedroom_radio_slider.Update()

        self.update_calendar_info()
        self.clear_frame(self.calender_frame)
        self.update_calendar_frame()

    def check_wmo(self, code):
        if (code > 2):
            return str(code)
        else:
            if (self.system_time.tm_hour >= 5 and self.system_time.tm_hour <=18 ):
                return str(code) + 'd'
            else:
                return str(code) + 'n'

    def ping_tado_system(self):
        tado_api = Tado(self.tado_creds.get('username'), self.tado_creds.get('password'),
                        self.tado_creds.get('key'))
        self.bedroom_temp = tado_api.get_zone_states()['zoneStates']['10']['setting']['temperature']['celsius']


