# Package 120 / Real Host Sensor Ingress And Raw Artifact Store v0

Status: Implemented
Runtime Impact: Bounded foreground local sensor capture only

Package 120 adds read-only local ingress adapters for camera, screen, microphone, and restricted host-state sources. Each capture requires an explicit state directory and an explicit capture command. Sensor modules do not open devices on import, ordinary test discovery does not start capture, and real capture commands require `--confirm-local-capture`.

## Capability

The package can acquire bounded adapter-output samples and preserve them as immutable `SensorRawArtifact` records:

- camera: OpenCV-delivered BGR8 frame bytes
- screen: MSS or Windows GDI-delivered BGRA8 pixel bytes
- microphone: sounddevice or Windows WinMM PCM signed little-endian chunks
- host_state: canonical UTF-8 JSON bytes containing only the restricted v0 host-state fields

Every artifact records byte length, SHA-256, a relative content-addressed blob path, capture metadata, and a canonical `TraceEnvelope` with `source_line = host_sensor_ingress` and `trace_layer = raw_sensor_trace`.

## Store

Artifacts are written under:

```text
<state_dir>/host_sensor_artifacts_v0/
  sensor_artifacts.sqlite3
  blobs/sha256/<prefix>/<sha256>.bin
  quarantine/
  store_backups/
```

The runtime writes a temporary file, flushes and fsyncs it, validates SHA-256 and byte length, then atomically renames it into the content-addressed blob path. Artifact rows and trace rows are append-only through the public runtime API. The store has no delete or update API for artifacts or traces.

## Boundaries

Package 120 does not create `HostBodyEvent`, `PerceptionReadableData`, perception primitives, `LearningFeedbackCandidate`, teacher review records, memory records, working readback, candidate scoring changes, external control, first_output, a scheduler, or open-ended capture.

TraceEnvelope payloads contain metadata only. They do not include raw camera pixels, screen pixels, microphone PCM bytes, base64 artifact content, or duplicated host-state blob bytes.

## Lifecycle

The runtime supports one active sensor source per foreground capture session:

```text
created -> started -> running -> paused -> resumed -> running -> stopping -> stopped
```

Hard duration, artifact-count, and byte-budget stops append lifecycle events, close the adapter, and preserve committed artifacts. Crash recovery reports temporary files, orphan blobs, missing blobs, hash mismatch, byte-length mismatch, and running sessions recovered as `recovered_aborted`.

## Safe Claim

ASHL Core v1 can manually and temporarily open selected local camera, screen, microphone, and restricted host-state sources in read-only mode, preserve bounded adapter-output samples as immutable content-addressed raw artifacts, verify their SHA-256 identity, and align their metadata to the canonical TraceEnvelope timeline.

The captured pixels, PCM samples, and host-state bytes remain raw perception input material. They are not interpreted, compiled into perception primitives, sent into learning, written to memory, or used for action.
