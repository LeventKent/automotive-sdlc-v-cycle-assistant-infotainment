# Interface Control Document ICD-TPMS-01 - TPMS ECU to Infotainment

Version: 1.3

## 1. Transport
- Bus: CAN FD, chassis domain, routed to the infotainment head unit through the central gateway.
- Frame: TPMS_Status_01, ID 0x3A4, cycle time 1000 ms, plus an event-triggered frame on any warning state change.
- Protection: CRC8 (SAE J1850 polynomial) in byte 0, 4-bit alive counter in byte 1 (low nibble).

## 2. Signals (per wheel: FL, FR, RL, RR)
| Signal | Type | Range / Values | Resolution |
|---|---|---|---|
| TpmsPress_xx | uint8 | 0 - 637.5 kPa | 2.5 kPa |
| TpmsTemp_xx | int8 | -40 - 125 degC | 1 degC |
| TpmsWarnSts_xx | enum | NO_WARNING, LOW_PRESSURE, RAPID_LOSS | - |
| TpmsSensorSts_xx | enum | OK, FAULT, NOT_LEARNED | - |

## 3. Timing
- Signal timeout: 3000 ms without a valid frame (3 missed cycles).
- An event-triggered frame is sent within 100 ms of a warning state change.
