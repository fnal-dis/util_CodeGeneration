{% extends "bits/header.vhd" %}

{% block content %}
library ieee;
use ieee.std_logic_1164.all;

package pkg_{{ project_name }} is

  -- <Base Types>
  subtype t_{{ project_name_short }}_BaseType is std_logic;

  -- <Records>
{# Write out all signals according to their bundle #}
{% for bundle_name in ports["Bundle Name"].unique() %}
  type t_rec_{{ project_name_short }}_{{ bundle_name }} is record
{% for idx, port in single_ended_ports[single_ended_ports["Bundle Name"]==bundle_name].iterrows() %}
{% set sig_name=port['Net Name']~"_"~port['DIR'].lower() %}
{{ sig_name.ljust(30).rjust(34) }}: t_{{ project_name_short }}_BaseType; -- {{ port['Comment'] }}
{% endfor %}
{% for idx, port in diff_ports[diff_ports["Bundle Name"]==bundle_name].iterrows() %}
{% set sig_name=port['Net Name']~"_"~port['DIR'].lower() %}
{{ sig_name.ljust(30).rjust(34) }}: t_{{ project_name_short }}_BaseType; -- {{ port['Comment'] }}
{% endfor %}
  end record;

{% endfor %}

  -- <Supertype>
  type t_{{ project_name_short }} is record
{% for bundle_name in ports["Bundle Name"].unique() %}
    if_{{ bundle_name.ljust(16) }} : t_rec_{{ project_name_short }}_{{ bundle_name }};
{% endfor %}
  end record;

end package pkg_{{ project_name }};

{% endblock %}
