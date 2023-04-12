from aiohttp import web
import geopandas
import branca
from branca.element import Template, MacroElement
import pandas as pd
import folium
from folium.plugins import Search
from folium.plugins import FastMarkerCluster
from PIL import ImageColor


class FoliumMap:
    # Name states to regions.
    okrugsShort = {
        'УФО': 'Уральский',
        'СЗФО': 'Северо-Западный',
        'ПФО': 'Приволжский',
        'ЮФО': 'Южный',
        'СКФО': 'Северо-Кавказский',
        'ЦФО': 'Центральный',
        'ДФО': 'Дальневосточный',
        'СФО': 'Сибирский'
    }
    # Name cities to states.
    citiesFO = {
        'Карачаево-Черкесия': 'СКФО',
        'Карелия': 'СЗФО',
        'Кемеровская область': 'СФО',
        'Хабаровский край': 'ДФО',
        'Хакасия': 'СФО',
        'Ханты-Мансийский АО — Югра': 'УФО',
        'Адыгея': 'ЮФО',
        'Алтайский край': 'СФО',
        'Амурская область': 'ДФО',
        'Архангельская область': 'СЗФО',
        'Астраханская область': 'ЮФО',
        'Башкортостан': 'ПФО',
        'Белгородская область': 'ЦФО',
        'Брянская область': 'ЦФО',
        'Бурятия': 'СФО',
        'Чечня': 'СКФО',
        'Челябинская область': 'УФО',
        'Чувашия': 'ПФО',
        'Санкт-Петербург': 'СЗФО',
        'Дагестан': 'СКФО',
        'Алтай': 'СФО',
        'Ингушетия': 'СКФО',
        'Ивановская область': 'ЦФО',
        'Кабардино-Балкария': 'СКФО',
        'Калининградская область': 'СЗФО',
        'Калмыкия': 'ЮФО',
        'Калужская область': 'ЦФО',
        'Кировская область': 'ПФО',
        'Коми': 'СЗФО',
        'Костромская область': 'ЦФО',
        'Краснодарский край': 'ЮФО',
        'Курганская область': 'УФО',
        'Курская область': 'ЦФО',
        'Ленинградская область': 'СЗФО',
        'Липецкая область': 'ЦФО',
        'Магаданская область': 'ДФО',
        'Марий Эл': 'ПФО',
        'Мордовия': 'ПФО',
        'Московская область': 'ЦФО',
        'Мурманская область': 'СЗФО',
        'Ненецкий АО': 'СЗФО',
        'Нижегородская область': 'ПФО',
        'Северная Осетия — Алания': 'СКФО',
        'Новгородская область': 'СЗФО',
        'Новосибирская область': 'СФО',
        'Омская область 	Flag of Omsk Oblast.svg': 'СФО',
        'Орловская область': 'ЦФО',
        'Оренбургская область': 'ПФО',
        'Пензенская область': 'ПФО',
        'Приморский край': 'ДФО',
        'Псковская область': 'СЗФО',
        'Ростовская область': 'ЮФО',
        'Рязанская область': 'ЦФО',
        'Саха (Якутия)': 'ДФО',
        'Сахалинская область': 'ДФО',
        'Самарская область': 'ПФО',
        'Саратовская область': 'ПФО',
        'Смоленская область': 'ЦФО',
        'Ставропольский край': 'СКФО',
        'Свердловская область': 'УФО',
        'Тамбовская область': 'ЦФО',
        'Татарстан': 'ПФО',
        'Томская область': 'СФО',
        'Тульская область': 'ЦФО',
        'Тыва (Тува)': 'СФО',
        'Тверская область': 'ЦФО',
        'Тюменская область': 'СФО',
        'Удмуртия': 'ПФО',
        'Ульяновская область': 'ПФО',
        'Владимирская область': 'ЦФО',
        'Волгоградская область': 'ЮФО',
        'Вологодская область': 'СЗФО',
        'Воронежская область': 'ЦФО',
        'Ямало-Ненецкий АО': 'УФО',
        'Ярославская область': 'ЦФО',
        'Еврейская АО': 'ДФО',
        'Крым': 'ЮФО',
        'Севастополь': 'ЮФО',
        'Красноярский край': 'СФО',
        'Забайкальский край': 'ДФО',
        'Иркутская область': 'СФО',
        'Пермский край': 'ПФО',
        'Камчатский край': 'ДФО',
        'Москва': 'ЦФО',
        'Чукотский АО': 'ДФО',
    }
    # Name states to colors.
    color = {
        'УФО': "#c8cc90",
        'СЗФО': "#62d3c6",
        'ПФО': "#ffff81",
        'ЮФО': "#fc8c8c",
        'СКФО': "#ab6ca8",
        'ЦФО': "#34cf00",
        'СФО': "#00bfe8",
        'ДФО': "#fecf28"
    }
    # Name states to color values
    colorData = {
         'УФО': 0.1,
         'СЗФО': 0.2,
         'ПФО': 0.3,
         'ЮФО': 0.4,
         'СКФО': 0.5,
         'ЦФО': 0.6,
         'СФО': 0.7,
         'ДФО': 0.9
    }
    managerColor = ['red', 'blue', 'green', 'purple', 'orange', 'darkred',
                    'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue',
                    'darkpurple', 'white', 'pink', 'lightblue', 'lightgreen',
                    'gray', 'black', 'lightgray']

    managerColorHTML = ['#d63c25', '#33a2d2', '#72b021', '#d150b8', '#f0942b', '#a13033',
                        '#ff8e7f', '#ffc98f', '#0064a0', '#72831f', '#3f6675',
                        '#583569', '#fbfbfb', '#fe8be9', '#86daff', '#bcf971',
                        '#565656', '#2c2c2c', '#a4a4a5']

    def __init__(self):
        # Use just two columns in df.
        self.states = geopandas.read_file("geojson/russian_regions_fix.geojson", driver="GeoJSON", )[['NL_NAME_1', 'geometry']]
        self.dilers = pd.read_csv('data/users.csv', sep=";")
        self.tasks = pd.read_csv('data/task.csv', sep=";")
        self.colormap = branca.colormap.LinearColormap(
            colors=["#5fb4b5", "#f99256", "#c695c6", "#fac963", "#669acd", "#9ac895", "#ed5f67", "#65747f"],
            index=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.9],
            vmin=0,
            vmax=1,
        )

    @staticmethod
    def bone(df, word, col1, col2):
        """
        Combine json and dict
        """
        df[col2] = ''
        for k, v in word.items():
            df.loc[df[col1] == k, col2] = v
        return df

    def style_function(self, x):
        """Color function"""
        return {
            "fillColor": self.colormap(x["properties"]["ColorData"]),
            "color": "black",
            "weight": 0.6,
            "fillOpacity": 0.3,
        }

    def create_map(self):
        # States short names.
        self.bone(self.states, self.citiesFO, "NL_NAME_1", "FO")
        # States full names.
        self.bone(self.states, self.okrugsShort, "FO", "FOfull")
        # States colors.
        self.bone(self.states, self.color, "FO", "Color")
        # States color values.
        self.bone(self.states, self.colorData, "FO", "ColorData")

        self.colormap.caption = "Цветовое выделение ФО"

        listManager = []
        for manager in self.dilers.manager.drop_duplicates(keep='first'):
            listManager += [manager]

        self.bone(self.dilers, dict(zip(listManager, self.managerColor)), 'manager', 'managerColor')
        self.tasks = self.tasks.dropna(subset=['lon', 'lat'])

        listType = []
        for taskType in self.tasks['type'].drop_duplicates(keep='first'):
            listType += [taskType]

        self.bone(self.tasks, dict(zip(listType, self.managerColor[3:])), 'type', 'typeColor')

        # Manager markers
        legendManager, legendTasks = "", ""

        for k, v in dict(zip(listManager, self.managerColorHTML)).items():
            legendManager += f"""
            <div class='legend-scale'>
                <ul class='legend-labels'>
                     <article class='fw6 flex flex-row items-center ph3 bg-white mb1'><svg aria-hidden='true' focusable='false' data-prefix='fas' data-icon='map-marker-alt' role='img' xmlns='http://www.w3.org/2000/svg' viewBox='0 0 384 512' class='svg-inline--fa fa-map-marker-alt fa-w-12 fa-fw fa-lg'><path fill={v} d='M172.268 501.67C26.97 291.031 0 269.413 0 192 0 85.961 85.961 0 192 0s192 85.961 192 192c0 77.413-26.97 99.031-172.268 309.67-9.535 13.774-29.93 13.773-39.464 0zM192 272c44.183 0 80-35.817 80-80s-35.817-80-80-80-80 35.817-80 80 35.817 80 80 80z' class=''></path></svg> <span class='ml3 bl bw1 b--lime7 pl3 pv3'>{k}</span></article>
                </ul>
            </div>"""

            # Type task markers
        legendTasks = ""

        for k, v in dict(zip(listType, self.managerColorHTML[3:])).items():
            legendTasks += f"""
            <div class='legend-scale'>
                <ul class='legend-labels'>
                     <article class='fw6 flex flex-row items-center ph3 bg-white mb1'><svg aria-hidden='true' focusable='false' data-prefix='fad' data-icon='circle' role='img' xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512' class='svg-inline--fa fa-circle fa-w-16 fa-fw fa-lg'><g class='fa-group'><path fill={v} d='M256 8C119 8 8 119 8 256s111 248 248 248 248-111 248-248S393 8 256 8zm0 424c-97.06 0-176-79-176-176S158.94 80 256 80s176 79 176 176-78.94 176-176 176z' class='fa-secondary'></path><path fill={v} fill-opacity='0.25' d='M256 432c-97.06 0-176-79-176-176S158.94 80 256 80s176 79 176 176-78.94 176-176 176z' class='fa-primary'></path></g></svg> <span class='ml3 bl bw1 b--pink7 pl3 pv3'>{k}</span></article>
                </ul>
            </div>"""

        template = """
        {% macro html(this, kwargs) %}

        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>jQuery UI Draggable - Default functionality</title>
          <link rel="stylesheet" href="//code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css">

          <script src="https://code.jquery.com/jquery-1.12.4.js"></script>
          <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.js"></script>

          <script>
          $( function() {
            $( "#maplegend" ).draggable({
                            start: function (event, ui) {
                                $(this).css({
                                    right: "auto",
                                    top: "auto",
                                    bottom: "auto"
                                });
                            }
                        });
        });

          </script>
        </head>
        <body>


        <div id='maplegend' class='maplegend' 
            style='position: absolute; z-index:9999; border:2px solid grey; background-color:rgba(255, 255, 255, 0.8);
             border-radius:6px; padding: 10px; font-size:14px; right: 20px; bottom: 20px;'>

        <div class='legend-title'>Маркеры</div>
        """ + legendTasks + legendManager + """
        </div>

        </body>
        </html>

        <style type='text/css'>
          .maplegend .legend-title {
            text-align: left;
            margin-bottom: 5px;
            font-weight: bold;
            font-size: 100%;
            }
          .maplegend .legend-scale ul {
            margin: 0;
            margin-bottom: 5px;
            padding: 0;
            float: left;
            list-style: none;
            }
          .maplegend .legend-scale ul li {
            font-size: 80%;
            list-style: none;
            margin-left: 0;
            line-height: 18px;
            margin-bottom: 2px;
            }
          .maplegend ul.legend-labels li span {
            display: block;
            float: left;
            height: 16px;
            width: 30px;
            margin-right: 5px;
            margin-left: 0;
            border: 1px solid #999;
            }
          .maplegend .legend-source {
            font-size: 80%;
            color: #777;
            clear: both;
            }
          .maplegend a {
            color: #777;
            }
        </style>
        {% endmacro %}"""

        macro = MacroElement()
        macro._template = Template(template)

        icon_create_function = """
            function(cluster) {
            var childCount = cluster.getChildCount(); 

            return new L.DivIcon({ html: '<div style="background-color:;color: rgba(0, 0, 0, 1);border: 4px outset \"><span style="position:relative;top:-3.5px">' + childCount + '</span></div>', className: 'marker-cluster marker-cluster-', iconSize: new L.Point(50, 50) }); 

            }
            """

        m = folium.Map(location=[73, 61], zoom_start=3, min_zoom=3.6, max_bounds=True, min_lat=40, max_lat=90,
                       min_lon=19, max_lon=187)

        # set up regions board on the map to show states.
        stategeo = folium.GeoJson(
            self.states,
            name="Регионы и ФО",
            style_function=self.style_function,
            tooltip=folium.GeoJsonTooltip(
                fields=["NL_NAME_1"], aliases=["Регион"], localize=True
            ),
        ).add_to(m)

        # add manager markers and layers to control it.
        for manager in listManager:
            feature_dilers = folium.FeatureGroup(name=manager)
            dfManager = self.dilers.loc[self.dilers.manager == manager].copy().reset_index()

            for i in range(len(dfManager)):
                folium.Marker(location=[dfManager.lat[i], dfManager.lon[i]],
                              icon=folium.Icon(color=dfManager.managerColor[i], icon_color='white', icon="circle",
                                               prefix='fa'),
                              popup=folium.Popup(
                                  f'<b>Имя дилера: </b>{dfManager.name_dil[i]}<br><br><b>Адрес: </b>{dfManager.adress[i]}',
                                  max_width=500),
                              tooltip=folium.Tooltip(dfManager.name_dil[i])).add_to(feature_dilers)

            m.add_child(feature_dilers)

        # add type task markers and layers to control it.
        cHTML = 3
        for taskType in listType:
            feature_tasks = folium.FeatureGroup(name=taskType)
            markerCluster = folium.plugins.MarkerCluster(icon_create_function=icon_create_function[:136] + 'rgba' + str(
                ImageColor.getcolor(self.managerColorHTML[cHTML], "RGB"))[:-1] + ', 0.7)' + icon_create_function[
                                                                                       136:180] + 'rgba' + str(
                ImageColor.getcolor(self.managerColorHTML[cHTML], "RGB"))[:-1] + ', 0.4)' + icon_create_function[
                                                                                       180:]).add_to(feature_tasks)
            cHTML += 1
            dfType = self.tasks.loc[self.tasks['type'] == taskType].copy().reset_index()

            for i in range(len(dfType)):
                folium.CircleMarker(location=[dfType.lat[i], dfType.lon[i]],
                                    color=dfType.typeColor[i],
                                    fill=True,
                                    popup=folium.Popup(
                                        f'<b>Статус: </b>{dfType.status[i]}<br><br><b>Имя участника: </b>{dfType.name_application[i]}<br><br><b>Адрес: </b>{dfType.adress_dirty[i][:60]}',
                                        max_width=300),
                                    tooltip=folium.Tooltip(f'{dfType.num[i]} {taskType}')).add_to(markerCluster)

            m.add_child(feature_tasks)

        # create search window with refions
        statesearch = Search(
            layer=stategeo,
            geom_type="Polygon",
            placeholder="Поиск по регионам",
            collapsed=False,
            search_label="NL_NAME_1",
            weight=3,
        ).add_to(m)

        # add legend
        m.get_root().add_child(macro)

        folium.LayerControl().add_to(m)

        return m


async def handle(request: web.Request) -> web.Response:
    folium_map = map
    folium_root = folium_map.get_root()
    folium_html = folium_root.render()
    return web.Response(text=folium_html, content_type="text/html")


map = FoliumMap().create_map()
app = web.Application()
app.add_routes([web.get('/', handle)])


if __name__ == '__main__':
    web.run_app(app)