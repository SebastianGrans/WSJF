# WATS Standard Json UUT Report Generator - With pytest plugin

This is a library for generating WATS reports, and it also comes with a `pytest` plugin that
generates and uploads a WATS report.

## Virinco documentation on the format

<https://support.virinco.com/hc/en-us/articles/360015705199-WATS-Standard-JSON-Format-WSJF>

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

## Status

* ✅ SequenceCall
* ✅ NumericLimit
* ✅ StringValue
  * Note: Only the equal and not equal comparison works.
  * The documentation say that other should work, but it doesn't.
* ✅ PassFail
* ✅ Attachment
* ✅ Chart
* ❌ CallExe
* ❌ MessagePopup
* ❌ Action
