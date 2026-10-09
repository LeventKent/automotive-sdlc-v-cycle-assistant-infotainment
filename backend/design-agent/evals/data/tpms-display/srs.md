# Software Requirements Specification (SRS) - Tire Pressure Monitoring Display

Version: 2.1
Platform: Android Automotive OS (AAOS) 14, Kotlin, center display

## 1. Functional Requirements
| ID | Requirement | ASIL | Priority |
|---|---|---|---|
| FR-100 | The application shall subscribe to the TPMS status signals defined in ICD-TPMS-01 through the vehicle signal service. | A | Must |
| FR-110 | The application shall display a low pressure warning card identifying the affected wheel(s) within 500 ms of receiving TpmsWarnSts = LOW_PRESSURE for that wheel. | A | Must |
| FR-120 | The application shall display a sensor fault indication ("--") for any wheel whose TpmsSensorSts is FAULT or whose signal is not received for more than 3 seconds (signal timeout). | A | Must |
| FR-130 | The application shall never display a stale or invalid pressure as a valid value. Values with an alive counter that has not changed for 3 consecutive messages shall be treated as invalid. | A | Must |
| FR-140 | The application shall show per-wheel pressure and temperature, plus the recommended cold pressure for the selected load setting, on the Tires screen when the gear is P. | QM | Must |
| FR-150 | The application shall convert pressure units according to the vehicle unit setting (kPa, bar, psi). | QM | Must |
| FR-160 | The warning card may be minimized but shall reappear on each ignition cycle while TpmsWarnSts = LOW_PRESSURE persists. | A | Must |

## 2. Non-Functional Requirements
| ID | Requirement | Target |
|---|---|---|
| NFR-100 | Warning latency | 500 ms from signal reception to visible warning card (p99). |
| NFR-110 | Startup | Warning path active within 2 seconds of the center display becoming available. |
| NFR-120 | Freedom from interference | QM components (Tires screen, unit conversion) shall not be able to delay or suppress the ASIL A warning path. |
| NFR-130 | Diagnostics | Every warning display and every signal timeout shall be logged with a monotonic timestamp. |
| NFR-140 | Driver distraction | The warning card shall contain no more than 1 action (minimize). |

## 3. Safety Requirements
- SR-1 (ASIL A): The warning path (signal reception, plausibility check, warning card rendering) shall be developed according to ISO 26262 ASIL A.
- SR-2 (ASIL A): Signal plausibility shall use the CRC and alive counter defined in ICD-TPMS-01.
- SR-3 (ASIL A): Loss of the TPMS signal for more than 3 seconds shall be indicated as a sensor fault, not as normal pressure.

## 4. Out of Scope
- The instrument cluster tell-tale (owned by cluster software).
- TPMS ECU firmware and sensor learning.
