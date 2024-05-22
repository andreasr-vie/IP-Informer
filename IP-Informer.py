from flask import Flask, request, render_template_string
import ipaddress

app = Flask(__name__)

def convert_mask_to_cidr(ip, mask):
    """
    Convert an IP address and subnet mask to CIDR notation.
    """
    ip = ipaddress.ip_address(ip)
    mask = ipaddress.ip_network(f'0.0.0.0/{mask}').prefixlen
    return f'{ip}/{mask}'

@app.route('/', methods=['GET', 'POST'])
def index():
    network_info = None
    error_message = None
    if request.method == 'POST':
        ip = request.form['ip']
        subnet = request.form['subnet']
        try:
            if '/' in ip:
                # CIDR notation
                network = ipaddress.ip_network(ip, strict=False)
            else:
                # Decimal notation
                cidr_notation = convert_mask_to_cidr(ip, subnet)
                network = ipaddress.ip_network(cidr_notation, strict=False)

            usable_ips = list(network.hosts())
            first_usable_ip = usable_ips[0] if usable_ips else 'N/A'
            last_usable_ip = usable_ips[-1] if usable_ips else 'N/A'
            num_usable_ips = len(usable_ips)

            network_info = {
                'network_address': str(network.network_address),
                'netmask': str(network.netmask),
                'first_usable_ip': str(first_usable_ip),
                'last_usable_ip': str(last_usable_ip),
                'num_usable_ips': num_usable_ips
            }
        except ValueError:
            error_message = 'Invalid IP address or subnet mask'
    
    return render_template_string('''
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
            <title>IP Address Calculator</title>
        </head>
        <body>
            <div class="container mt-5">
                <h1 class="mb-4">IP Address Calculator</h1>
                <form method="post">
                    <div class="form-group">
                        <label for="ip">Enter IP address:</label>
                        <input type="text" class="form-control" id="ip" name="ip" placeholder="e.g., 192.168.1.0 or 192.168.1.0/24">
                    </div>
                    <div class="form-group">
                        <label for="subnet">Enter Subnet Mask (optional if CIDR is used):</label>
                        <input type="text" class="form-control" id="subnet" name="subnet" placeholder="e.g., 255.255.255.0">
                    </div>
                    <button type="submit" class="btn btn-primary">Calculate</button>
                </form>
                {% if error_message %}
                    <div class="alert alert-danger mt-4">{{ error_message }}</div>
                {% endif %}
                {% if network_info %}
                    <div class="card mt-4">
                        <div class="card-body">
                            <h5 class="card-title">Network Details</h5>
                            <p class="card-text"><strong>Network Address:</strong> {{ network_info.network_address }}</p>
                            <p class="card-text"><strong>Subnet Mask:</strong> {{ network_info.netmask }}</p>
                            <p class="card-text"><strong>First Usable IP Address:</strong> {{ network_info.first_usable_ip }}</p>
                            <p class="card-text"><strong>Last Usable IP Address:</strong> {{ network_info.last_usable_ip }}</p>
                            <p class="card-text"><strong>Number of Usable IP Addresses:</strong> {{ network_info.num_usable_ips }}</p>
                        </div>
                    </div>
                {% endif %}
            </div>
            <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.4/dist/umd/popper.min.js"></script>
            <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
        </body>
        </html>
    ''', network_info=network_info, error_message=error_message)

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=5002)
