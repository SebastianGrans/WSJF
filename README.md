# WATS Standard Json UUT Report Generator

This is a library for generating WATS UUT reports, and it also comes with a `pytest` plugin that
generates and upload the report to WATS.

**Note:** This is a very young project and is not a complete implementation.

Contributions are much appreciated!

## About this project

This project came about because the "unofficial" Python library that Virinco [provides](https://github.com/Virinco/Python-WATS-API/) is pretty old and clunky. And it doesn't even
implement the standard in the correct way.

The initial framework for this project was created using the
[`datamodel-code-generator`](https://docs.pydantic.dev/latest/integrations/datamodel_code_generator/)
python library.

Virinco provides a JSON Schema that you can access at:
<https://your-wats-server.com/WSJFReport.schema.json>

```bash
datamodel-codegen --input WSJFReport.schema.json \ 
    --input-file-type jsonschema \
    --output wsjf.py \
    --output-model-type pydantic_v2.BaseModel
```

## Usage as pytest plugin

You can clone this repo and run this command.

* Replace the `base-url` argument with your WATS domain.
* Set the `purpose` argument to something that won't polute your production data
* Set the `process-code` argument to something reasonable. We use `10` as the `SW Debug` process
  code.
* Set an environment variable named `WATS_REST_API_TOKEN` to contain your API token.

```bash
pytest --base-url "https://<your-domain>.wats.com" \  
    --check-max-tb=0 \
    --name SomeTestName \
    --part-number somePartNumber \
    --serial-number 1234 \
    --revision x \
    --process-code 10 \
    --machine-name hostname \
    --purpose development \
    --operator-name someone \
    --location somewhere
```

All the tests in `tests/` will run, and upload a report to WATS using the REST API.

**Note:** The tests will fail to demonstrate how that is portrayed in the WATS report.

## Standalone usage

Check out `examples/basic_example.py`

## Virinco documentation on the format

<https://support.virinco.com/hc/en-us/articles/360015705199-WATS-Standard-JSON-Format-WSJF>
