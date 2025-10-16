{% extends "bits/header.vhd" %}

{% block content %}
library ieee;
use ieee.std_logic_1164.all;

package {{ spec.project.package_name }} is

  -- <Base Types>
  subtype {{ spec.project.basetype_name }} is std_logic;

  -- <Records>
{% for bundle in spec.bundles %}
  type {{ bundle.record_typename }} is record
{% for signal in bundle.signals %}
{{ signal.name_record.ljust(59).rjust(63) }} : {{ spec.project.basetype_name }};
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
