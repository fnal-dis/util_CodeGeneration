#!/usr/bin/env python3

import argparse
import jinja2

from pathlib import Path

from SignalModel import Project, SignalSpecification
from Loaders import ExcelLoader

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

    parser = argparse.ArgumentParser(description="Generate HDL and constraints files.")
    parser.add_argument(
        "-c",
        "--config",
        default="../project.yaml",
        help="Path to configuration file."
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="src",
        help="Directory where generated files will be saved."
    )
    args = parser.parse_args()

    project = Project(scr_dir / args.config)
    spec = SignalSpecification(project)
    loader = ExcelLoader(project.spec)
    loader.load(spec, project.get_sheets())

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
        folder = Path(args.output_dir) / map_extension(ext) / "_AUTOGEN"
        folder.mkdir(parents=True, exist_ok=True)

        new_filename = path.stem + f"_{project.name}." + ext
        new_path = folder / new_filename

        print(f"Generating template {new_filename} in {folder}")

        templates[template.name] = (template, new_path, new_filename)

    # Get all project specific templates (terminated in .j2)
    # Templates matching those in the common core will be overwritten
    if project_template_dir.exists():
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
            folder = Path(args.output_dir) / map_extension(ext) / "_AUTOGEN"
            folder.mkdir(parents=True, exist_ok=True)

            new_filename = path.with_suffix('').stem + f"_{project.name}." + ext
            new_path = folder / new_filename

            print(f"Generating template {new_filename} in {folder}")

            templates[template.name] = (template, new_path, new_filename)


    for template, new_path, new_filename in templates.values():
        new_path.write_text(
            template.render(
                spec=spec,
                file_name=new_filename,
                spec_DigitalBus=spec.digital_bus
            )
        )
