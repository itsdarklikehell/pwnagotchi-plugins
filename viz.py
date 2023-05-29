import logging
import json
import plotly
import plotly.graph_objects as go
import random
from functools import lru_cache
from math import pi, cos, sin
from pwnagotchi import plugins
from flask import render_template_string, abort, jsonify
from threading import Lock
from pwnagotchi.wifi import freq_to_channel


TEMPLATE = """
{% extends "base.html" %}

{% set active_page = "plugins" %}

{% block title %}
    Viz
{% endblock %}

{% block scripts %}
    {{ super() }}
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
{% endblock %}

{% block script %}
    $(document).ready(function(){
        var hasData = false;
        var ajaxDataRenderer = function(url, plot, options) {
        var ret = null;

        $.ajax({
            async: false,
            url: url,
            dataType:"json",
            success: function(data) {
                ret = JSON.parse(data);
            }
        });
        return ret;
        };

        function loadGraphData() {
            var layout = {
                title: 'Viz Map',
                hovermode: 'closest',
                showlegend: false,
                xaxis: {
                    title: {
                        text: 'Signal',
                    },
                },
                yaxis: {
                    title: {
                        text: 'Channel',
                    },
                    tickmode: 'linear',
                    tick0: 1,
                    dtick: 1
                }
            };
            var result = ajaxDataRenderer('/plugins/viz/update');
            if (Array.isArray(result) && Object.keys(result).length > 0) {
                if (hasData == false) {
                    $('#plot').text('');
                    Plotly.newPlot('plot', result, layout);
                    hasData = true;
                } else {
                    Plotly.animate('plot', {
                        data: result,
                        layout: layout
                    }, {
                    transition: {
                        duration: 1000,
                        easing: 'cubic-in-out'
                    },
                    frame: {
                        duration: 1000
                    }
                    })
                }
            }
        }
        loadGraphData();
        setInterval(loadGraphData, 5000);
    });
{% endblock %}

{% block content %}
    <div class="chart" id="plot">
        Waiting for data...
    </div>
{% endblock %}
"""


