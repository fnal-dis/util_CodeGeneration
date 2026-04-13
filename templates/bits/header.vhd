{% block header %}
-------------------------------------------------------------------------------
--
--        _-    -_
--       |  |  |  |            Fermi National Accelerator Laboratory
--       |  |  |  |
--       |  |  |  |        Operated by Fermi Forward Discovery Group, LLC
--       |  |  |  |        for the Department of Energy under contract
--       /  |  |   \                    89243024CSC000002
--      /   /   \   \
--     /   /     \   \
--     ----       ----
-------------------------------------------------------------------------------
-- Title        : {% block title %} The Title {% endblock +%}
-- Project      : {{ spec.project.project }}
-------------------------------------------------------------------------------
-- File         : {{ file_name }}
-- Author       : {{ spec.project.author }}
-- Division     : {{ spec.project.division }}
-- Created      : {{ spec.project.date_created }}
-- Last updated : {{ date_updated }}
-- Standard     : {{ spec.project.vhdl_standard }}
-------------------------------------------------------------------------------
-- Description:
{% block description %}
{% endblock %}
-------------------------------------------------------------------------------
-- {{ spec.project.copyright }}
-------------------------------------------------------------------------------
-- Revisions  :
-- Date        Version  Author  Description
{% for rev in revisions %}
-- {{ rev.date }}   {{ rev.version }}   {{ rev.author }}  {{ rev.description }}
{% endfor %}
-------------------------------------------------------------------------------
{% endblock %}

{% block content %} {% endblock %}
