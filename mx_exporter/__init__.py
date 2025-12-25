import sys
import os.path
import argparse
import signal
from http.server import HTTPServer
from prometheus_client import MetricsHandler
from prometheus_client import REGISTRY, GC_COLLECTOR, PLATFORM_COLLECTOR, PROCESS_COLLECTOR
from mx_exporter.mx_exporter import MxCollector


def check_port(value):
    port = int(value)
    if port < 0 or port > 65535:
        raise argparse.ArgumentTypeError("%s is an invalid port value" % value)
    return port


def check_interval(value):
    interval = int(value)
    if interval < 100:
        raise argparse.ArgumentTypeError("%s is invalid, interval must be larger than 100ms" % value)
    return interval


def check_path(value):
    if not os.path.exists(value):
        raise argparse.ArgumentTypeError("%s is an invalid path" % value)
    return value


def get_default_config_file():
    default_config_files = [
        "/opt/maca/etc/default-counters.csv",
        "/opt/mxn100/etc/default-counters.csv",
        os.getcwd() + "/default-counters.csv",
        os.path.dirname(os.path.abspath(__file__)) + "/default-counters.csv",
    ]

    for default_file in default_config_files:
        if os.path.exists(default_file):
            print("Find default config file: %s" % default_file)
            return default_file

    return "" 


def signal_handler(signum, frame):
    print("Signal %d received." % signum)
    if signum == signal.SIGINT:
        sys.exit(0)
    else:
        print("Unexpected exit.")
        sys.exit(100 + signum)


class MxExporterHandler(MetricsHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            html_content = """<html>
<head><title>MetaX Exporter</title></head>
<body>
<h1>MetaX Exporter</h1>
<p><a href="./metrics">Metrics</a></p>
</body>
</html>"""
            self.wfile.write(html_content.encode("utf-8"))

        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

        else:
            # prometheus /metrics
            super().do_GET()


def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    parser = argparse.ArgumentParser(description="MetaX Data Exporter")
    parser.add_argument("-p", "--port", type=check_port, default=8000, help="HTTP listen port")
    parser.add_argument("-i", "--interval", type=check_interval, default=10000, help="Metrics gathering interval, unit:ms")
    parser.add_argument("-c", "--config-file", type=check_path, help="Path to metrics config file")
    parser.add_argument("-m", "--mode", type=int, choices=[0,1], default=1, help="Deprecated, keep for back compatibility")
    parser.add_argument("-lm", "--log-monitor", type=int, choices=[0,1], default=1, help="Deprecated, keep for back compatibility")
    parser.add_argument("-im", "--ib-monitor", type=int, choices=[0,1], default=0, help=argparse.SUPPRESS) # help="0/1 - Disable/Enable IB NIC counter monitoring"
    parser.add_argument("-mp", "--mount-point", type=check_path, default="/", help="Container mount point")

    args = parser.parse_args()
    print(args)

    cfg_file = ""
    if args.config_file is not None:
        cfg_file = args.config_file
    else:
        cfg_file = get_default_config_file()

    print("Config file: %s" % cfg_file)
    if cfg_file == "":
        return

    # disable the default metrics
    REGISTRY.unregister(GC_COLLECTOR)
    REGISTRY.unregister(PLATFORM_COLLECTOR)
    REGISTRY.unregister(PROCESS_COLLECTOR)

    registry = REGISTRY

    mx_collector = MxCollector(cfg_file, registry, args.interval/1000, args.ib_monitor, args.mount_point)

    server_address = ('', args.port)
    try:
        httpd = HTTPServer(server_address, MxExporterHandler)
        httpd.serve_forever()
    except OSError:
        print("Invalid HTTP listen port: '{}' already in use(Please use -p/--port to specify a valid port)".format(args.port))
        exit(-1)
