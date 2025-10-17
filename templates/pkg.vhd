{% extends "bits/header.vhd" %}

{% block content %}
library ieee;
use ieee.std_logic_1164.all;

package {{ spec.project.package_name }} is

  -- <Base Types>
  subtype t_{{ spec.project.basetype_name }} is std_logic;
  subtype t_arr_{{ spec.project.basetype_name }} is std_logic_vector;

  -- <Records>
{% for bundle in spec.bundles %}
  type {{ bundle.record_typename }} is record
{% for signal in bundle.signals %}
{% if not signal.is_array %}
{{ signal.name_record.ljust(59).rjust(63) }} : t_{{ spec.project.basetype_name }};
{% else %}
{{ signal.name_record.ljust(59).rjust(63) }} : t_arr_{{ spec.project.basetype_name }}(signal.last-1 downto 0);
{% endif %}
{% endfor %}
  end record;

{% endfor %}

  -- <Supertype>
  type {{ spec.project.supertype_name }} is record
{% for bundle in spec.bundles %}
    {{ bundle.interface_name.ljust(19) }} : {{ bundle.record_typename }};
{% endfor %}
  end record;

end package pkg_{{ spec.project.name }};

{% endblock %}
