#!/usr/bin/env python3

import yaml
import os
import jinja2

from read_spreadsheet import get_spec_data

def validate_yaml(yaml_dict):
    if len(yaml_dict.keys()) > 1:
        raise Exception("Only 1 project allowed in a YAML")

hdl_extensions = ["vhd", "v", "sv"]
constraints_extensions = ["xdc", "qsf"]
def map_extension(ext):
    if ext in hdl_extensions:
        return "hdl"
    if ext in constraints_extensions:
        return "constraints"

    raise Exception(f"Found file extension {ext} not mapped to an output folder")

template_dir = "./templates"
if __name__ == '__main__':

    # Load project information
    with open("project.yaml", 'r') as f:
        project_yaml = yaml.safe_load(f)
        validate_yaml(project_yaml)
        project_name, project = next(iter(project_yaml.items()))

    data = get_spec_data(project['spec'])

    env = jinja2.Environment(loader=jinja2.FileSystemLoader("."),
                            trim_blocks=True)

    for filename in os.listdir(template_dir):

        if "jinja" in filename or "j2" in filename or "bits" in filename:
            continue

        template = env.get_template(f"{template_dir}/{filename}")
        folder = f"src/{map_extension(filename.split('.')[-1])}/_AUTOGEN"
        os.makedirs(folder, exist_ok=True)

        new_filename = filename.replace(".", f"_{project_name}.")
        print(f"Generating template {new_filename} in {folder}")

        with open(f"{folder}/{new_filename}", 'w') as f:
            f.write(
                template.render(
                    file_name=new_filename,
                    project_name_short=project_name,
                    **project['metadata'],
                    **data
                )
            )
