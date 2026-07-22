# Taurus and JMeter gap analysis

Status: 2026-07-22. This compares the public `Blazemeter/bzm-mcp` source at commit `b5b6b32573c9125af05f5bc09754150c95277cb1` with native Taurus/JMeter workflows. It is an implementation inventory, not a claim about every capability in the BlazeMeter web UI.

## What the official MCP already covers

The official `blazemeter_tests` tool can create a BlazeMeter test with a Taurus/JMeter default configuration, upload `.jmx`, `.yaml`, `.zip`, `.csv`, and related assets, select a supported executor, set basic load (`iterations`, `concurrency`, `hold-for`, `ramp-up`, `steps`), distribute locations, and replace BlazeMeter failure-criteria rules. It can also start a saved test and retrieve execution/report data.

That is useful for a **pre-authored test artifact**: create a container, upload the script and dependencies, tune cloud load, and run it.

## Gap matrix

| Area | Native Taurus/JMeter workflow | Official MCP status | Needed MCP capability |
| --- | --- | --- | --- |
| Taurus authoring | Create and edit YAML scenarios, executions, variables, includes, and file references | Not exposed; the MCP uploads a finished YAML/JMX file | `taurus_validate`, `taurus_render`, and a structured scenario/execution editor |
| Taurus modules and services | Configure `modules`, `services`, reporters, provisioning, consolidator, and custom executor settings | Not exposed | Schema-aware module/service configuration, with safe allowlists |
| Local Taurus lifecycle | Run `bzt`, capture console output/artifacts, stop/retry, and inspect exit code | Not exposed; all execution is a saved BlazeMeter test | Local-run tool with explicit workspace root and artifact collection |
| Taurus conversion/debugging | Convert/inspect generated JMeter plans and diagnose YAML/schema errors | Not exposed | YAML parsing, dry-run validation, generated-JMX inspection, and actionable error formatting |
| JMeter plan editing | Build or patch the JMX element tree: thread groups, samplers, controllers, timers, assertions, extractors, config elements, listeners | Not exposed; `.jmx` is opaque uploaded content | Typed JMX-plan read/patch tools with XML-safe round-tripping |
| JMeter dependencies | Discover/install/manage plugins, custom JARs, JDBC drivers, and `user.properties`/`jmeter.properties` | Upload only; no dependency-resolution or compatibility check | Dependency manifest, compatibility scan, and preflight validation |
| JMeter local/CI execution | Non-GUI CLI execution, `.jtl` generation, HTML dashboard, JVM/heap tuning, exit-code handling | Not exposed | Bounded CLI/CI runner and result-artifact tools |
| JMeter distributed execution | Controller/server topology, remote hosts, RMI/SSL properties, server logs, engine-specific diagnostics | Not exposed | Explicit remote-engine configuration and diagnostic retrieval; never a generic shell tool |
| Test data and secrets | CSV data modeling, variable scopes, credential/secret injection, masking and rotation | Asset upload exists, but no data/secret modeling or validation | Test-data bindings and secret references that never expose plaintext |
| Recording and API-test composition | Generate scenarios from recorded traffic or compose request chains with headers, bodies, assertions, and extractors | Not exposed as structured authoring | Recorder import and typed HTTP-scenario CRUD |
| Service Virtualization for Taurus/JMeter | Validate Taurus dependencies, create/update/deploy/start/stop virtual services, services, transactions, templates, and mappings | Not registered in the official source inspected | Separate `blazemeter_virtual_services` tool group using `mock.blazemeter.com`, with confirmation for mutations |
| API Monitoring | Buckets, API tests, schedules, environments, integrations, agents, run history and alerts | Not registered in the official source inspected | Separate `blazemeter_api_monitoring` tool group using `api.runscope.com` |

## Important separation of API surfaces

The small Swagger document at `a.blazemeter.com/api/v4/explorer/swagger.json` is not the right contract for these gaps. BlazeMeter documents different hosts:

- Performance/functional APIs: `https://a.blazemeter.com/api/v4/`
- Service Virtualization: `https://mock.blazemeter.com`
- API Monitoring (Runscope): `https://api.runscope.com`
- Virtual-service analytics: `https://analytics.blazemeter.com/reports/api/v1/`

The companion Explorer MCP therefore cannot gain Taurus/JMeter, service-virtualization, or monitoring coverage merely by refreshing its current Swagger snapshot.

## Recommended implementation order

1. **Read-only discovery first:** list/read virtual services, templates, transactions, monitor buckets/tests, and API-monitor runs.
2. **Taurus/JMeter preflight:** validate scripts/assets/dependencies before an upload or run; return exact missing-file/plugin/property errors.
3. **Structured authoring:** YAML/JMX inspection and minimal safe edits, not free-form XML or shell execution.
4. **Explicit lifecycle mutations:** create/update/deploy/start/stop virtual services and create/update/run monitors, each with `confirm=true`.
5. **Local execution only if needed:** constrain `bzt`/JMeter to a caller-selected workspace and return collected artifacts; do not expose arbitrary command execution.

## Source notes

- [Official BlazeMeter MCP source](https://github.com/Blazemeter/bzm-mcp): `tools/test_manager.py` is the basis for the supported-test row above.
- [BlazeMeter API overview](https://help.blazemeter.com/docs/guide/api-blazemeter-api-overview.html): documents the distinct API hosts.
- [Service Virtualization API introduction](https://help.blazemeter.com/apidocs/service-virtualization/index.htm): describes automating virtual-service and transaction creation.
- [Validate Taurus configuration dependencies](https://help.blazemeter.com/apidocs/service-virtualization/validate.htm): documents the service-mock validation operation.
- [BlazeMeter's URL/API performance-test guide](https://help.blazemeter.com/docs/guide/performance-create-url-api-test.html): documents Taurus YAML that executes JMeter.
- [Apache JMeter distributed-testing guide](https://jmeter.apache.org/usermanual/remote-test.html): describes the native distributed-testing model.
