{% for idx, port in single_ended_ports.iterrows() %}
{% set get_ports = "[get_ports io_" ~ port["Net Name"] ~ "]"  %}
set_property PACKAGE_PIN {{ port['FPGA Pin'].ljust(7) }} {{ get_ports }}
set_property IOSTANDARD {{ port['IO Standard'] | default('LVCMOS33') }} {{ get_ports }}

{% endfor %}

{% for idx, port in diff_ports.iterrows() %}
{% set get_ports = "[get_ports io_" ~ port["Net Name"] ~ "_p]"  %}
set_property PACKAGE_PIN {{ port['FPGA Pin'].ljust(7) }} {{ get_ports }}
set_property IOSTANDARD {{ port['IO Standard'] }} {{ get_ports }}
{% if port['DIR'] == 'IN' %}
set_property DIFF_TERM TRUE {{ get_ports }}
{% endif %}

{% endfor %}