class Viz(plugins.Plugin):
    __author__ = '33197631+dadav@users.noreply.github.com'
    __version__ = "1.0.1"
    __license__ = "GPL3"
    __description__ = "This plugin visualizes the surrounding APs."
    __name__ = 'Viz'
    __help__ = """
    This plugin visualizes the surrounding APs.
    """
    __dependencies__ = {
        'pip': ['plotly', 'pandas', 'flask']
    }
    __defaults__ = {
        'enabled': False,
    }

    COLORS = ["aliceblue", "aqua", "aquamarine", "azure",
              "beige", "bisque", "black", "blanchedalmond", "blue",
              "blueviolet", "brown", "burlywood", "cadetblue",
              "chartreuse", "chocolate", "coral", "cornflowerblue",
              "cornsilk", "crimson", "cyan", "darkblue", "darkcyan",
              "darkgoldenrod", "darkgray", "darkgrey", "darkgreen",
              "darkkhaki", "darkmagenta", "darkolivegreen", "darkorange",
              "darkorchid", "darkred", "darksalmon", "darkseagreen",
              "darkslateblue", "darkslategray", "darkslategrey",
              "darkturquoise", "darkviolet", "deeppink", "deepskyblue",
              "dimgray", "dimgrey", "dodgerblue", "firebrick",
              "forestgreen", "fuchsia", "gainsboro",
              "gold", "goldenrod", "gray", "grey", "green",
              "greenyellow", "honeydew", "hotpink", "indianred", "indigo",
              "ivory", "khaki", "lavender", "lavenderblush", "lawngreen",
              "lemonchiffon", "lightblue", "lightcoral", "lightcyan",
              "lightgoldenrodyellow", "lightgray", "lightgrey",
              "lightgreen", "lightpink", "lightsalmon", "lightseagreen",
              "lightskyblue", "lightslategray", "lightslategrey",
              "lightsteelblue", "lightyellow", "lime", "limegreen",
              "linen", "magenta", "maroon", "mediumaquamarine",
              "mediumblue", "mediumorchid", "mediumpurple",
              "mediumseagreen", "mediumslateblue", "mediumspringgreen",
              "mediumturquoise", "mediumvioletred", "midnightblue",
              "mintcream", "mistyrose", "moccasin", "navy",
              "oldlace", "olive", "olivedrab", "orange", "orangered",
              "orchid", "palegoldenrod", "palegreen", "paleturquoise",
              "palevioletred", "papayawhip", "peachpuff", "peru", "pink",
              "plum", "powderblue", "purple", "red", "rosybrown",
              "royalblue", "rebeccapurple", "saddlebrown", "salmon",
              "sandybrown", "seagreen", "seashell", "sienna", "silver",
              "skyblue", "slateblue", "slategray", "slategrey", "snow",
              "springgreen", "steelblue", "tan", "teal", "thistle", "tomato",
              "turquoise", "violet", "wheat",
              "yellow", "yellowgreen"]
    COLOR_MEMORY = dict()

    def __init__(self):
        self.options = dict()
        self.data = None
        self.lock = Lock()

    def on_loaded(self):
        logging.info("[viz] plugin is loaded!")

    @staticmethod
    def lookup_color(node):
        random.seed(node)
        if node not in Viz.COLOR_MEMORY:
            Viz.COLOR_MEMORY[node] = random.choice(Viz.COLORS)
        return Viz.COLOR_MEMORY[node]

    @staticmethod
    def random_pos(name, x0, y0, r):
        random.seed(name)
        t = 2 * pi * random.random()
        x = r * cos(t)
        y = r * sin(t)
        return x + x0, y + y0

    @staticmethod
    @lru_cache(maxsize=13)
    def create_graph(data, channel=None):
        if not data:
            return '{}'

        data = json.loads(data)

        node_text = list()
        edge_x = list()
        edge_y = list()
        node_x = list()
        node_y = list()
        node_symbols = list()
        node_sizes = list()
        node_colors = list()

        for ap_data in data:
            name = ap_data['hostname'] or ap_data['vendor'] or ap_data['mac']
            color = Viz.lookup_color(name)
            # nodes
            x, y = abs(ap_data['rssi']), freq_to_channel(ap_data['frequency'])
            node_x.append(x)
            node_y.append(y)
            node_text.append(name)
            node_symbols.append('square')
            node_sizes.append(15 + len(ap_data['clients']) * 3)
            node_colors.append(color)

            for c in ap_data['clients']:
                # node
                cname = c['hostname'] or c['vendor'] or c['mac']
                xx, yy = Viz.random_pos(cname, x, y, 3)
                node_x.append(xx)
                node_y.append(yy)
                node_text.append(cname)
                node_symbols.append('circle')
                node_sizes.append(10)
                node_colors.append(color)

                # edge
                edge_x.append(x)
                edge_x.append(xx)
                edge_x.append(None)
                edge_y.append(y)
                edge_y.append(yy)
                edge_y.append(None)

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines')

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers',
            marker=dict(
                size=node_sizes,
                color=node_colors,
                symbol=node_symbols,
            ),
            hovertext=node_text,
            hoverinfo='text')

        channel_line = go.Scatter(
            mode='lines',
            line=dict(width=15, color='#ff0000'),
            x=[min(node_x) - 5, max(node_x) + 5],
            y=[channel, channel],
            opacity=0.25,
            hoverinfo='none',
        ) if channel else dict()

        return json.dumps((channel_line, edge_trace, node_trace),
                          cls=plotly.utils.PlotlyJSONEncoder)

    def on_unfiltered_ap_list(self, agent, data):
        with self.lock:
            data = sorted(data, key=lambda k: k['mac'])
            self.data = json.dumps(data)

    def on_channel_hop(self, agent, channel):
        with self.lock:
            self.channel = channel

    def on_webhook(self, path, request):
        if not path or path == "/":
            return render_template_string(TEMPLATE)

        if path == 'update':
            with self.lock:
                g = Viz.create_graph(self.data, self.channel)
                return jsonify(g)

        abort(404)
