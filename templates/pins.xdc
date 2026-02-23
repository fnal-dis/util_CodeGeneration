# Single-ended signals

{% for port in spec.all_signals_singleended %}
{% set get_ports = "[get_ports " ~ port.name_io ~ "]"  %}
set_property PACKAGE_PIN {{ port['FPGA Pin'].ljust(7) }} {{ get_ports }}
{% if port['IO Standard'] != '' %}
set_property IOSTANDARD {{ port['IO Standard'] | default("LVCMOS33")}} {{ get_ports }}
{% endif %}
{% if port['DIR'] != 'IN' %}
set_property OFFCHIP_TERM NONE {{ get_ports }}
{% endif %}

{% endfor %}

# Differential signals

{% for port in spec.all_signals_differential %}
{% set get_ports = "[get_ports " ~ port.name_io ~ "_p]"  %}
set_property PACKAGE_PIN {{ port['FPGA Pin'].ljust(7) }} {{ get_ports }}
{% if port['IO Standard'] != '' %}
set_property IOSTANDARD {{ port['IO Standard'] }} {{ get_ports }}
{% endif %}
{% if port['DIR'] == 'IN' %}
set_property DIFF_TERM TRUE {{ get_ports }}
{% else %}
set_property OFFCHIP_TERM NONE {{ get_ports }}
{% endif %}

{% endfor %}


# Vivado port interfaces

{% for bundle in spec.bundles %}
create_interface if_{{ bundle.name }}
{% for port in bundle.signals if not port.Differential %}
{% set get_ports = "[get_ports " ~ port.name_io ~ "]"  %}
set_property interface if_{{ bundle.name }} {{ get_ports }}
{% endfor %}
{% for port in bundle.signals if port.Differential %}
{% set get_ports = "[get_ports io_" ~ port.name_io ~ "_p]"  %}
set_property interface if_{{ bundle.name }} {{ get_ports }}
{% endfor %}
{% endfor %}

