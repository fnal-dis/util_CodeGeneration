  type t_axis is record
    tvalid : std_logic;
    tready : std_logic;
    tdata : std_logic_vector;
  end record t_axis;

  {% set tname = "t_axis_"~protocol.name.lower() %}
  {% set tarrname = "t_arr_axis_"~protocol.name.lower() %}

  subtype {{ tname }} is t_axis(tdata({{module_output.tdata}}-1 downto 0));
  type {{ tarrname }} is array(natural range <>) of {{ tname }};
