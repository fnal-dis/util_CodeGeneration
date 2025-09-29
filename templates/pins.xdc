# Single-ended signals

{% for idx, port in single_ended_ports.iterrows() %}
{% set get_ports = "[get_ports io_" ~ port["Net Name"] ~ "]"  %}
set_property PACKAGE_PIN {{ port['FPGA Pin'].ljust(7) }} {{ get_ports }}
{% if port['IO Standard'] != '' %}
set_property IOSTANDARD {{ port['IO Standard'] }} {{ get_ports }}
{% endif %}

{% endfor %}

# Differential signals

{% for idx, port in diff_ports.iterrows() %}
{% set get_ports = "[get_ports io_" ~ port["Net Name"] ~ "_p]"  %}
set_property PACKAGE_PIN {{ port['FPGA Pin'].ljust(7) }} {{ get_ports }}
{% if port['IO Standard'] != '' %}
set_property IOSTANDARD {{ port['IO Standard'] }} {{ get_ports }}
{% endif %}
{% if port['DIR'] == 'IN' %}
set_property DIFF_TERM TRUE {{ get_ports }}
{% endif %}

{% endfor %}


# Vivado port interfaces

{% for bundle_name in ports["Bundle Name"].unique() %}
create_interface if_{{ bundle_name }}
{% for idx, port in single_ended_ports[single_ended_ports["Bundle Name"]==bundle_name].iterrows() %}
{% set get_ports = "[get_ports io_" ~ port["Net Name"] ~ "]"  %}
set_property interface if_{{ bundle_name }} {{ get_ports }}
{% endfor %}
{% for idx, port in diff_ports[diff_ports["Bundle Name"]==bundle_name].iterrows() %}
{% set get_ports = "[get_ports io_" ~ port["Net Name"] ~ "_p]"  %}
set_property interface if_{{ bundle_name }} {{ get_ports }}
{% endfor %}
{% endfor %}

