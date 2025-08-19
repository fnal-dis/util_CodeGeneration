#!/usr/bin/env python3

import yaml
import sys
import os
import jinja2

from pathlib import Path

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

scr_dir = Path(__file__).parent.resolve()
template_dir = scr_dir / "templates"
project_template_dir = scr_dir / "../templates"

if __name__ == '__main__':

    # Load project information
    project_yaml = yaml.safe_load(Path("project.yaml").read_text())
    validate_yaml(project_yaml)
    project_name, project = next(iter(project_yaml.items()))

    data = get_spec_data(
        filename=project['spec'],
        ports_sheet=project['ports_sheet'])

    env = jinja2.Environment(
        loader=jinja2.ChoiceLoader([
                jinja2.FileSystemLoader(str(template_dir)),
                jinja2.FileSystemLoader(str(project_template_dir))
            ]),
        trim_blocks=True)

    templates = {}
    # Get all default templates to render
    for path in template_dir.iterdir():

        if not path.is_file():
            continue
        if path.suffix in [".jinja", ".j2"]:
            print(path + " skipped")
            continue

        print(path.name)
        template = env.get_template(path.name)
        print(f"Found template {template.name}")

        ext = path.suffix.lstrip(".")
        folder = Path("src") / map_extension(ext) / "_AUTOGEN"
        folder.mkdir(parents=True, exist_ok=True)

        new_filename = path.stem + f"_{project_name}." + ext
        new_path = folder / new_filename

        print(f"Generating template {new_filename} in {folder}")

        templates[template.name] = (template, new_path)

    # Get all project specific templates (terminated in .j2)
    # Templates matching those in the common core will be overwritten
    for path in project_template_dir.iterdir():

        if not path.is_file():
            continue
        if path.suffix not in [".jinja", ".j2"]:
            continue
        if len(path.suffixes) < 2:
            continue

        print(path.name)
        template = env.get_template(path.name)
        print(f"Found project-specific template {template.name}")

        ext = path.suffixes[0].lstrip(".")
        folder = Path("src") / map_extension(ext) / "_AUTOGEN"
        folder.mkdir(parents=True, exist_ok=True)

        new_filename = path.with_suffix('').stem + f"_{project_name}." + ext
        new_path = folder / new_filename

        print(f"Generating template {new_filename} in {folder}")

        templates[template.name] = (template, new_path)


    for template, new_path in templates.values():
        new_path.write_text(
            template.render(
                file_name=new_filename,
                project_name_short=project_name,
                **project['metadata'],
                **data
            )
        )
